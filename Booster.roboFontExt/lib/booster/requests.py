import weakref

class BoosterRequestCenter(object):

    def __init__(self):
        self.responders = {}

    def addResponder(self, responder, selector, request):
        responder = weakref.ref(responder)
        self.responders[request] = (responder, selector)

    def removeResponder(self, request):
        del self.responders[request]

    def postRequest(self, request, *args, **kwargs):
        if request in self.responders:
            responder, selector = self.responders[request]
            responder = responder()
            selector = getattr(responder, selector)
            value = selector(*args, **kwargs)
        else:
            value = None
        return value


# -------------
# Shared Object
# -------------

_center = None

def SharedRequestCenter():
    global _center
    if _center is None:
        _center = BoosterRequestCenter()
    return _center