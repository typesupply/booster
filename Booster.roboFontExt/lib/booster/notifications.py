from defcon.tools.notifications import NotificationCenter

class BoosterNotificationCenter(NotificationCenter): pass

# ----
# Main
# ----

_dispatcher = BoosterNotificationCenter()

def SharedNotificationCenter():
    return _dispatcher