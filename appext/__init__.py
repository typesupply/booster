from appext.menubar import SharedMenubar
from appext.defaults import SharedUserDefaults
from appext import environment
from appext.font import *


class ExtensionManager(object):

    def __init__(self, owner, userDefaults=None, menu=None, fontWrapper=None):
        self.menubar = SharedMenubar()
        self.userDefaults = SharedUserDefaults()
        self.owner = owner
        if userDefaults is not None:
            self.userDefaults.registerDefaults(owner, userDefaults)
        if menu is not None:
            title = menu["title"]
            items = menu["items"]
            self.menubar.buildMenu(owner, title, items)
        if fontWrapper is None:
            self.fontWrapper = AppExtFont

    def teardown(self):
        self.menubar.teardownMenu(self.owner)

    # --------
    # Defaults
    # --------

    def getUserDefault(self, key, fallback=None):
        self.userDefaults.getDefault(self.owner, key, fallback=fallback)

    def setUserDefault(self, key, value):
        self.userDefaults.setDefault(self.owner, key, value)

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
        return self.menubar.getItemData(identifier)

    def setMenuItemData(self, identifier, **kwargs):
        self.menubar.setItemData(identifier, kwargs)

    # -------
    # Objects
    # -------

    def _rewrapFont(self, native):
        naked = native.naked()
        wrapped = self.fontWrapper(naked)
        return wrapped

    def getAllFonts(self):
        return [self._rewrapFont(native) for native in AllFonts()]

    def openFont(self, path, showInterface=True):
        native = OpenFont(path, showInterface=showInterface)
        return self._rewrapFont(native)

    def getCurrentFont(self):
        native = CurrentFont()
        if native is None:
            return None
        return self._rewrapFont(native)
