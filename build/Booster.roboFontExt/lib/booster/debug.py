"""
-----
Debug
-----

This implements Just's clever class name incrementer
to deal with the limitations of the Obj-C namespace.
"""

# XXX
# This needs a heuristic to make sure that this is off
# when necessary. Or, maybe there is an external way to
# turn it off. booster.debug.setState(False) or something.

debug = True

ClassNameIncrementer = None

if debug:
    def ClassNameIncrementer(clsName, bases, dct):
        import objc
        orgName = clsName
        counter = 0
        while 1:
            try:
                objc.lookUpClass(clsName)
            except objc.nosuchclass_error:
                break
            counter += 1
            clsName = orgName + repr(counter)
        return type(clsName, bases, dct)


import time


"""
Some very basic debug support.
"""

def logMessage(message):
    print(time.strftime("%H:%M:%S"), message)