# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\structures.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect

class StructureOffline(GenericEffect):
    __guid__ = 'effects.StructureOffline'

    def __init__(self, trigger, *args):
        if trigger.moduleID is not None and trigger.moduleID != trigger.shipID:
            self.ballIDs = [trigger.moduleID]
        else:
            self.ballIDs = [trigger.shipID]
        self.fxSequencer = sm.GetService('FxSequencer')
        self.gfx = None
        return

    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if ball is None:
            return
        else:
            if hasattr(ball, 'OfflineAnimation'):
                ball.OfflineAnimation(1)
            return


class StructureOnlined(GenericEffect):
    __guid__ = 'effects.StructureOnlined'

    def __init__(self, trigger, *args):
        if trigger.moduleID is not None and trigger.moduleID != trigger.shipID:
            self.ballIDs = [trigger.moduleID]
        else:
            self.ballIDs = [trigger.shipID]
        self.fxSequencer = sm.GetService('FxSequencer')
        self.gfx = None
        return

    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if ball is None:
            return
        else:
            if hasattr(ball, 'OnlineAnimation'):
                ball.OnlineAnimation(1)
            return


class StructureOnline(GenericEffect):
    __guid__ = 'effects.StructureOnline'

    def __init__(self, trigger, *args):
        if trigger.moduleID is not None and trigger.moduleID != trigger.shipID:
            self.ballIDs = [trigger.moduleID]
        else:
            self.ballIDs = [trigger.shipID]
        self.fxSequencer = sm.GetService('FxSequencer')
        self.gfx = None
        return

    def Start(self, duration):
        ballID = self.ballIDs[0]
        ball = self.fxSequencer.GetBall(ballID)
        if ball is None:
            return
        else:
            if hasattr(ball, 'OnlineAnimation'):
                ball.OnlineAnimation(1)
            return