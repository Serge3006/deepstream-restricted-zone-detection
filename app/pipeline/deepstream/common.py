from typing import Any

import gi
gi.require_version("Gst", "1.0")
import ctypes
import platform


from gi.repository import Gst
from loguru import logger

def is_aarch64() -> bool:
    """
    Check if the current platform is aarch64
    Returns: bool: True if the current platform is aarch64, False otherwise
    """
    return platform.uname()[4] == "aarch64"

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        logger.info("End-of-stream")
        loop.quit()
    elif t == Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        logger.warning(f"{err}: {debug}")
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        logger.error(f"{err}: {debug}")
    return True