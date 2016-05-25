# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\LargeCollidableObject.py
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject

class LargeCollidableObject(SpaceObject):

    def Assemble(self):
        self.SetStaticRotation()
        if getattr(self.model, 'ChainAnimationEx', None) is not None:
            self.model.ChainAnimationEx('NormalLoop', 0, 0, 1.0)
        self.SetupSharedAmbientAudio()
        return