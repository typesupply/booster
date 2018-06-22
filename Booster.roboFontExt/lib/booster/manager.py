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
        self._noInterface = set()
        addOppObserver(self, "_fontDidOpenNotificationCallback", "fontDidOpen")
        addOppObserver(self, "_newFontDidOpenNotificationCallback", "newFontDidOpen")
        addOppObserver(self, "_fontWillCloseNotificationCallback", "fontWillClose")

    def fontOpened(self, font):
        if not font.hasInterface():
            self._noInterface.add(font)

    def fontClosed(self, font):
        if not font.hasInterface() and font in self._noInterface:
            self._noInterface.remove(font)

    def getAllFonts(self):
        from mojo.roboFont import AllFonts, FontList
        fonts = AllFonts() + list(self._noInterface)
        fonts = FontList(fonts)
        return fonts

    def getCurrentFont(self):
        from mojo.roboFont import CurrentFont
        return CurrentFont()

    # -------------
    # Notifications
    # -------------

    def addObserver(self, observer, selector, notification):
        pass

    def removeObserver(self, observer, selector, notification):
        pass

    def _fontDidOpenNotificationCallback(self, info):
        font = info["font"]
        self.fontOpened(font)

    def _newFontDidOpenNotificationCallback(self, info):
        font = info["font"]
        self.fontOpened(font)

    def _fontWillCloseNotificationCallback(self, info):
        font = info["font"]
        self.fontClosed(font)




# ----
# Main
# ----

_fontManager = BoosterFontManager()

def SharedFontManager():
    return _fontManager
