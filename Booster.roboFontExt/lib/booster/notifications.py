from defcon.tools.notifications import NotificationCenter

class BoosterNotificationMixin(object):

    def addObserver(self, observer, selector, notification):
        dispatcher = SharedNotificationCenter()
        dispatcher.addObserver(
            observer=observer,
            methodName=selector,
            notification=notification,
            observable=self
        )

    def removeObserver(self, observer, notification):
        dispatcher = SharedNotificationCenter()
        dispatcher.removeObserver(
            observer=observer,
            observable=self,
            notification=notification
        )

    def postNotification(self, notification, data=None):
    	dispatcher = SharedNotificationCenter()
    	dispatcher.postNotification(notification=notification, observable=self, data=data)


# ----
# Main
# ----

_dispatcher = NotificationCenter()

def SharedNotificationCenter():
    return _dispatcher