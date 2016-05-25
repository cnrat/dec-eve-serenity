# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\cargo.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
import trinity

class Cargo(SpaceObject):

    def Assemble(self):
        self.UnSync()
        if self.model is not None:
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        return

    def Explode(self):
        if self.exploded:
            return False
        elif self.model is None:
            return
        else:
            self.exploded = True
            fileName = 'res:/dx9/Model/WorldObject/Cargo/cargoContainerImploding.red'
            gfx = trinity.Load(fileName)
            if gfx:
                gfx.translationCurve = self
                gfx.modelRotationCurve = self.model.modelRotationCurve
                self.explosionModel = gfx
            else:
                self.LogError('Cargo Container Misisng GFX for explosion. Could not find %s', fileName)
            scene = self.spaceMgr.GetScene()
            scene.objects.append(gfx)
            return False