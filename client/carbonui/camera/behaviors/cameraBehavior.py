# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\camera\behaviors\cameraBehavior.py


class CameraBehavior(object):
    __guid__ = 'cameras.CameraBehavior'

    def __init__(self):
        self.gameWorldClient = sm.GetService('gameWorldClient')
        self.gameWorld = None
        self._LoadGameWorld()
        return

    def _LoadGameWorld(self):
        if self.gameWorldClient.HasGameWorld(session.worldspaceid):
            self.gameWorld = self.gameWorldClient.GetGameWorld(session.worldspaceid)

    def ProcessCameraUpdate(self, camera, now, frameTime):
        pass

    def _GetEntity(self, entID):
        return sm.GetService('entityClient').FindEntityByID(entID)

    def _GetEntityModel(self, entID):
        entity = sm.GetService('entityClient').FindEntityByID(entID)
        if entity and entity.HasComponent('paperdoll'):
            return entity.GetComponent('paperdoll').doll.avatar
        else:
            return None

    def Reset(self):
        pass

    def OnBehaviorAdded(self, camera):
        pass