"""
Temporary lib support for objects.
These are just like the lib, except
that they aren't persistent after an
object is destroyed.
"""

def makeTempLib(obj):
    if hasattr(obj, "naked"):
        obj = obj.naked()
    if not hasattr(obj, "_boosterTempLib"):
        obj._boosterTempLib = {}
    return obj

def getTempLibValue(obj, key, fallback):
    obj = makeTempLib(obj)
    return obj._boosterTempLib.get(key, fallback)

def setTempLibValue(obj, key, value):
    obj = makeTempLib(obj)
    obj._boosterTempLib[key] = value

def delTempLibValue(obj, key):
    obj = makeTempLib(obj)
    if key in obj.boosterTempLib:
        del obj._boosterTempLib[key]
