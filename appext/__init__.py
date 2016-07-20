from appext import menubar
from appext import defaults

class ExtensionManager(object):

    def __init__(self, owner):
        self.owner = owner
        self.ownerStub = owner + "."

    def __del__(self):
        """
        - menu tear down
        - notification observer release
        """

    # --------
    # Defaults
    # --------

    def registerDefaults(self, data):
        completed = {}
        for key, value in data.items():
            completed[self.ownerStub + key] = value
        defaults.registerDefaults(completed)

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

    def buildMenu(self, title, items):
        menubar.buildMenu(self.owner, title, items)

    def teardownMenu(self, title=None):
        menubar.teardownMenu(self.owner, title=title)

    def getItemData(self, identifier):
        return menubar.getItemData(identifier)

    def setItemData(self, identifier, **kwargs):
        menubar.setItemData(identifier, kwargs)

    # -------
    # Objects
    # -------

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

