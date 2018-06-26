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
        self._rewrapFont(font)
        self.postNotification(name, dict(font=font))

    def _fontManagerFontClosedNotificationCallback(self, notification):
        name = notification.name
        font = notification.data["font"]
        self._rewrapFont(font)
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

    # -------
    # Objects
    # -------

    def _rewrapFont(self, native):
        naked = native.naked()
        wrapped = self.fontWrapperClass(naked, showInterface=native.hasInterface())
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

    def openFont(self, path, showInterface=True):
        font = self.fontWrapperClass(path, showInterface=showInterface)
        return font

    def openFonts(self, paths, showInterface=True):
        fonts = [self.openFont(path, showInterface=showInterface) for path in paths]
        return fonts

