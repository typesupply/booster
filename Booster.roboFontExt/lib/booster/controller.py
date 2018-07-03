import weakref
from collections import OrderedDict
from defcon.tools.notifications import Notification
from mojo.roboFont import RFont, CurrentGlyph
from mojo.events import addObserver as addAppObserver
from mojo.events import removeObserver as removeAppObserver
from booster.objects import BoosterFont
from booster.activity import SharedActivityPoller
from booster.manager import SharedFontManager
from booster.notifications import BoosterNotificationMixin


class BoosterController(BoosterNotificationMixin):

    """
    Notifications:
    - fontDidOpen
    - fontWillClose
    - availableFontsChanged
    """

    fontWrapperClass = BoosterFont

    def __init__(self):
        self._fontObservervations = {}


    def start(self):
        self._beginInternalObservations()

    def stop(self):
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

    # ---
    # App
    # ---

    def addAppObserver(self, observer, selector, notification):
        addAppObserver(observer, selector, notification)

    def removeAppObserver(self, observer, notification):
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
        SharedActivityPoller().removeObserver_(info)

    # -----
    # Fonts
    # -----

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
        fonts = SharedFontManager().getAllFonts()
        fonts = [self._rewrapFont(native) for native in fonts]
        for font in fonts:
            if font.uniqueName is None:
                font.makeUniqueName(fonts)
        return fonts

    def getCurrentFont(self):
        native = SharedFontManager().getCurrentFont()
        if native is None:
            return None
        return self._rewrapFont(native)

    def getCurrentGlyph(self):
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
        font = self.fontWrapperClass(path, showInterface=showInterface)
        return font

    def openFonts(self, paths, showInterface=True):
        fonts = [self.openFont(path, showInterface=showInterface) for path in paths]
        return fonts

    def openInterface(self):
        super(BoosterFont, self).openInterface()
        manager = SharedFontManager()
        manager.fontChangedVisibility(self)

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
        naked = self._unwrapFont(font)
        fontRef = weakref.ref(naked)
        observerRef = weakref.ref(observer)
        del self._fontObservervations[fontRef][notification][observerRef]
        if not self._fontObservervations[fontRef][notification]:
            del self._fontObservervations[fontRef][notification]
            naked.removeObserver(self, notification)
        if not self._fontObservervations[fontRef]:
            del self._fontObservervations[fontRef]
