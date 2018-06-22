"""
This needs to be observable.

- font opened
- font closed
- new font opened
- available fonts changed
"""

from mojo.events import addObserver as addAppObserver
from mojo.events import removeObserver as removeAppObserver

class BoosterFontManager(object):

    def __init__(self):
        self._noInterface = []
        addOppObserver(self, "_fontDidOpenNotificationCallback", "fontDidOpen")
        addOppObserver(self, "_newFontDidOpenNotificationCallback", "newFontDidOpen")
        addOppObserver(self, "_fontWillCloseNotificationCallback", "fontWillClose")

    # Notifications

    def _fontDidOpenNotificationCallback(self, info):
        font = info["font"]
        self.fontOpened(font)

    def _newFontDidOpenNotificationCallback(self, info):
        font = info["font"]
        self.fontOpened(font)

    def _fontWillCloseNotificationCallback(self, info):
        font = info["font"]
        self.fontClosed(font)

    def fontOpened(self, font):
        if not font.hasInterface() and font not in self._noInterface:
            self._noInterface.append(font)

    def fontClosed(self, font):
        if not font.hasInterface() and font in self._noInterface:
            self._noInterface.remove(font)

    def getAllFonts(self):
        from mojo.roboFont import AllFonts, FontList
        fonts = AllFonts() + self._noInterface
        fonts = FontList(fonts)
        return fonts

    def getCurrentFont(self):
        from mojo.roboFont import CurrentFont
        return CurrentFont()


# ----
# Main
# ----

_fontManager = BoosterFontManager()

def SharedFontManager():
    return _fontManager
