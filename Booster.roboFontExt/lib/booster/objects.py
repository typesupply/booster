import weakref
from collections import OrderedDict
from defcon.tools.notifications import Notification
from fontParts.base.base import dynamicProperty
from mojo.roboFont import RFont, RInfo, RGroups, RKerning, RFeatures, RLib, \
    RLayer, RGlyph, RContour, RComponent, RAnchor, RGuideline, RImage


# --------------
# Temporary Data
# --------------

class TempDataMixin(object):

    bstr_tempData = dynamicProperty("boosterTempData")

    def _get_boosterTempData(self):
        obj = self.naked()
        if not hasattr(obj, "bstr_tempData"):
            obj.bstr_tempData = TempData()
        return obj.bstr_tempData


class TempData(object): pass


# -------------
# Notifications
# -------------

class BoosterNotificationMixin(object):

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


class BoosterInfo(RInfo, TempDataMixin, BoosterNotificationMixin): pass


class BoosterGroups(RGroups, TempDataMixin, BoosterNotificationMixin): pass


class BoosterKerning(RKerning, TempDataMixin, BoosterNotificationMixin): pass


class BoosterFeatures(RFeatures, TempDataMixin, BoosterNotificationMixin): pass


class BoosterLib(RLib, TempDataMixin, BoosterNotificationMixin): pass


class BoosterContour(RContour, TempDataMixin, BoosterNotificationMixin): pass


class BoosterComponent(RComponent, TempDataMixin, BoosterNotificationMixin): pass


class BoosterAnchor(RAnchor, TempDataMixin, BoosterNotificationMixin): pass


class BoosterGuideline(RGuideline, TempDataMixin, BoosterNotificationMixin): pass


class BoosterImage(RImage, TempDataMixin, BoosterNotificationMixin): pass


class BoosterGlyph(RGlyph, TempDataMixin, BoosterNotificationMixin):

    contourClass = BoosterContour
    componentClass = BoosterComponent
    anchorClass = BoosterAnchor
    guidelineClass = BoosterGuideline
    imageClass = BoosterImage
    libClass = BoosterLib


class BoosterLayer(RLayer, TempDataMixin, BoosterNotificationMixin):

    libClass = BoosterLib
    glyphClass = BoosterGlyph


class BoosterFont(RFont, TempDataMixin, BoosterNotificationMixin):

    infoClass = BoosterInfo
    groupsClass = BoosterGroups
    kerningClass = BoosterKerning
    featuresClass = BoosterFeatures
    libClass = BoosterLib
    layerClass = BoosterLayer
    guidelineClass = BoosterGuideline

    uniqueName = dynamicProperty("uniqueName")

    def _get_uniqueName(self):
        if not hasattr(self.bstr_tempData, "bstr_uniqueName"):
            self.bstr_tempData.bstr_uniqueName = None
        return self.bstr_tempData.bstr_uniqueName

    def makeUniqueName(self, others):
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
