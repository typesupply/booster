"""
Base objects and object creators.

These can be subclassed to suite an extension's needs.
Subclass Font and any necessary classes, setting the
*Class attributes as needed.
"""

__all__ = [
    "AllFonts",
    "CurrentFont",
    "CurrentGlyph",
    "NewFont",
    "OpenFont",
    "AppExtFont",
    "AppExtInfo",
    "AppExtGroups",
    "AppExtKerning",
    "AppExtFeatures",
    "AppExtLib",
    "AppExtLayer",
    "AppExtGlyph",
    "AppExtContour",
    "AppExtComponent",
    "AppExtAnchor",
    "AppExtGuideline",
    "AppExtImage"
]

from appext import environment

if environment.inRoboFont:
    # XXX Frederik: can you add these to mojo.roboFont?
    from lib.fontObjects import fontPartsWrappers as roboFont
    baseFont = roboFont.RFont
    baseInfo = roboFont.RInfo
    baseGroups = roboFont.RGroups
    baseKerning = roboFont.RKerning
    baseFeatures = roboFont.RFeatures
    baseLib = roboFont.RLib
    baseLayer = roboFont.RLayer
    baseGlyph = roboFont.RGlyph
    baseContour = roboFont.RContour
    baseComponent = roboFont.RComponent
    baseAnchor = roboFont.RAnchor
    baseGuideline = roboFont.RGuideline
    baseImage = roboFont.RImage
    from mojo import roboFont
    AllFonts = roboFont.AllFonts
    CurrentFont = roboFont.CurrentFont
    CurrentGlyph = roboFont.CurrentGlyph
    NewFont = roboFont.NewFont
    OpenFont = roboFont.OpenFont
else:
    raise NotImplementedError


class AppExtBase(object):

    # ---------------
    # Representations
    # ---------------

    def getRepresentation(self, name, **kwargs):
        return self.naked().getRepresentation(name, **kwargs)

    def destroyRepresentation(self, name, **kwargs):
        self.naked().destroyRepresentation(name, **kwargs)

    def destroyAllRepresentations(self):
        self.naked().destroyAllRepresentations()

    # -------------
    # Notifications
    # -------------

    def addObserver(self, observer, methodName, notification):
        self.naked().addObserver(observer, methodName, notification)

    def removeObserver(self, observer, notification):
        self.naked().removeObserver(observer, notification)

    def hasObserver(self, observer, notification):
        return self.naked().hasObserver(observer, notification)

    def holdNotifications(self, notification=None):
        self.naked().holdNotifications(self, notification=notification)

    def releaseHeldNotifications(self, notification=None):
        self.naked().releaseHeldNotifications(self, notification=notification)

    def disableNotifications(self, notification=None, observer=None):
        self.naked().disableNotifications(notification=notification, observer=observer)

    def enableNotifications(self, notification=None, observer=None):
        self.naked().enableNotifications(notification=notification, observer=observer)

    def postNotification(self, notification, data=None):
        self.naked().postNotification(notification, data=data)


class AppExtLib(AppExtBase, baseLib):

    wrapClass = baseLib.wrapClass


class AppExtImage(AppExtBase, baseImage):

    wrapClass = baseImage.wrapClass


class AppExtGuideline(AppExtBase, baseGuideline):

    wrapClass = baseGuideline.wrapClass


class AppExtAnchor(AppExtBase, baseAnchor):

    wrapClass = baseAnchor.wrapClass


class AppExtComponent(AppExtBase, baseComponent):

    wrapClass = baseComponent.wrapClass


class AppExtContour(AppExtBase, baseContour):

    wrapClass = baseContour.wrapClass


class AppExtGlyph(AppExtBase, baseGlyph):

    wrapClass = baseGlyph.wrapClass
    contourClass = AppExtContour
    componentClass = AppExtComponent
    anchorClass = AppExtAnchor
    guidelineClass = AppExtGuideline
    imageClass = AppExtImage
    libClass = AppExtLib


class AppExtLayer(AppExtBase, baseLayer):

    wrapClass = baseLayer.wrapClass
    libClass = AppExtLib
    glyphClass = AppExtGlyph


class AppExtFeatures(AppExtBase, baseFeatures):

    wrapClass = baseFeatures.wrapClass


class AppExtKerning(AppExtBase, baseKerning):

    wrapClass = baseKerning.wrapClass


class AppExtGroups(AppExtBase, baseGroups):

    wrapClass = baseGroups.wrapClass


class AppExtInfo(AppExtBase, baseInfo):

    wrapClass = baseInfo.wrapClass


class AppExtFont(AppExtBase, baseFont):

    wrapClass = baseFont.wrapClass
    infoClass = AppExtInfo
    groupsClass = AppExtGroups
    kerningClass = AppExtKerning
    featuresClass = AppExtFeatures
    libClass = AppExtLib
    layerClass = AppExtLayer
    guidelineClass = AppExtGuideline
