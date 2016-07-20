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
    from fontParts import nonelab
    baseFont = nonelab.RFont
    baseInfo = nonelab.RInfo
    baseGroups = nonelab.RGroups
    baseKerning = nonelab.RKerning
    baseFeatures = nonelab.RFeatures
    baseLib = nonelab.RLib
    baseLayer = nonelab.RLayer
    baseGlyph = nonelab.RGlyph
    baseContour = nonelab.RContour
    baseComponent = nonelab.RComponent
    baseAnchor = nonelab.RAnchor
    baseGuideline = nonelab.RGuideline
    baseImage = nonelab.RImage
    from fontParts import world
    AllFonts = world.AllFonts
    CurrentFont = world.CurrentFont
    CurrentGlyph = world.CurrentGlyph
    NewFont = world.NewFont
    OpenFont = world.OpenFont


class AppExtBase(object):

    pass


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
