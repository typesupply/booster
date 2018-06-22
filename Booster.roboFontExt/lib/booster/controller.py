from mojo.events import addObserver as addAppObserver
from mojo.events import removeObserver as removeAppObserver
from booster.objects import BoosterFont
from booster.activity import SharedActivityPoller
from booster.manager import SharedFontManager


class BoosterController(object):

    fontWrapperClass = BoosterFont

    def start(self):
        pass

    def stop(self):
        pass

    # ---
    # App
    # ---

    def addAppObserver(self, observer, selector, event):
        addAppObserver(observer, selector, event)

    def removeAppObserver(self, observer, event):
        removeAppObserver(observer, event)

    # ------------
    # Font Manager
    # ------------

    def addFontManagerObserver(self, observer, selector, event):
        pass

    def removeFontManagerObserver(self, observer, event):
        pass

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
        wrapped = self.fontWrapperClass(naked)
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

