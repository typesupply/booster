from AppKit import *
from vanilla.vanillaBase import VanillaCallbackWrapper


"""
The aplication's shared menubar.

SharedMenubar.buildMenu("MyExtension.Go", "Go", items)
SharedMenubar.teardownMenu("MyExtension.Go")
data = SharedMenubar.getItemData("MyExtension.Go.something")
SharedMenubar.setItemData("MyExtension.Go.something", {"state" : "mixed"})

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

class _MenubarManager(object):

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


# -------------
# Shared Object
# -------------

_manager = None

def SharedMenubar():
    global _manager
    if _manager is None:
        app = NSApp()
        m = app.mainMenu()
        _manager = _MenubarManager(m)
    return _manager
