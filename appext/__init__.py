from appext.menubar import SharedMenubar
from appext.defaults import SharedUserDefaults
from appext import environment

"""
This needs to handle wrapping/unwrapping fonts with FontParts subclasses.
We won't be able to make defcon subclasses anymore, so we'll have to get
by with FontParts.
"""

class ExtensionManager(object):

    def __init__(self, owner, userDefaults=None, menu=None):
        self._menubar = SharedMenubar()
        self._userDefaults = SharedUserDefaults()

        self.owner = owner
        if userDefaults is not None:
            self._userDefaults.registerDefaults(owner, userDefaults)
        if menu is not None:
            title = menu["title"]
            items = menu["items"]
            self._menubar.buildMenu(owner, title, items)

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


# ----
# Test
# ----

import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController

class Test(BaseWindowController):

    def __init__(self):
        self.extensionManager = ExtensionManager(
            owner="My Extension",
            userDefaults=dict(
                foo=1,
                bar=2
            ),
            menu = dict(
                title="My Extension",
                items=[
                    dict(
                        title="My Item"
                    ),
                    dict(
                        title="My Item with Key Command",
                        binding=("5", ["command", "option"])
                    )
                ]
            )
        )
        self.w = vanilla.Window((500, 500))
        self.w.open()
        self.setUpBaseWindowBehavior()

    def windowCloseCallback(self, sender):
        super(Test, self).windowCloseCallback(sender)
        self.extensionManager.teardown()

if __name__ == "__main__":
    if environment.inRoboFont:
        Test()
    else:
        from vanilla.test.testTools import executeVanillaTest
        executeVanillaTest(Test)
