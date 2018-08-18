"""
-------------------
SharedRequestCenter
-------------------

This function will return the request ceneter that is shared
by all Booster based extensions. This allows extensions to
make requests of each other without needing to do imports
or know the extension internal API.

Requests are essentially the opposite of notifications.
In the notification model, observers are added to a hub and
wait patiently for the thing that they care about to happen.
Requests are impatient. The responders for specific actions
are added to a hub and they patiently wait to be called into
action. A requestor then sends a request to the hub and, if
a responder is registered to handle the request, the responder
will process the request and return the result to the requestor.

Here's an example responder:

    class Cafe(object):

        def makeSandwich(self, cheese, meat):
            # make a sandwich and return it

        def makeSalad(self, dressing):
            # make a salad and return it

    myCafe = Cafe()
    SharedRequestCenter().addResponder(myCafe, "makeSandwich", "Sandwich.Make")
    SharedRequestCenter().addResponder(myCafe, "makeSalad", "Salad.Make")

To send a request, you do this:

    sandwich = SharedRequestCenter().postRequest("Sandwich.Make", cheese=True, meat=False)
"""

import weakref
from booster.notifications import BoosterNotificationMixin

class BoosterRequestCenter(BoosterNotificationMixin):

    def __init__(self):
        self.responders = {}

    def addResponder(self, responder, selector, request):
        """
        Register a responder for a specific request.

        responder: an object.
        selector: a string defining the method name to be called.
        request: a string naming the request.
        """
        responder = weakref.ref(responder)
        self.responders[request] = (responder, selector)
        self.postNotification("BoosterRequestSenter.AddedResponder")

    def removeResponder(self, request):
        """
        Unregister a responder for a specific request.

        request: a string naming the request.
        """
        del self.responders[request]
        self.postNotification("BoosterRequestSenter.RemovedResponder")

    def postRequest(self, request, *args, **kwargs):
        """
        Post a request and get a response if a responder
        is registered for the request.

        request: a string naming the request.

        Any additional args or kwargs will be passed
        to the responder.
        """
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
