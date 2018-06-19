import weakref
from booster.menubar import SharedMenubar
from booster.defaults import SharedUserDefaults
from booster.notifications import SharedNotificationCenter
from booster.requests import SharedRequestCenter
from booster.activity import SharedActivityPoller
from booster.font import *


class AppExtController(object):

    owner = None
    fontWrapperClass = None
    documentClass = None

    def __init__(self):
        self._documents = []

    def teardown(self):
        self.menubar.teardownMenu(self.owner)

    # --------
    # Defaults
    # --------

    def _get_userDefaults(self):
        return SharedUserDefaults()

    userDefaults = property(_get_userDefaults)

    def registerUserDefaults(self, userDefaults):
        self.userDefaults.registerDefaults(self.owner, userDefaults)

    def getUserDefault(self, key, fallback=None):
        return self.userDefaults.getDefault(self.owner, key, fallback=fallback)

    def setUserDefault(self, key, value):
        self.userDefaults.setDefault(self.owner, key, value)

    # -------
    # Menubar
    # -------

    def _get_menubar(self):
        return SharedMenubar()

    menubar = property(_get_menubar)

    def buildMenu(self, title, items, image=None):
        self.menubar.buildMenu(self.owner, title, items, image=image)

    def getMenuItemData(self, identifier):
        return self.menubar.getItemData(identifier)

    def setMenuItemData(self, identifier, **kwargs):
        self.menubar.setItemData(identifier, kwargs)

    # -------------
    # Notifications
    # -------------

    def addObserver(self, observer=None, selector=None, notification=None, observable=None):
        relay = SharedNotificationCenter()
        relay.addObserver_selector_notification_observable_(
            observer,
            selector, 
            notification,
            observable
        )

    def removeObserver(self, observer=None, notification=None, observable=None):
        relay = SharedNotificationCenter()
        relay.removeObserver_notification_observable_(
            observer,
            notification,
            observable
        )

    def postNotification(self, notification=None, observable=None, data=None):
        relay = SharedNotificationCenter()
        relay.postNotification_observable_userInfo_(
            notification,
            observable,
            data
        )

    # --------
    # Requests
    # --------

    def addResponder(self, responder, selector, request, domain=None):
        SharedRequestCenter().addResponder(responder, selector, request, domain)

    def removeResponder(self, request, domain=None):
        SharedRequestCenter().removeResponder(request, domain)

    def postRequest(self, request, domain=None, *args, **kwargs):
        SharedRequestCenter().removeResponder(request, domain, *args, **kwargs)

    # --------
    # Activity
    # --------

    def addActivityObserver(self,
            observer, selector,
            appIsActive=None, # None, True, False
            sinceUserActivity=2.0, # None, number
            sinceFontActivity=2.0, # None, number
            repeat=False # True, False
        ):
        info = dict(
            observer=observer,
            selector=selector,
            appIsActive=appIsActive,
            sinceUserActivity=sinceUserActivity,
            sinceFontActivity=sinceFontActivity,
            repeat=repeat
        )
        SharedActivityPoller().addObserver_(info)

    def removeActivityObserver(self, observer, selector):
        info = dict(
            observer=observer,
            selector=selector
        )
        SharedActivityPoller().addObserver_(info)

    # -------
    # Objects
    # -------

    def _rewrapFont(self, native):
        naked = native.naked()
        wrapped = self.fontWrapperClass(naked)
        return wrapped

    def getAllFonts(self):
        return [self._rewrapFont(native) for native in AllFonts()]

    def openFont(self, path, showInterface=True):
        native = OpenFont(path, showInterface=showInterface)
        return self._rewrapFont(native)

    def getCurrentFont(self):
        native = CurrentFont()
        if native is None:
            return None
        return self._rewrapFont(native)

    # ---------
    # Documents
    # ---------

    def newDocument(self, *args, **kwargs):
        kwargs["documentController"] = self
        document = self.documentClass(*args, **kwargs)
        self._documents.append(document)
        return document

    def closeDocument(self, document):
        document.postNotification(
            notification="MM5.Document.Close"
        )
        self._documents.remove(document)


class AppExtDocument(object):

    def __init__(self, *args, **kwargs):
        self.documentController = kwargs["documentController"]

    # -------------------
    # Document Controller
    # -------------------

    _documentController = None

    def _get_documentController(self):
        if self._documentController is None:
            return None
        return self._documentController()

    def _set_documentController(self, controller):
        self._documentController = weakref.ref(controller)

    documentController = property(_get_documentController, _set_documentController)

    # -------------
    # Notifications
    # -------------

    def addObserver(self, observer=None, selector=None, notification=None):
        self.documentController.addObserver(
            observer=observer,
            selector=selector,
            notification=notification,
            observable=self
        )

    def removeObserver(self, observer=None, notification=None):
        self.documentController.removeObserver(
            observer=observer,
            notification=notification,
            observable=self
        )

    def postNotification(self, notification=None, data=None):
        self.documentController.postNotification(
            notification=notification,
            observable=self,
            data=data
        )

    # --------
    # Requests
    # --------

    def addResponder(self, responder, selector, request):
        self.documentController.addResponder(responder, selector, request, domain=self)

    def removeResponder(self, request):
        self.documentController.removeResponder(request, domain=self)

    def postRequest(self, request, *args, **kwargs):
        self.documentController.removeResponder(request, domain=self, *args, **kwargs)
