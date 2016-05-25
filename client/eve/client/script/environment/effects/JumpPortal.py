# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\JumpPortal.py
from eve.client.script.environment.effects.GenericEffect import ShipEffect

class JumpPortal(ShipEffect):
    __guid__ = 'effects.JumpPortal'

    def Start(self, duration):
        if self.gfx is None:
            raise RuntimeError('JumpPortal: no effect defined')
        self.PlayOldAnimations(self.gfx)
        return

    def Repeat(self, duration):
        if self.gfx is None:
            raise RuntimeError('JumpPortal: no effect defined')
        self.PlayOldAnimations(self.gfx)
        return


class JumpPortalBO(JumpPortal):
    __guid__ = 'effects.JumpPortalBO'