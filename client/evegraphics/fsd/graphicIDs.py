# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\fsd\graphicIDs.py
import os
try:
    import fsd.schemas.binaryLoader as binaryLoader
except ImportError:
    import site
    branchRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    site.addsitedir(os.path.abspath(os.path.join(branchRoot, 'packages')))
    import fsd.schemas.binaryLoader as binaryLoader

class GraphicIDs(object):
    __binary__ = None

    @staticmethod
    def __LoadGraphicIDBinary():
        try:
            data = binaryLoader.LoadFSDDataForCFG('res:/staticdata/graphicIDs.static')
            if data is None:
                raise ImportError
            return data
        except ImportError:
            import devenv
            pathRelativeToBranchRoot = 'eve/autobuild/staticdata/client/graphicIDs.static'
            autobuildFilePath = os.path.abspath(os.path.join(devenv.BRANCHROOT, pathRelativeToBranchRoot))
            return binaryLoader.LoadFSDDataInPython(autobuildFilePath)

        return

    @staticmethod
    def GetData():
        if GraphicIDs.__binary__ is None:
            GraphicIDs.__binary__ = GraphicIDs.__LoadGraphicIDBinary()
        return GraphicIDs.__binary__


def GetGraphicIDDictionary():
    return GraphicIDs.GetData()


def GetGraphic(graphicID):
    return GraphicIDs.GetData().get(graphicID, None)


def GetGraphicIDAttribute(graphicID, attributeName, default=None):
    return getattr(GetGraphic(graphicID), attributeName, default)


def GetGraphicFile(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'graphicFile', default)


def GetExplosionBucket(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'explosionBucket', default)


def GetSofRaceName(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'sofRaceName', default)


def GetSofHullName(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'sofHullName', default)


def GetSofFactionName(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'sofFactionName', default)


def GetCollisionFile(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'collisionFile', default)


def GetIsisIconPath(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'isisIconPath', default)


def GetAnimationStates(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'animationStates', default)


def GetAnimationStateObjects(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'animationStateObjects', default)


def GetAmmoColor(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'ammoColor', default)


def GetAlbedoColor(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'albedoColor', default)


def GetEmissiveColor(graphicID, default=None):
    return GetGraphicIDAttribute(graphicID, 'emissiveColor', default)