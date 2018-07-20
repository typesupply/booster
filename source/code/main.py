"""
This is a tool for monitoring the internals of Booster.
"""

from AppKit import NSApp, NSTimer
import vanilla
from defconAppKit.windows.baseWindow import BaseWindowController
from booster.controller import BoosterController
from booster.activity import SharedActivityPoller
from booster.requests import SharedRequestCenter

# --------------------
# Controller/Responder
# --------------------

class BoosterStatusMonitorController(BoosterController):

    statusPanel = None

    def start(self):
        super(BoosterStatusMonitorController, self).start()
        app = NSApp()
        app.com_typesupply_boosterMonitor = self
        self.addResponder(self, "showStatusPanelResponder", "BoosterMonitor.ShowStatusPanel")

    def stop(self):
        super(BoosterStatusMonitorController, self).stop()
        app = NSApp()
        app.boosterMonitor = None
        self.removeResponder("BoosterMonitor.ShowStatusPanel")

    def showStatusPanelResponder(self):
        if self.statusPanel is None:
            self.statusPanel = BoosterStatusMonitorPanelController(self)

    def statusPanelWillCloseCallback(self):
        self.statusPanel = None


# -----
# Panel
# -----

userActivityTemplate = "Seconds since user activity: %.2f"
fontActivityTemplate = "Seconds since font activity: %.2f"


class BoosterStatusMonitorPanelController(BaseWindowController):

    def __init__(self, controller):
        self.controller = controller
        self.w = vanilla.FloatingWindow((800, 500), "Booster Status", minSize=(400, 400))
        self.w.tabs = vanilla.Tabs((15, 15, -15, -15), ["Fonts", "Activity", "Requests"])

        self.fontsTab.list = vanilla.List(
            (15, 15, -15, -15),
            [],
            columnDescriptions=[
                dict(title="visible", width=50),
                dict(title="name")
            ]
        )

        self.inactivityInfo = None
        self.activityTab.userInfoTextBox = vanilla.TextBox((15, 15, -15, 17), userActivityTemplate % 0)
        self.activityTab.fontInfoTextBox = vanilla.TextBox((15, 40, -15, 17), "<font info>")
        self.activityTab.list = vanilla.List(
            (15, 80, -15, -15),
            [],
            columnDescriptions=[
                dict(title="observer"),
                dict(title="selector"),
                dict(title="sinceUserActivity"),
                dict(title="sinceFontActivity"),
                dict(title="repeat")
            ]
        )

        self.requestsTab.list = vanilla.List(
            (15, 15, -15, -15),
            [],
            columnDescriptions=[
                dict(title="request"),
                dict(title="responder"),
                dict(title="selector")
            ]
        )

        self.setUpBaseWindowBehavior()

        self.controller.addObserver(self, "updateFontList", "bstr.availableFontsChanged")
        self.updateFontList()

        self.controller.addActivityObserver(self, "inactivityCallback", sinceUserActivity=0.25, sinceFontActivity=0.25, repeat=True)
        self.controller.addActivityObserver(self, "updateActivityObserverList")
        self.updateActivityObserverList()

        center = SharedRequestCenter()
        center.addObserver(self, "updateRespondersList", "BoosterRequestCenter.AddedResponder")
        center.addObserver(self, "updateRespondersList", "BoosterRequestCenter.RemovedResponder")
        self.updateResponderList()

        self.startActivityTimer()

        self.w.open()

    def windowCloseCallback(self, sender):
        super(BoosterStatusMonitorPanelController, self).windowCloseCallback(sender)
        self.controller.removeObserver(self, "bstr.availableFontsChanged")
        self.stopActivityTimer()
        self.controller.removeActivityObserver(self, "inactivityCallback")
        self.controller.removeActivityObserver(self, "updateActivityObserverList")
        center = SharedRequestCenter()
        center.removeObserver(self, "BoosterRequestCenter.AddedResponder")
        center.removeObserver(self, "BoosterRequestCenter.RemovedResponder")
        self.controller = None

    # Tabs

    def _get_fontsTab(self):
        return self.w.tabs[0]

    fontsTab = property(_get_fontsTab)

    def _get_activityTab(self):
        return self.w.tabs[1]

    activityTab = property(_get_activityTab)

    def _get_requestsTab(self):
        return self.w.tabs[2]

    requestsTab = property(_get_requestsTab)

    # Fonts

    def updateFontList(self, info=None):
        items = []
        for font in self.controller.getAllFonts():
            name = font.uniqueName
            if name is None:
                name = font.makeUniqueName()
            visible = font.hasInterface()
            d = dict(
                name=name,
                visible=repr(visible)
            )
            items.append(d)
        self.fontsTab.list.set(items)

    # Activity

    def inactivityCallback(self, info=None):
        self.inactivityInfo = info

    def startActivityTimer(self):
        self._activityTimer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            0.25,
            self,
            "activityTimerCallback",
            None,
            False
        )
        self._activityTimer.setTolerance_(0.25)

    def stopActivityTimer(self):
        if self._activityTimer is not None:
            self._activityTimer.invalidate()
            self._activityTimer = None

    def activityTimerCallback(self):
        if self.inactivityInfo is None:
            userTime = 0
            fontTime = 0
        else:
            userTime = self.inactivityInfo["sinceUserActivity"]
            fontTime = self.inactivityInfo["sinceFontActivity"]
        self.activityTab.userInfoTextBox.set(userActivityTemplate % userTime)
        self.activityTab.fontInfoTextBox.set(fontActivityTemplate % fontTime)
        self.startActivityTimer()

    def updateActivityObserverList(self, info=None):
        observers = SharedActivityPoller()._observers
        items = []
        for (observer, selector), data in observers.items():
            observer = observer()
            if observer is not None:
                observer = observer.__class__.__name__
            else:
                observer = "<dead reference>"
            d = dict(
                observer=observer,
                selector=selector,
                sinceUserActivity=repr(data.get("sinceUserActivity")),
                sinceFontActivity=repr(data.get("sinceFontActivity")),
                repeat=repr(data.get("repeat", False))
            )
            items.append(d)
        self.activityTab.list.set(items)

    # Requests

    def updateResponderList(self, notification=None):
        responders = SharedRequestCenter().responders
        items = []
        for request, responder in sorted(responders.items()):
            responder, selector = responder
            responder = responder()
            if responder is not None:
                responder = responder.__class__.__name__
            else:
                responder = "<dead reference>"
            d = dict(
                request=request,
                responder=responder,
                selector=selector
            )
            items.append(d)
        self.requestsTab.list.set(items)


if __name__ == "__main__":
    monitor = BoosterStatusMonitorController()
    monitor.start()
