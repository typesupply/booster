"""
-----------------
BoosterController
-----------------

This base class implements the basic functionality of and
implements a ton of functionality for extensions. To implement
it, do this:


    class MyExtensionController(BoosterController):

        fontWrapperClass = MyExtensionFont (optional)
        identifier = "com.me.myExtension"

This will give you a bunch of stuff to work with. See below.

Always try to get font objects through your controller.
The reason is that the objects will always be wrapped in
your font wrapper (and any other object wrappers). Your
methods, properties and attributes will be there for you.

Thsi implements the basic notification behavior defined in
BoosterNotificationMixin. This posts the following notifications:

- fontDidOpen
- fontWillClose
- availableFontsChanged
"""

import weakref
from collections import OrderedDict
from defcon.tools.notifications import Notification
from mojo.roboFont import RFont, CurrentGlyph
from mojo.events import addObserver as addAppObserver
from mojo.events import removeObserver as removeAppObserver
from mojo import extensions
from .objects import BoosterFont
from .activity import SharedActivityPoller
from .manager import SharedFontManager
from .notifications import BoosterNotificationMixin
from .requests import SharedRequestCenter


class BoosterController(BoosterNotificationMixin):

    fontWrapperClass = BoosterFont
    identifier = None

    def __init__(self):
        """
        Subclasses should not implement this. Implement start instead.
        """
        self._fontObservervations = {}

    def start(self):
        """
        Start the extension.

        Subclasses may implement this, but the must call the super.
        """
        self._beginInternalObservations()

    def stop(self):
        """
        Stop the extension.

        Subclasses may implement this, but the must call the super.
        """
        self._stopInternalObservations()

    def _beginInternalObservations(self):
        manager = SharedFontManager()
        manager.addObserver(observer=self, selector="_fontManagerFontOpenedNotificationCallback", notification="bstr.fontDidOpen")
        manager.addObserver(observer=self, selector="_fontManagerFontClosedNotificationCallback", notification="bstr.fontWillClose")
        manager.addObserver(observer=self, selector="_fontManagerAvailableFontsChangedNotificationCallback", notification="bstr.availableFontsChanged")

    def _stopInternalObservations(self):
        manager = SharedFontManager()
        manager.removeObserver(observer=self, notification="bstr.fontDidOpen")
        manager.removeObserver(observer=self, notification="bstr.fontWillClose")
        manager.removeObserver(observer=self, notification="bstr.availableFontsChanged")

    # --------
    # Requests
    # --------

    """
    Convenience for SharedRequestCenter.
    """

    def addResponder(self, responder, selector, request):
        SharedRequestCenter().addResponder(responder, selector, request)

    def removeResponder(self, request):
        SharedRequestCenter().removeResponder(request)

    def postRequest(self, request, *args, **kwargs):
        SharedRequestCenter().removeResponder(request, *args, **kwargs)

    # --------
    # Defaults
    # --------

    """
    Defaults will be handled by mojo.extensions default functions.
    They will be stored with the provided key appended to the
    string defined in self.identifier.
    """

    def _makeDefaultKey(self, key):
        return self.identifier + "." + key

    def registerDefaults(self, defaults):
        """
        Convenience for mojo.extensions.registerExtensionDefaults.
        """
        d = {}
        for k, v in defaults.items():
            k = self._makeDefaultKey(k)
            d[k] = v
        extensions.registerExtensionDefaults(d)

    def getDefault(self, key, fallback=None):
        """
        Convenience for mojo.extensions.getExtensionDefault.
        """
        key = self._makeDefaultKey(key)
        return extensions.getExtensionDefault(key, fallback=fallback)

    def getDefaultColor(self, fallback=None):
        """
        Convenience for mojo.extensions.getExtensionDefaultColor.
        """
        key = self._makeDefaultKey(key)
        return extensions.getExtensionDefaultColor(key, fallback=fallback)

    def setDefault(self, key, value):
        """
        Convenience for mojo.extensions.setExtensionDefault.
        """
        key = self._makeDefaultKey(key)
        extensions.setExtensionDefault(key, value)

    def setDefaultColor(self, key, value):
        """
        Convenience for mojo.extensions.setExtensionDefaultColor.
        """
        key = self._makeDefaultKey(key)
        extensions.setExtensionDefaultColor(key, value)

    # ---
    # App
    # ---

    def addAppObserver(self, observer, selector, notification):
        """
        Convenience for mojo.events.addObserver.
        """
        addAppObserver(observer, selector, notification)

    def removeAppObserver(self, observer, notification):
        """
        Convenience for mojo.events.removeObserver.
        """
        removeAppObserver(observer, notification)

    # ------------
    # Font Manager
    # ------------

    def _fontManagerFontOpenedNotificationCallback(self, notification):
        name = notification.name
        font = notification.data["font"]
        font = self._rewrapFont(font)
        self.postNotification(name, dict(font=font))

    def _fontManagerFontClosedNotificationCallback(self, notification):
        name = notification.name
        font = notification.data["font"]
        font = self._rewrapFont(font)
        self.postNotification(name, dict(font=font))

    def _fontManagerAvailableFontsChangedNotificationCallback(self, notification):
        name = notification.name
        self.getAllFonts()
        self.postNotification(name, dict(fonts=self.getAllFonts()))

    # --------
    # Activity
    # --------

    """
    Convenience for SharedActivityPoller.
    """

    def addActivityObserver(self,
            observer, selector,
            appIsActive=None,
            sinceUserActivity=2.0,
            sinceFontActivity=2.0,
            repeat=False
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
        SharedActivityPoller().removeObserver_(info)

    # -----
    # Fonts
    # -----

    """
    Convenience for SharedFontManager.
    """

    def _unwrapFont(self, font):
        if hasattr(font, "naked"):
            font = font.naked()
        return font

    def _rewrapFont(self, native):
        if not hasattr(native, "naked"):
            naked = native
            native = RFont(naked)
        else:
            naked = native.naked()
        wrapped = self.fontWrapperClass(naked, showInterface=native.hasInterface(), document=native.document())
        return wrapped

    def getAllFonts(self):
        """
        Get all fonts from the SharedFontManager wrapped with
        the font class defined as self.fontWrapperClass.
        """
        fonts = SharedFontManager().getAllFonts()
        fonts = [self._rewrapFont(native) for native in fonts]
        for font in fonts:
            if font.uniqueName is None:
                font.makeUniqueName(fonts)
        return fonts

    def getCurrentFont(self):
        """
        Get the current font from the SharedFontManager wrapped with
        the font class defined as self.fontWrapperClass.
        """
        native = SharedFontManager().getCurrentFont()
        if native is None:
            return None
        return self._rewrapFont(native)

    def getCurrentGlyph(self):
        """
        Get the current glyph from the SharedFontManager wrapped as a
        glyph from the font class defined as self.fontWrapperClass.
        """
        glyph = CurrentGlyph()
        if glyph is None:
            return None
        layer = glyph.layer
        layerName = layer.name
        font = self._rewrapFont(glyph.font)
        layer = font.getLayer(layerName)
        glyph = layer[glyph.name]
        return glyph

    def openFont(self, path, showInterface=True):
        """
        Open a font wrapped with the font class defined as self.fontWrapperClass.
        """
        font = self.fontWrapperClass(path, showInterface=showInterface)
        return font

    def openFonts(self, paths, showInterface=True):
        """
        Open fonts wrapped with the font class defined as self.fontWrapperClass.
        """
        fonts = [self.openFont(path, showInterface=showInterface) for path in paths]
        return fonts

    # observation

    def _fontNotificationCallback(self, notification):
        notificationName = notification.name
        nakedFont = notification.object
        notificationData = notification.data
        nakedFontRef = weakref.ref(nakedFont)
        wrappedFont = self._rewrapFont(nakedFont)
        wrappedFontRef = weakref.ref(wrappedFont)
        notification = Notification(
            name=notificationName,
            objRef=wrappedFontRef,
            data=notificationData
        )
        if nakedFontRef in self._fontObservervations:
            if notificationName in self._fontObservervations[nakedFontRef]:
                for observerRef, selector in self._fontObservervations[nakedFontRef][notificationName].items():
                    observer = observerRef()
                    if observer is not None:
                        meth = getattr(observer, selector)
                        meth(notification)

    def hasFontObserver(self, font, observer, notification):
        """
        Boolean if the font is being observed.
        """
        nakedFont = self._unwrapFont(font)
        nakedFontRef = weakref.ref(nakedFont)
        observerRef = weakref.ref(observer)
        if nakedFontRef in self._fontObservervations:
            if notification in self._fontObservervations[nakedFontRef]:
                if notification in self._fontObservervations[nakedFontRef]:
                    if observerRef in self._fontObservervations[nakedFontRef][notification]:
                        return True
        return False

    def addFontObserver(self, font, observer, selector, notification):
        """
        Observe a font. The method called for the notification
        will recieve a font object wrapped with self.fontWrapperClass.
        """
        naked = self._unwrapFont(font)
        if not naked.hasObserver(self, notification):
            font.addObserver(self, "_fontNotificationCallback", notification)
        fontRef = weakref.ref(naked)
        observerRef = weakref.ref(observer)
        if fontRef not in self._fontObservervations:
            self._fontObservervations[fontRef] = {}
        if notification not in self._fontObservervations[fontRef]:
            self._fontObservervations[fontRef][notification] = OrderedDict()
        assert observerRef not in self._fontObservervations[fontRef][notification], "Observer %r is already registered for %r." % (observer, notification)
        self._fontObservervations[fontRef][notification][observerRef] = selector

    def removeFontObserver(self, font, observer, notification):
        """
        Stop observing a font.
        """
        naked = self._unwrapFont(font)
        fontRef = weakref.ref(naked)
        observerRef = weakref.ref(observer)
        del self._fontObservervations[fontRef][notification][observerRef]
        if not self._fontObservervations[fontRef][notification]:
            del self._fontObservervations[fontRef][notification]
            naked.removeObserver(self, notification)
        if not self._fontObservervations[fontRef]:
            del self._fontObservervations[fontRef]
