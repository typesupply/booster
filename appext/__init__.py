from appext import menubar
from appext import defaults

"""
This needs to handle wrapping/unwrapping fonts with FontParts subclasses.
We won't be able to make defcon subclasses anymore, so we'll have to get
by with FontParts.
"""

class ExtensionManager(object):

    def __init__(self, owner, userDefaults={}, menu=None):
        # self.owner = owner
        # self.ownerStub = owner + "."
        # # defaults
        # userDefaults = {}
        # for key, value in userDefaults.items():
        #     userDefaults[self.ownerStub + key] = value
        # defaults.registerDefaults(userDefaults)
        # # menu
        # if self._menu is not None:
        #     menubar.buildMenu(self.owner, title, items)

    def terminate(self):
        """
        - opposite of initiate
        """
        menubar.teardownMenu(self.owner)

    # --------
    # Defaults
    # --------

    def getDefault(self, key, fallback=None):
        key = self.ownerStub + key
        return defaults.getDefault(key, fallback=fallback)

    def setDefault(self, key, value):
        key = self.ownerStub + key
        defaults.setDefault(key, value)

    # -------------
    # Notifications
    # -------------

    def addObserver(self, observer=None, selector=None, notification=None, observable=None):
        pass

    def removeObserver(self, observer=None, notification=None, observable=None):
        pass

    # -------
    # Menubar
    # -------

    def getItemData(self, identifier):
        return menubar.getItemData(identifier)

    def setItemData(self, identifier, **kwargs):
        menubar.setItemData(identifier, kwargs)

    # -------
    # Objects
    # -------

    def wrapFont(self, font):
        pass

    def getAllFonts(self):
        pass

    def getCurrentFont(self):
        pass

    def setCurrentFont(self, font):
        pass

    def getCurrentGlyph(self):
        pass

    def setCurrentGlyph(self, glyph):
        pass



class Test(object):

    def __init__(self):