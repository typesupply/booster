from AppKit import NSBundle

__all__ = [
    "identifier",
    "inRoboFont"
]

identifier = None

b = NSBundle.mainBundle()
if b is not None:
    identifier = b.bundleIdentifier().lower()

inRoboFont = identifier.lower() == "com.typemytype.robofont"
