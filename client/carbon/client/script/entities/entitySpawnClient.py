# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\client\script\entities\entitySpawnClient.py
import entities

class EntitySpawnClient(entities.EntitySpawnService):
    __guid__ = 'svc.entitySpawnClient'
    __dependencies__ = entities.EntitySpawnService.__dependencies__
    __dependencies__ += ['worldSpaceClient']

    def Run(self, *args):
        entities.EntitySpawnService.Run(self, args)
        self.idCounter = const.minFakeClientItem

    def GetNextEntityID(self):
        self.idCounter += 1
        return self.idCounter

    def GetWorldSpaceTypeID(self, sceneID):
        return self.worldSpaceClient.GetWorldSpaceTypeIDFromWorldSpaceID(sceneID)

    def GetSceneID(self, worldSpaceTypeID):
        raise NotImplementedError('GetSceneID() function not implemented on: ', self.__guid__)