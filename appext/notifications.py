"""
Cross-language notifications.
"""

from AppKit import *

# -----
# Relay
# -----

class _NotificationRelay(NSObject):

    def init(self):
        self = super(_NotificationRelay, self).init()
        self._objCCenter = NSNotificationCenter.defaultCenter()
        self._pythonObservingObjC = {}
        self._objCObservingPython = {}
        return self

    # Add

    def addObserver_selector_notification_observable_(self, observer, selector, notification, observable):
        meth = None
        if isinstance(observable, NSObject):
            if isinstance(observer, NSObject):
                meth = self.addObjcObserver_selector_notification_objcObservable_
            else:
                meth = self.addPythonObserver_selector_notification_objcObservable_
        else:
            if isinstance(observer, NSObject):
                meth = self.addObjcObserver_selector_notification_pythonObservable_
            else:
                meth = self.addPythonObserver_selector_notification_pythonObservable_
        meth(observer, selector, notification, observable)

    def addObjcObserver_selector_notification_objcObservable_(self, observer, selector, notification, observable):
        self._objCCenter.addObserver_selector_name_object_(
                observer,
                selector,
                notification,
                observable
            )

    def addPythonObserver_selector_notification_objcObservable_(self, observer, selector, notification, observable):
        key = (
            notification,
            observable
        )
        observer = weakref.ref(observer)
        if key not in self._pythonObservingObjC:
            self._pythonObservingObjC[key] = []
        self._pythonObservingObjC[key].append((observer, selector))
        self.addObserverOfObjC_selector_notification_observable_(
            self,
            "_pythonObservingObjCRelayCallback:",
            notification,
            observable
        )

    def addObjcObserver_selector_notification_pythonObservable_(self, observer, selector, notification, observable):
        raise NotImplementedError

    def addPythonObserver_selector_notification_pythonObservable_(self, observer, selector, notification, observable):
        raise NotImplementedError

    # Remove

    def removeObserver_notification_observable_(self, observer, notification, observable):
        meth = None
        if isinstance(observable, NSObject):
            if isinstance(observer, NSObject):
                meth = None
            else:
                meth = None
        else:
            if isinstance(observer, NSObject):
                meth = None
            else:
                meth = None
        meth(observer, notification, observable)

    def removeObjcObserver_notification_objcObservable_(self, observer, notification, observable):
        if observable is not None:
            self._objCCenter.removeObserver_name_object_(
                observer,
                notification,
                observable
            )
        else:
            self._objCCenter.removeObserver_(observer)

    def removePythonObserver_notification_objcObservable_(self, observer, notification, observable):
        if observable is not None:
            key = (
                notification,
                observable
            )
            if key in self._pythonObservingObjC:
                self._pythonObservingObjC[key] = [
                    i for i in self._pythonObservingObjC[key]
                    if i != observer
                ]
        else:
            for (notification, observable), observersAndSelectors in self._pythonObservingObjC.items():
                for otherObserver, selector in observersAndSelectors:
                    if observer == otherObserver:
                        print "<<<", observer, notification, observable
                        self.removeObserverOfObjC_notification_observable_(self, notification, observable)
        self.removeObserverOfObjC_notification_observable_(self, notification, observable)

    def removeObjcObserver_notification_pythonObservable_(self, observer, notification, observable):
        raise NotImplementedError

    def removePythonObserver_notification_pythonObservable_(self, observer, notification, observable):
        raise NotImplementedError

    # Post

    def postNotification_observable_userInfo_(self, notification, observable, userInfo):
        if isinstance(observable, NSObject):
            meth = self.postObjCNotification_observable_userInfo_
        else:
            meth = self.postPythonNotification_observable_userInfo_
        meth(notification, observable, userInfo)

    def postObjCNotification_observable_userInfo_(self, notification, observable, userInfo):
        notification = NSNotification.notificationWithName_object_userInfo_(
            notification,
            observable,
            userInfo
        )
        self._objCCenter.postNotification_(notification)

    def postPythonCNotification_observable_userInfo_(self, notification, observable, userInfo):
        raise NotImplementedError

    # Internal Routing

    def _pythonObservingObjCRelayCallback_(self, notification):
        key = (
            notification.name(),
            notification.object()
        )
        if key in self._pythonObservingObjC:
            for observer, selector in self._pythonObservingObjC[key]:
                observer = observer()
                method = getattr(observer, selector)
                method(notification)


# -------------
# Shared Object
# -------------

_relay = None

def SharedNotificationCenter():
    global _relay
    if _relay is None:
        _relay = _NotificationRelay()
    return _relay
