from AppKit import *
from vanilla.vanillaBase import VanillaCallbackWrapper

"""
Main menu abstraction.

The available functions are:

buildMenu("MyExtension.Go", "Go", items)
teardownMenu("MyExtension.Go")
data = getItemData("MyExtension.Go.something")
setItemData("MyExtension.Go.something", {"state" : "mixed"})

Item format:

    {
        "identifier" : string (None)
        "separator" : bool (False)
        "title" : string
        "state" : "on | off | mixed"
        "binding" : vanilla style key binding (None)
        "target" : NSObject (None)
        "action" : string defining NSObject method name (None)
        "callback" : vanilla style callback
        "submenu" : [ items ]
    }
"""

__all__ = [
    "buildMenu",
    "teardownMenu",
    "getItemData",
    "setItemData"
]

# ------------
# External API
# ------------

def buildMenu(owner, title, items):
    if _manager is None:
        return
    _manager.buildMenu(owner, title, items)

def teardownMenu(owner, title=None):
    if _manager is None:
        return
    _manager.teardownMenu(owner, title=title)

def getItemData(identifier):
    return _manager.getItemData(identifier)

def setItemData(identifier, **kwargs):
    _manager.setItemData(identifier, kwargs)

# -------
# Manager
# -------

_modifierMap = {
    "command": NSCommandKeyMask,
    "control": NSAlternateKeyMask,
    "option": NSAlternateKeyMask,
    "shift": NSShiftKeyMask,
    "capslock": NSAlphaShiftKeyMask,
}

_keyMap = {
    "help": NSHelpFunctionKey,
    "home": NSHomeFunctionKey,
    "end": NSEndFunctionKey,
    "pageup": NSPageUpFunctionKey,
    "pagedown": NSPageDownFunctionKey,
    "forwarddelete": NSDeleteFunctionKey,
    "leftarrow": NSLeftArrowFunctionKey,
    "rightarrow": NSRightArrowFunctionKey,
    "uparrow": NSUpArrowFunctionKey,
    "downarrow": NSDownArrowFunctionKey,
}

_stateMap = {
    "off" : 0,
    "on" : 1,
    "mixed" : -1
}

class _MenuManager(object):

    def __init__(self, mainMenu):
        self._mainMenu = mainMenu
        self._ownerToMenu = {}
        self._idToCallbackWrapper = {}
        self._ownerToIds = {}
        self._idToItem = {}

    # ------------
    # Construction
    # ------------

    def buildMenu(self, owner, title, items):
        baseItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, None, "")
        self._mainMenu.insertItem_atIndex_(baseItem, self._mainMenu.numberOfItems() - 1)
        baseMenu = NSMenu.alloc().initWithTitle_(title)
        baseItem.setSubmenu_(baseMenu)
        identifiers = self._buildTree(baseMenu, items)
        self._ownerToMenu[owner, title] = baseItem
        self._ownerToIds[owner, title] = identifiers

    def _buildTree(self, parent, submenu):
        identifiers = set()
        for data in submenu:
            if data.get("separator", False):
                item = NSMenuItem.separatorItem()
            else:
                title = data["title"]
                identifier = data.get("identifier")
                state = data.get("state", "off")
                state = _stateMap[state]
                binding = data.get("binding")
                target = data.get("target")
                action = data.get("action")
                callback = data.get("callback")
                subsubmenu = data.get("submenu")
                item = NSMenuItem.alloc().init()
                item.setTitle_(title)
                item.setState_(state)
                if binding is not None:
                    key, modifiers = binding
                    modifiers = sum([_modifierMap[i] for i in modifiers])
                    key = _keyMap.get(key, key)
                    item.setKeyEquivalent_(key)
                    item.setKeyEquivalentModifierMask_(modifiers)
                if identifier is not None:
                    self._idToItem[identifier] = item
                    identifiers.add(identifier)
                    if callback is not None:
                        target = VanillaCallbackWrapper(callback)
                        self._idToCallbackWrapper[identifier] = target
                        action = "action:"
                if target is not None:
                    item.setTarget_(target)
                if action is not None:
                    item.setAction_(action)
                if subsubmenu:
                    menu = NSMenu.alloc().initWithTitle_(title)
                    item.setSubmenu_(menu)
                    identifiers |= self._buildTree(menu, subsubmenu)
            parent.addItem_(item)
        return identifiers

    # --------
    # Teardown
    # --------

    def teardownMenu(self, owner, title=None):
        keys = []
        if title is not None:
            keys.append((owner, title))
        else:
            for o, t in self._ownerToMenu.keys():
                if o == owner:
                    keys.append((o, t))
        for key in keys:
            item = self._ownerToMenu.pop(key)
            self._mainMenu.removeItem_(item)
            for identifier in self._ownerToIds[key]:
                del self._idToCallbackWrapper[identifier]
                del self._idToItem[identifier]

    # ------------
    # Modification
    # ------------

    def getItem(self, identifier):
        return self._idToItem[identifier]

    def getItemData(self, identifier):
        item = self.getItem(identifier)
        data = dict(
            title=item.title(),
            state=_stateMap[item.state()]
        )
        return data

    def setItemData(self, identifier, data):
        title = data.get("title")
        state = data.get("state")
        item = self.getItem(identifier)
        if title is not None:
            item.setTitle_(title)
        if state is not None:
            state = _stateMap[state]
            item.setState_(state)


_manager = None
app = NSApp()
if app is not None:
    m = app.mainMenu()
    if m is not None:
        _manager = _MenuManager(m)


# ----
# Test
# ----

if __name__ == "__main__":
    import vanilla
    from vanilla.test.testTools import executeVanillaTest

    class Test(object):

        def __init__(self):
            app = NSApp()
            self.m = _MenuManager(app.mainMenu())

            self.w = vanilla.Window((500, 500))
            self.w.startButton = vanilla.Button((10, 10, -10, 20), "Start", callback=self.startButtonCallback)
            self.w.stopButton = vanilla.Button((10, 40, -10, 20), "Stop", callback=self.stopButtonCallback)
            self.w.reportButton = vanilla.Button((10, 70, -10, 20), "Dump", callback=self.reportButtonCallback)
            self.w.open()

        def aMenuItemCallback(self, sender):
            print sender

        def startButtonCallback(self, sender):
            items = [
                dict(
                    title="This Menu",
                    callback=self.aMenuItemCallback,
                    identifier="MenuTest.thisMenu",
                    binding=("e", ["command", "option"])
                ),
                dict(title="is built", action="isBuilt_"),
                dict(separator=True),
                dict(
                    title="on the fly!",
                    submenu=[
                        dict(title="foo"),
                        dict(title="bar"),
                    ]
                )
            ]
            self.m.buildMenu("MenuTest", "Hey Erik", items)

        def stopButtonCallback(self, sender):
            self.m.teardownMenu("MenuTest")

        def reportButtonCallback(self, sender):
            self.m.setItemData("MenuTest.thisMenu", title="Fooooooo")

    executeVanillaTest(Test)
