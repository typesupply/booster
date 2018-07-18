"""
--------------------
SharedActivityPoller
--------------------

This function returns the activity poller used by
all Booster based extensions. The main methods are
addObserver_ and removeObserver_. See below for
details on these.

The polling and notification precision tries to
be 0.01 seconds. However, since this is polling,
don't rely on a specific level of precision.
Also, keep in mind that each poll is a relatively
inefficient and expensive operation. Too much
polling will slow performance.
"""

from __future__ import division
import time
import re
import subprocess
import weakref
from collections import OrderedDict
from Foundation import NSObject, NSTimer
from AppKit import NSApp, NSNotificationCenter
from mojo.events import addObserver, removeObserver
from mojo.roboFont import AllFonts
from booster.debug import ClassNameIncrementer

# --------
# Defaults
# --------

def getDefaultPollingInterval():
    return 2.0

# -------
# Monitor
# -------

class ActivityPoller(NSObject, metaclass=ClassNameIncrementer):

    _timer = None
    _interval = getDefaultPollingInterval()
    _lastPoll = None
    _resignedActiveTime = None

    def init(self):
        self = super(ActivityPoller, self).init()
        self._observers = OrderedDict()
        nc = NSNotificationCenter.defaultCenter()
        nc.addObserver_selector_name_object_(
            self,
            "_appResignedActiveNotificationCallback:",
            "NSApplicationDidResignActiveNotification",
            NSApp()
        )
        return self

    def dealloc(self):
        nc = NSNotificationCenter.defaultCenter()
        app.removeObserver_name_object_(
            self,
            "NSApplicationDidResignActiveNotification",
            NSApp()
        )
        super(ActivityPoller, self).dealloc()

    def _appResignedActiveNotificationCallback_(self, notification):
        self._resignedActiveTime = time.time()

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
        if appIsActive:
            sinceUserActivity, endedUserActivity = userIdleTime()
        else:
            endedUserActivity = self._resignedActiveTime
            sinceUserActivity = time.time() - endedUserActivity
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
        self._notifyObserversWithInfo_(info)
        # Restart
        if self.polling():
            self._startTimer()

    # -------
    # Polling
    # -------

    def polling(self):
        """
        Returns a boolean indicating if the poller is
        actively monitoring for inactivity.
        """
        if self._timer is not None:
            return self._timer.isValid()
        else:
            return False

    def startPolling(self):
        """
        Start polling. This should not be called externally
        unless you have a really good reason to do so.
        """
        _fontObserver.startObserving()
        self._startTimer()

    def stopPolling(self):
        """
        Stop polling. This should not be called externally
        unless you have a really good reason to do so.
        """
        _fontObserver.stopObserving()
        self._stopTimer()

    def setInterval_(self, value):
        """
        Set the polling interval.
        """
        self._interval = value
        if self.polling():
            self.stopPolling()
            self.startPolling()

    # ---------
    # Observers
    # ---------

    def addObserver_(self, info):
        """
        Add an observer. The gist is that you define how much
        time should be allowed to elapse between events before
        being notified of inactivity.

        info must be a dict with this structure:

            {
                     observer : The observing object.
                     selector : The name of the method to call.
                  appIsActive : Boolean or None indicating if the app must
                                of must not be active for the notification
                                to be posted. False means that the app must
                                not be active. True means that the app must
                                be active. None means that the notification
                                should be posted if the app is active or is
                                not active.
            sinceUserActivity : Seconds of user inactivity.
                                Optional. The default is 2.0 seconds.
            sinceFontActivity : Seconds of font processing inactivity.
                                Optional. The default is 2.0 seconds.
                       repeat : Boolean indicating if the notification should
                                be posted repeatedly during an inactive period.
                                Optional. The default is False.
            }

        The method that will be called needs to have this signature:

            def myCallback(self, info):
                ...

        info will be a dict with this structure:

            {
                  appIsActive : Boolean indicating if the app is active.
                 userActivity : Boolean indicating if user activity has
                                occured since the last poll.
            sinceUserActivity : Seconds since the last user activity.
            endedUserActivity : When the last user activity occured.
                 fontActivity : Boolean indicating if font activity has
                                occured since the last poll.
            sinceFontActivity : Seconds since the last font activity.
            endedFontActivity : When the last font activity occured.
            }
        """
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
        """
        Remove an observer. The info dict must contain observer
        and selector as they are defined in addObserver_.
        """
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
            desiredAppIsActive = value["appIsActive"]
            desiredUserActivity = value["sinceUserActivity"]
            desiredFontActivity = value["sinceFontActivity"]
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
            meth(info)
            # store repeat stamp
            value["notifiedUserActivity"] = endedUserActivity
            value["notifiedFontActivity"] = endedFontActivity


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
    s = s.decode("UTF-8")
    times = idleTimePattern.findall(s)
    if not times:
        return 0
    times = [int(t) / nanoToSec for t in times]
    length = min(times)
    began = round(time.time() - length, 2) # round to hundredth of second to limit expected precision
    return length, began

# Main

_fontObserver = _FontObserver()
_activityPoller = ActivityPoller.alloc().init()

def SharedActivityPoller():
    return _activityPoller
