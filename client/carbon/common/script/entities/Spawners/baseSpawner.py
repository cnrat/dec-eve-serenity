# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\entities\Spawners\baseSpawner.py


class BaseSpawner(object):
    __guid__ = 'cef.BaseSpawner'

    def __init__(self, sceneID):
        self.sceneID = sceneID

    def GetSceneID(self):
        return self.sceneID

    def GetEntityID(self):
        return False

    def GetPosition(self):
        raise NotImplementedError('GetPosition() not defined on:', self.__guid__)

    def GetRotation(self):
        raise NotImplementedError('GetRotation() not defined on:', self.__guid__)

    def GetRecipe(self, entityRecipeSvc):
        raise NotImplementedError('GetRecipe() not defined on:', self.__guid__)

    def CanSpawn(self):
        if self.GetPosition() is None:
            return False
        elif self.GetRotation() is None:
            return False
        else:
            return True

    def _OverrideRecipePosition(self, recipeOverrides, position, rotation):
        if const.cef.POSITION_COMPONENT_ID not in recipeOverrides:
            recipeOverrides[const.cef.POSITION_COMPONENT_ID] = {}
        recipeOverrides[const.cef.POSITION_COMPONENT_ID]['position'] = position
        recipeOverrides[const.cef.POSITION_COMPONENT_ID]['rotation'] = rotation
        return recipeOverrides