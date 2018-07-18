"""
---------------
Booster Objects
---------------

These objects are subclasses of the RoboFont wrapper classes,
so support everything that the RoboFont and fontParts objects
do. They also implement some important functionality required
by Booster along with some other useful functionality. If you
are building a Booster based extension, you must use these
classes or your own subclasses of them.

Here are the big things that these implement:


Temporary Data Storage
----------------------

Each object has a bstr_tempData sub-object. This is a container
for storing data that does not need to be retained in the written
UFO. The values are written to attributes of your own design.
So, you know, make the attribute names unique. I suggest that
you use an identifier, then an underscore and then a descriptive
tag. (This is the same as the fontParts environment specific
method/attribute naming system.) Here's how you set something:

    something.bstr_tempData.blah_number = 13

Here's how you get something:

    text = "blah" * something.bstr_tempData.blah_number

The values are completely up to you. It can be a standard type,
a custom object or whatever. The data will be stored in the
low-level defcon objects, so if your object wrapper is lost,
you can still get it by rewrapping the lower-level object.


Automatic Font Manager Interaction
----------------------------------

The font class will alert the font manager when a font is
opened/closed regardless of whether it has an interface or not.
It is extremely important that you close fonts without interfaces
once you are done using them. The font manager will retain a reference
to them and they will stay in memory until you close them.


See below for additional things.
"""

import weakref
from fontParts.base.base import dynamicProperty
from mojo.roboFont import RFont, RInfo, RGroups, RKerning, RFeatures, RLib, \
    RLayer, RGlyph, RContour, RComponent, RAnchor, RGuideline, RImage
from .manager import SharedFontManager


# --------------
# Temporary Data
# --------------

class TempDataMixin(object):

    bstr_tempData = dynamicProperty("bstr_tempData")

    def _get_bstr_tempData(self):
        obj = self.naked()
        if not hasattr(obj, "_bstr_tempData"):
            obj._bstr_tempData = TempData()
        return obj._bstr_tempData


class TempData(object): pass


# -------------
# Notifications
# -------------

class BoosterDefconNotificationMixin(object):

    def bstr_postNotification(self, notification, data=None):
        if hasattr(self, "postNotification"):
            self.postNotification(notification, data=data)
        else:
            self.naked().postNotification(notification, data=data)


# ------------------
# FontParts Wrappers
# ------------------


class BoosterInfo(RInfo, TempDataMixin, BoosterDefconNotificationMixin): pass


class BoosterGroups(RGroups, TempDataMixin, BoosterDefconNotificationMixin): pass


class BoosterKerning(RKerning, TempDataMixin, BoosterDefconNotificationMixin): pass


class BoosterFeatures(RFeatures, TempDataMixin, BoosterDefconNotificationMixin): pass


class BoosterLib(RLib, TempDataMixin, BoosterDefconNotificationMixin): pass


class BoosterContour(RContour, TempDataMixin, BoosterDefconNotificationMixin): pass


class BoosterComponent(RComponent, TempDataMixin, BoosterDefconNotificationMixin): pass


class BoosterAnchor(RAnchor, TempDataMixin, BoosterDefconNotificationMixin): pass


class BoosterGuideline(RGuideline, TempDataMixin, BoosterDefconNotificationMixin): pass


class BoosterImage(RImage, TempDataMixin, BoosterDefconNotificationMixin): pass


class BoosterGlyph(RGlyph, TempDataMixin, BoosterDefconNotificationMixin):

    contourClass = BoosterContour
    componentClass = BoosterComponent
    anchorClass = BoosterAnchor
    guidelineClass = BoosterGuideline
    imageClass = BoosterImage
    libClass = BoosterLib


class BoosterLayer(RLayer, TempDataMixin, BoosterDefconNotificationMixin):

    libClass = BoosterLib
    glyphClass = BoosterGlyph


class BoosterFont(RFont, TempDataMixin, BoosterDefconNotificationMixin):

    infoClass = BoosterInfo
    groupsClass = BoosterGroups
    kerningClass = BoosterKerning
    featuresClass = BoosterFeatures
    libClass = BoosterLib
    layerClass = BoosterLayer
    guidelineClass = BoosterGuideline

    # ------------------------
    # Font Manager Interaction
    # ------------------------

    def _init(self, pathOrObject=None, showInterface=True, **kwargs):
        super(BoosterFont, self)._init(pathOrObject, showInterface, **kwargs)
        # don't announce ths as a new font if
        # the font manager has already seen it.
        announce = False
        if pathOrObject is None or isinstance(pathOrObject, str):
            announce = True
        elif not hasattr(pathOrObject, "_bstr_tempData"):
            d = self.bstr_tempData
            announce = True
        if announce:
            manager = SharedFontManager()
            manager.fontDidOpen(self)

    def _close(self, **kwargs):
        manager = SharedFontManager()
        manager.fontWillClose(self)
        super(BoosterFont, self)._close(**kwargs)

    # -----------
    # Unique Name
    # -----------

    uniqueName = dynamicProperty(
        "uniqueName",
        doc="""
            A unique name for the font. If `None` is returned,
            call `makeUniqueName` to assign a name to this font.
            """
        )

    def _get_uniqueName(self):
        if not hasattr(self.bstr_tempData, "bstr_uniqueName"):
            self.bstr_tempData.bstr_uniqueName = None
        return self.bstr_tempData.bstr_uniqueName

    def makeUniqueName(self, others):
        """
        Make a unique name for and assign it to this font.
        `others` should be all open fonts. This name is suitable
        for use as informative text in interface controls (such
        as font selection controls) but should not be used for
        storage, reference or anything else that requires
        reproducability.
        """
        existing = set()
        for font in others:
            if font == self:
                continue
            if font.uniqueName is not None:
                existing.add(font.uniqueName)
        family = self.info.familyName
        style = self.info.styleName
        if family is None:
            family = "Untitled Family"
        if style is None:
            style = "Untitled Style"
        name = "-".join((family, style))
        if name == "Untitled Family-Untitled Style":
            name = "Untitled Font"
        increment = None
        while 1:
            if increment is None:
                if name not in existing:
                    break
                else:
                    increment = 1
            else:
                n = name + " " + repr(increment)
                if n not in existing:
                    name = n
                    break
                else:
                    increment += 1
        self.bstr_tempData.bstr_uniqueName = name
        return name
