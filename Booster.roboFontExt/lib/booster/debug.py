debug = True


# --------------------------
# obj-c namespace workaround
# --------------------------

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

