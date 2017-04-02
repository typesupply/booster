"""
The application's shared user defaults.

SharedUserDefaults.registerDefaults({"something" : "foo"})
value = SharedUserDefaults.getDefault("something")
SharedUserDefaults.setDefault("foo", NSColor.redColor())
"""

from Foundation import *
from AppKit import *
from booster import environment
if environment.inRoboFont:
    from mojo import extensions as mojoExtensions


class _DefaultsManager(object):

    def registerDefaults(self, owner, data):
        if owner is not None:
            owner = _makeOwnerStub(owner)
            d = {}
            for k, v in data.items():
                k = _makeOwnerKey(owner, k)
                d[k] = v
            data = d
        data = _normalizeIncomingData(data)
        if environment.inRoboFont:
            mojoExtensions.registerExtensionDefaults(data)
        else:
            raise NotImplementedError

    def getDefault(self, owner, key, fallback=None):
        if owner is not None:
            owner = _makeOwnerStub(owner)
            key = _makeOwnerKey(owner, key)
        if environment.inRoboFont:
            value = mojoExtensions.getExtensionDefault(key, fallback=fallback)
        else:
            raise NotImplementedError
        value = _normalizeOutgoingData(value)
        return value

    def setDefault(self, owner, key, value):
        if owner is not None:
            owner = _makeOwnerStub(owner)
            key = _makeOwnerKey(owner, key)
        value = _normalizeIncomingData(value)
        if environment.inRoboFont:
            mojoExtensions.setExtensionDefault(key, value)
        else:
            raise NotImplementedError


def _makeOwnerStub(owner):
    if not owner.endswith("."):
        owner += "."
    return owner

def _makeOwnerKey(owner, key):
    if not key.startswith(owner):
        key = owner + key
    return key

# ----------------
# NS Normalization
# ----------------

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

# -------------
# Shared Object
# -------------

_manager = None

def SharedUserDefaults():
    global _manager
    if _manager is None:
        _manager = _DefaultsManager()
    return _manager
