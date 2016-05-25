# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\entities\entityMonitor.py
import uicls
import util

class EveEntityBrowser(uicls.EntityBrowserCore):
    __guid__ = 'uicls.EntityBrowser'

    def GetSceneName(self, sceneID):
        return cfg.evelocations.Get(sceneID).name

    def GetEntityName(self, entity):
        if entity.HasComponent('info'):
            return entity.GetComponent('info').name
        try:
            if util.IsCharacter(entity.entityID):
                return cfg.eveowners.Get(entity.entityID).name
        except:
            pass

        return 'Entity %s' % entity.entityID

    def GetEntitySpawnID(self, entity):
        if entity.HasComponent('info'):
            return entity.info.spawnID and entity.info.spawnID

    def GetEntityRecipeID(self, entity):
        if entity.HasComponent('info') and entity.info.recipeID:
            return entity.info.recipeID