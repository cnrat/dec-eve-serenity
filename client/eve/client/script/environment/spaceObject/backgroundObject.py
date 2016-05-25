# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\backgroundObject.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import trinity

class BackgroundObject(SpaceObject):

    def LoadModel(self):
        graphicURL = self.typeData.get('graphicFile')
        obj = trinity.Load(graphicURL)
        self.backgroundObject = obj
        scene = self.spaceMgr.GetScene()
        scene.backgroundObjects.append(obj)

    def Release(self):
        if self.released:
            return
        else:
            scene = self.spaceMgr.GetScene()
            if scene:
                scene.backgroundObjects.fremove(self.backgroundObject)
            self.backgroundObject = None
            SpaceObject.Release(self, 'BackgroundObject')
            return