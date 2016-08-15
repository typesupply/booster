"""
The application's shared request center.

SharedRequestCenter().addResponder(self, "answerSomething", "something", self.document)
value = SharedRequestCenter().postRequest("something", self.document)
SharedRequestCenter().removeResponder("something", self.document)
"""

import weakref

# ------
# Center
# ------

class _RequestCenter(object):

    def __init__(self):
        self.responders = {}

    def _packDomain(self, domain):
        try:
            ref = weakref.ref(domain)
            domain = ref
        except:
            pass
        return domain

    def addResponder(self, responder, selector, request, domain=None):
        responder = weakref.ref(responder)
        domain = self._packDomain(domain)
        key = request, domain
        assert key not in self.responders
        self.responders[key] = (responder, selector)

    def removeResponder(self, request, domain=None):
        domain = self._packDomain(domain)
        del self.responders[request, domain]

    def postRequest(self, request, domain=None, *args, **kwargs):
        domain = self._packDomain(domain)
        key = (request, domain)
        if key in self.responders:
            responder, selector = self.responders[request, domain]
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
        _center = _RequestCenter()
    return _center
