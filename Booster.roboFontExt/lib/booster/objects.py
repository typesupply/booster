import weakref
from collections import OrderedDict
from defcon.tools.notifications import Notification
from fontParts.base.base import dynamicProperty
from mojo.roboFont import RFont, RInfo, RGroups, RKerning, RFeatures, RLib, \
    RLayer, RGlyph, RContour, RComponent, RAnchor, RGuideline, RImage
from booster.manager import SharedFontManager


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

    """
    This relay is used to wrap the objects sent via
    notifications in the appropriate wrappers rather
    than the defcon objects.
    """

    def _get_boosterNotificationReferences(self):
        tempData = self.bstr_tempData
        if not hasattr(tempData, "bstr_notificationReferences"):
            tempData.bstr_notificationReferences = {}
        return tempData.bstr_notificationReferences

    _bstr_notificationReferences = property(_get_boosterNotificationReferences)

    def _notificationRelay(self, notification):
        name = notification.name
        wrapped = Notification(
            name,
            weakref.ref(self),
            notification.data
        )
        notificationReferences = self._bstr_notificationReferences
        observers = notificationReferences.get(name)
        if observers:
            for observer, selector in observers.items():
                observer = observer()
                if observer is None:
                    continue
                meth = getattr(observer, selector)
                meth(wrapped)

    def bstr_addObserver(self, observer, selector, notification):
        observer = weakref.ref(observer)
        notificationReferences = self._bstr_notificationReferences
        if notification not in notificationReferences:
            notificationReferences[notification] = OrderedDict()
        notificationReferences[notification][observer] = selector
        observable = self.naked()
        observable.addObserver(self, "_notificationRelay", notification)

    def bstr_removeObserver(self, observer, notification):
        observer = weakref.ref(observer)
        notificationReferences = self._bstr_notificationReferences
        del notificationReferences[notification][observer]
        if not notificationReferences[notification]:
            observable = self.naked()
            observable.removeObserver(self, notification)


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

    def _close(self, save=False):
        manager = SharedFontManager()
        manager.fontWillClose(self)
        super(BoosterFont, self)._close(save)

    # -----------
    # Unique Name
    # -----------

    uniqueName = dynamicProperty(
        "uniqueName",
        doc="""
            A unique name for use in interfaces. If `None` is returned,
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
        `others` should be all open fonts.
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
