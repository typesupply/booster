from mojo.events import addObserver as addAppObserver
from mojo.events import removeObserver as removeAppObserver
from booster.notifications import BoosterNotificationMixin


class BoosterFontManager(BoosterNotificationMixin):

    def __init__(self):
        self._noInterface = set()
        addAppObserver(self, "_fontDidOpenNotificationCallback", "fontDidOpen")
        addAppObserver(self, "_newFontDidOpenNotificationCallback", "newFontDidOpen")
        addAppObserver(self, "_fontWillCloseNotificationCallback", "fontWillClose")
        addAppObserver(self, "_fontDidCloseNotificationCallback", "fontDidClose")

    def _removeFromNoInterface(self, font):
        naked = font.naked()
        for other in self._noInterface:
            if other.naked() == naked:
                self._noInterface.remove(other)
                break
            if font.path is not None and other.path == font.path:
                self._noInterface.remove(other)
                break

    def fontDidOpen(self, font):
        if not font.hasInterface():
            self._noInterface.add(font)
        else:
            self._removeFromNoInterface(font)
        self.postNotification("bstr.fontDidOpen", data=dict(font=font))
        self.postNotification("bstr.availableFontsChanged", data=dict(fonts=self.getAllFonts()))

    def fontWillClose(self, font):
        if not font.hasInterface():
            self._removeFromNoInterface(font)
        self.postNotification("bstr.fontWillClose", data=dict(font=font))

    def fontDidClose(self):
        self.postNotification("bstr.fontDidClose")
        self.postNotification("bstr.availableFontsChanged", data=dict(fonts=self.getAllFonts()))

    def getAllFonts(self):
        from mojo.roboFont import AllFonts #, FontList
        fonts = AllFonts() + list(self._noInterface)
        # fonts = FontList(fonts)
        return fonts

    def getCurrentFont(self):
        from mojo.roboFont import CurrentFont
        return CurrentFont()

    # -------------
    # Notifications
    # -------------

    def _fontDidOpenNotificationCallback(self, info):
        font = info["font"]
        self.fontDidOpen(font)

    def _newFontDidOpenNotificationCallback(self, info):
        font = info["font"]
        self.fontDidOpen(font)

    def _fontWillCloseNotificationCallback(self, info):
        font = info["font"]
        self.fontWillClose(font)

    def _fontDidCloseNotificationCallback(self, info):
        self.fontDidClose()

# ----
# Main
# ----

_fontManager = BoosterFontManager()

def SharedFontManager():
    return _fontManager
