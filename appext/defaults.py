"""
User defaults abstraction.

The available functions are:

registerDefaults({"something" : "foo"})
value = getDefault("something")
setDefault("foo", NSColor.redColor())
"""

from Foundation import NSData, NSMutableDictionary, NSDictionary, NSArchiver, NSUnarchiver
from AppKit import NSColor
from appext.bundle import inRoboFont

__all__ = [
    "registerDefaults",
    "getDefault",
    "setDefault"
]

if inRoboFont:
    from mojo import extensions as mojoExtensions
else:
    _defaults = {}


def registerDefaults(data):
    data = _normalizeIncomingData(data)
    if inRoboFont:
        mojoExtensions.registerExtensionDefaults(data)
    else:
        _defaults.update(data)

def getDefault(key, fallback=None):
    if inRoboFont:
        value = mojoExtensions.getExtensionDefault(key, fallback=fallback)
    else:
        if key in _defaults:
            value = _defaults[key]
        else:
            value = fallback
    value = _normalizeOutgoingData(value)
    return value

def setDefault(key, value):
    value = _normalizeIncomingData(value)
    if inRoboFont:
        mojoExtensions.setExtensionDefault(key, value)
    else:
        _defaults[key] = value

# --------------
# Internal Tools
# --------------

def _normalizeIncomingData(data):
    normalized = data
    if isinstance(data, (dict, NSDictionary)):
        normalized = NSMutableDictionary.alloc().init()
        for key, value in data.items():
            normalized[key] = _normalizeIncomingData(value)
    elif isinstance(data, NSColor):
        normalized = NSArchiver.archivedDataWithRootObject_(data)
    return normalized

def _normalizeOutgoingData(data):
    normalized = data
    if isinstance(data, (dict, NSDictionary)):
        normalized = {}
        for key, value in data.items():
            normalized[key] = _normalizeOutgoingData(value)
    else:
        if isinstance(data, NSData):
            normalized = NSUnarchiver.unarchiveObjectWithData_(data)
    return normalized
