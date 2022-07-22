import gi

gi.require_version("Gst", "1.0")

import json
import math
from typing import Dict
import pyds
from gi.repository import GObject, Gst
from loguru import logger

from .deepstream import helpers as deepstream_helpers
from .deepstream.common import bus_call, is_aarch64

class Pipeline:
    def __init__(
        self,
        streams: Dict,
        tiled_output_height: int,
        tiled_output_width: int,
        model_config_path: str
    ) -> None:
        
        self._streams = streams
        self._tiled_output_height = tiled_output_height
        self._tiled_output_width = tiled_output_width
        self._model_config_path = model_config_path
        
        self._build()
        
        
    def _build(self) -> None:
        num_sources = len(self._streams)
        
        GObject.threads_init()
        Gst.init(None)
        
        # Creating deepstream elements
        logger.info("Creating pipeline")
        self._pipeline = Gst.Pipeline()
        is_live = False
        
        if not self._pipeline:
            raise RuntimeError("Unable to create a pipeline")
        
        logger.info("Creating streammux")
        streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
        if not streammux:
            raise RuntimeError("Unable to create NvStreamMux")
        
        self._pipeline.add(streammux)
        
        for i in range(num_sources):
            logger.info(f"Creating source_bin {i}")
            uri_name = self._streams[str(i)]["uri"]
            if uri_name.find("rtsp://") == 0 or uri_name.find("http://") == 0:
                is_live = True
                
            source_bin = deepstream_helpers.create_source_bin(i, uri_name)
            if not source_bin:
                raise RuntimeError("Unable to create source bin")
            
            self._pipeline.add(source_bin)
            
            sinkpad = streammux.get_request_pad(f"sink_{i}")
            if not sinkpad:
                raise RuntimeError("Unable to create sink pad bin")
            
            srcpad = source_bin.get_static_pad("src")
            if not srcpad:
                raise RuntimeError("Unable to create source pad bin")
            
            srcpad.link(sinkpad)
        
        logger.info("Creating pgie")
        pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
        if not pgie:
            raise RuntimeError("Unable to create pgie")
        
        logger.info("Creating nvvidconv1")
        nvvidconv1 = Gst.ElementFactory.make("nvvideoconvert", "convertor1")
        if not nvvidconv1:
            raise RuntimeError("Unable to create nvvideoconv1")
        
        logger.info("Creating filter1")
        caps1 = Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA")
        filter1 = Gst.ElementFactory.make("capsfilter", "filter1")
        if not filter1:
            raise RuntimeError("Unable to create the caps filter")
        
        filter1.set_property("caps", caps1)
        
        logger.info("Creating tiler")
        tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
        if not tiler:
            raise RuntimeError("Unable to create tiler")
        
        logger.info("Creating nvvidconv")
        nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
        if not nvvidconv:
            raise RuntimeError("Unable to create nvvidconvert")
        
        logger.info("Creating nvosd")
        nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
        if not nvosd:
            raise RuntimeError("Unable to create nvosd")
        
        if is_aarch64():
            logger.info("Creating transform")
            transform = Gst.ElementFactory.make("nvegltransform", "nvegl-transform")
            if not transform:
                raise RuntimeError("Unable to create transform")
            
        logger.info("Creating output sink")
        sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
        if not sink:
            raise RuntimeError("Unable to create output sink")
        
        if is_live:
            logger.info("At least one of the sources is live")
            streammux.set_property("live-source", 1)
            
        logger.info("Setting elements properties")
        streammux.set_property("width", 1920)
        streammux.set_property("height", 1080)
        streammux.set_property("batch_size", num_sources)
        streammux.set_property("batched-push-timeout", 40000)
        
        pgie.set_property("config-file-path", self._model_config_path)
        pgie_batch_size = pgie.get_property("batch_size")
        if pgie_batch_size != num_sources:
            logger.info(
                f"WARNING: Overriding infer-config batch size {pgie_batch_size} with "
                f"number of sources {num_sources}"
            )
            pgie.set_property("batch_size", num_sources)
        
        tiler_rows = int(math.sqrt(num_sources))
        tiler_columns = int(math.ceil(1.0 * num_sources / tiler_rows))
        tiler.set_property("rows", tiler_rows)
        tiler.set_property("columns", tiler_columns)
        tiler.set_property("width", self._tiled_output_width)
        tiler.set_property("height", self._tiled_output_height)
        
        sink.set_property("sync", 0)
        sink.set_property("qos", 0)
        
        logger.info("Adding elements to Pipeline")
        self._pipeline.add(pgie)
        self._pipeline.add(nvvidconv1)
        self._pipeline.add(nvvidconv)
        self._pipeline.add(filter1)
        self._pipeline.add(nvosd)
        self._pipeline.add(tiler)
        if is_aarch64():
            self._pipeline.add(transform)
        self._pipeline.add(sink)
        
        logger.info("Linkink elements in the pipeline")
        streammux.link(pgie)
        pgie.link(nvvidconv1)
        nvvidconv1.link(filter1)
        filter1.link(tiler)
        tiler.link(nvvidconv)
        nvvidconv.link(nvosd)
        
        if is_aarch64():
            nvosd.link(transform)
            transform.link(sink)
            
        else:
            nvosd.link(sink)
            
        # Create an event loop and feed gstreamer bus messages to it
        self._loop = GObject.MainLoop()
        bus = self._pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", bus_call, self._loop)
        
        
    def _clean(self) -> None:
        logger.info("Cleaning up pipeline")
        pyds.unset_callback_funcs()
        self._pipeline.set_state(Gst.State.NULL)
        
    def run(self) -> None:
        """Run pipeline"""
        logger.info("Running pipeline")
        self._pipeline.set_state(Gst.State.PLAYING)
        
        try:
            self._loop.run()
        except Exception as e:
            self._clean()
            raise e
        
        self._clean()