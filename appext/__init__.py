from appext.menubar import SharedMenubar
from appext.defaults import SharedUserDefaults
from appext import environment
from appext.font import *


class ExtensionManager(object):

    def __init__(self, owner, userDefaults=None, menu=None, fontWrapper=None):
        self._menubar = SharedMenubar()
        self._userDefaults = SharedUserDefaults()
        self.owner = owner
        if userDefaults is not None:
            self._userDefaults.registerDefaults(owner, userDefaults)
        if menu is not None:
            title = menu["title"]
            items = menu["items"]
            self._menubar.buildMenu(owner, title, items)
        if fontWrapper is None:
            self._fontWrapper = AppExtFont

    def teardown(self):
        self._menubar.teardownMenu(self.owner)

    # --------
    # Defaults
    # --------

    def getUserDefault(self, key, fallback=None):
        self._userDefaults.getDefault(self.owner, key, fallback=fallback)

    def setUserDefault(self, key, value):
        self._userDefaults.setDefault(self.owner, key, value)

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

    def getMenuItemData(self, identifier):
        return self._menubar.getItemData(identifier)

    def setMenuItemData(self, identifier, **kwargs):
        self._menubar.setItemData(identifier, kwargs)

    # -------
    # Objects
    # -------

    def wrapFont(self, font):
        pass

    def getAllFonts(self):
        pass

    def openFont(self, path, showInterface=True):
        pass

    def getCurrentFont(self):
        pass
