"""
-----------------
SharedFontManager
-----------------

This function will return the font manager used across all
Booster based extensions. The difference between this and
the fontParts specified AllFonts() function is that this
manager also keeps track of fonts that do not have an
interface. So, asking this manager for all fonts will
give you fonts with and without an interface.

The manager allows subscribing to the following notifications:

- bstr.availableFontsChanged
- bstr.fontDidOpen
- bstr.fontWillClose
- bstr.fontDidClose
"""

from mojo.events import addObserver as addAppObserver
from mojo.events import removeObserver as removeAppObserver
from booster.notifications import BoosterNotificationMixin


class BoosterFontManager(BoosterNotificationMixin):

    def __init__(self):
        self._noInterface = set()
        self._fontChangingVisibility = None
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

    def fontWillChangeVisibility(self, font):
        """
        This is needed because turning visibility off
        causes RF to send out notifications that the
        font has been closed. These notifications
        are indistinguishable for the notifications
        sent by other "real" document close actions.
        So, this makes a note to not pay attention
        to the incoming notifications.
        """
        self._fontChangingVisibility = font

    def fontDidChangeVisibility(self, font):
        """
        Notification relay. Don't use this externally.
        """
        if font in self._noInterface:
            self._noInterface.remove(font)
        else:
            self._noInterface.add(font)
        self._fontChangingVisibility = None

    def fontDidOpen(self, font):
        """
        Notification relay. Don't use this externally.
        """
        if self._fontChangingVisibility == font:
            return
        if not font.hasInterface():
            self._noInterface.add(font)
        else:
            self._removeFromNoInterface(font)
        self.postNotification("bstr.fontDidOpen", data=dict(font=font))
        self.postNotification("bstr.availableFontsChanged", data=dict(fonts=self.getAllFonts()))

    def fontWillClose(self, font):
        """
        Notification relay. Don't use this externally.
        """
        if self._fontChangingVisibility == font:
            return
        if not font.hasInterface():
            self._removeFromNoInterface(font)
        self.postNotification("bstr.fontWillClose", data=dict(font=font))

    def fontDidClose(self):
        """
        Notification relay. Don't use this externally.
        """
        if self._fontChangingVisibility is not None:
            return
        self.postNotification("bstr.fontDidClose")
        self.postNotification("bstr.availableFontsChanged", data=dict(fonts=self.getAllFonts()))

    def getAllFonts(self):
        """
        Get all fonts.
        """
        from mojo.roboFont import AllFonts #, FontList
        fonts = AllFonts()# + list(self._noInterface)
        # fonts = FontList(fonts)
        return fonts

    def getCurrentFont(self):
        """
        Get the current font.
        """
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
