from __future__ import division
import time
import re
import subprocess
import weakref
from collections import OrderedDict
from Foundation import NSObject, NSTimer
from AppKit import NSApp
from mojo.events import publishEvent
from mojo.events import addObserver, removeObserver
from mojo.roboFont import AllFonts

# --------
# Defaults
# --------

def getDefaultPollingInterval():
    return 2.0

# -------
# Monitor
# -------

class ActivityPoller(NSObject):

    _timer = None
    _interval = getDefaultPollingInterval()
    _lastPoll = None

    def init(self):
        self = super(ActivityPoller, self).init()
        self._observers = OrderedDict()
        return self

    # -----
    # Timer
    # -----

    def _startTimer(self):
        self._timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            self._interval,
            self,
            "_timerCallback:",
            None,
            False
        )
        self._timer.setTolerance_(0.25)

    def _stopTimer(self):
        if self._timer is not None:
            self._timer.invalidate()
            self._timer = None

    def _timerCallback_(self, timer):
        idle = False
        # App activity
        app = NSApp()
        appIsActive = app.isActive()
        # Font activity
        sinceFontActivity, endedFontActivity = _fontObserver.fontIdleTime()
        # User activity
        sinceUserActivity = None
        if appIsActive:
            sinceUserActivity, endedUserActivity = userIdleTime()
        # Activity since last poll
        lastPoll = self._lastPoll
        userActivity = False
        fontActivity = False
        now = time.time()
        self._lastPoll = now
        if lastPoll is not None:
            sinceLastPoll = now - lastPoll
            fontActivity = sinceFontActivity < sinceLastPoll
            if sinceUserActivity is not None:
                userActivity = sinceUserActivity < sinceLastPoll
        # Notify observers
        info = dict(
            appIsActive=appIsActive,
            userActivity=userActivity,
            sinceUserActivity=sinceUserActivity,
            endedUserActivity=endedUserActivity,
            fontActivity=fontActivity,
            sinceFontActivity=sinceFontActivity,
            endedFontActivity=endedFontActivity
        )
        self._notifyObserversForInfo_(info)
        # Restart
        if self.polling():
            self._startTimer()

    # -------
    # Polling
    # -------

    def polling(self):
        if self._timer is not None:
            return self._timer.isValid()
        else:
            return False

    def startPolling(self):
        _fontObserver.startObserving()
        self._startTimer()

    def stopPolling(self):
        _fontObserver.stopObserving()
        self._stopTimer()

    def setInterval_(self, value):
        self._interval = value
        if self.polling():
            self.stopPolling()
            self.startPolling()

    # ---------
    # Observers
    # ---------

    def addObserver_(self, info):
        observer = info["observer"]
        observer = weakref.ref(observer)
        selector = info["selector"]
        value = dict(
            appIsActive=info.get("appIsActive"),
            sinceUserActivity=info.get("sinceUserActivity"),
            sinceFontActivity=info.get("sinceFontActivity"),
            repeat=info.get("repeat", False),
            notifiedFontActivity=None,
            notifiedUserActivity=None
        )
        self._observers[observer, selector] = value
        if self.polling():
            self.stopPolling()
        self.startPolling()

    def removeObserver_(self, info):
        observer = info["observer"]
        observer = weakref.ref(observer)
        selector = info["selector"]
        del self._observers[observer, selector]
        if not self._observers:
            self.stopPolling()

    def _notifyObserversWithInfo_(self, info):
        now = time.time()
        appIsActive = info["appIsActive"]
        sinceUserActivity = info["sinceUserActivity"]
        endedUserActivity = info["endedUserActivity"]
        sinceFontActivity = info["sinceFontActivity"]
        endedFontActivity = info["endedFontActivity"]
        for (observer, selector), value in self._observers.items():
            desiredAppIsActive = value["desiredAppIsActive"]
            desiredUserActivity = value["desiredUserActivity"]
            desiredFontActivity = value["desiredFontActivity"]
            repeat = value["repeat"]
            notifiedUserActivity = value["notifiedUserActivity"]
            notifiedFontActivity = value["notifiedFontActivity"]
            # app not in desired active state
            if desiredAppIsActive is not None:
                if desiredAppIsActive != appIsActive:
                    continue
            # too recent user activity
            if desiredUserActivity:
                if desiredUserActivity > sinceUserActivity:
                    continue
            # too recent font activity
            if desiredFontActivity:
                if desiredFontActivity > sinceFontActivity:
                    continue
            # don't want repeat and already notified
            if not repeat:
                if notifiedUserActivity == endedUserActivity and notifiedFontActivity == endedFontActivity:
                    continue
            # notify
            observer = observer()
            meth = getattr(observer, selector)
            meth(self, info)
            # store repeat stamp
            value["notifiedUserActivity"] = now
            value["notifiedFontActivity"] = now


# -------------
# Font Observer
# -------------

class _FontObserver(object):

    _lastNotificationTime = None

    def fontIdleTime(self):
        if self._lastNotificationTime is None:
            return 0
        length = time.time() - self._lastNotificationTime
        began = self._lastNotificationTime
        return length, began

    def startObserving(self):
        self._lastNotificationTime = time.time()
        openEvents = [
            "newFontDidOpen",
            "fontDidOpen"
        ]
        for event in openEvents:
            addObserver(
                self,
                "_fontDidOpenEventCallback",
                event
            )
        addObserver(
            self,
            "_fontWillCloseEventCallback",
            "fontWillClose"
        )
        for font in AllFonts():
            self._fontDidOpenEventCallback(dict(font=font))

    def stopObserving(self):
        self._lastNotificationTime = None
        openEvents = [
            "newFontDidOpen",
            "fontDidOpen"
        ]
        for event in openEvents:
            removeObserver(
                self,
                event
            )
        removeObserver(
            self,
            "fontWillClose"
        )
        for font in AllFonts():
            self._fontWillCloseEventCallback(dict(font=font))

    # Event Callbacks

    def _fontDidOpenEventCallback(self, info):
        font = info["font"]
        font.addObserver(
            self,
            "_fontChangeNotificationCallback",
            "Font.Changed"
        )

    def _fontWillCloseEventCallback(self, info):
        font = info["font"]
        font.removeObserver(
            self,
            "Font.Changed"
        )

    # Font Callbacks

    def _fontChangeNotificationCallback(self, notification):
        self._lastNotificationTime = time.time()


# ---------------------
# Idle Time Calculation
# ---------------------

idleTimePattern = re.compile("\"HIDIdleTime\"\s*=\s*(\d+)")
nanoToSec = 10 ** 9

def userIdleTime():
    # http://stackoverflow.com/questions/2425087/testing-for-inactivity-in-python-on-mac
    s = subprocess.Popen(
        ["ioreg", "-c", "IOHIDSystem"], stdout=subprocess.PIPE
    ).communicate()[0]
    times = idleTimePattern.findall(s)
    if not times:
        return 0
    times = [long(t) / nanoToSec for t in times]
    length = min(times)
    began = round(time.time() - length, 2) # round to hundredth of second to limit expected precision
    return length, began

# Main

_fontObserver = _FontObserver()
_activityPoller = ActivityPoller.alloc().init()

def ShareActivityPoller():
    return _activityPoller
