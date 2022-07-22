from gi.repository import Gst

def cb_newpad(decodebin, decoder_src_pad, data):
    caps = decoder_src_pad.get_current_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    source_bin = data
    features = caps.get_features(0)
    
    if gstname.find("video") != -1:
        if features.contains("memory:NVMM"):
            bin_ghost_pad = source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                raise RuntimeError("Failed to link decoder src pad with source bin ghost pad")
        else:
            raise RuntimeError("Error: Decodebin did not pick nvidia decoder plugin")

def decodebin_child_added(child_proxy, Object, name, user_data):
    if name.find("decodebin") != -1:
        Object.connect("child-added", decodebin_child_added, user_data)
        
    if "source" in name:
        Object.set_property("drop-on-latency", True)

def create_source_bin(index: int, uri: str) -> Gst.Bin:
    bin_name = f"source-bin-{index}"
    nbin = Gst.Bin.new(bin_name)
    if not bin:
        raise RuntimeError("Unable to create source bin")
    
    uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    if not uri_decode_bin:
        raise RuntimeError("Unable to create uri decode bin")
    
    uri_decode_bin.set_property("uri", uri)
    uri_decode_bin.connect("pad-added", cb_newpad, nbin)
    uri_decode_bin.connect("child-added", decodebin_child_added, nbin)
    
    Gst.Bin.add(nbin, uri_decode_bin)
    bin_pad = nbin.add_pad(Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    if not bin_pad:
        raise RuntimeError("Unable to add ghost pad in source bin")
    
    return nbin