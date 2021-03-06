# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\turrets.py
from eve.client.script.environment.effects.GenericEffect import GenericEffect, STOP_REASON_DEFAULT
from fighters import ABILITY_SLOT_ID_KEY
import evegraphics.settings as gfxsettings
import uthread

class StandardWeapon(GenericEffect):
    __guid__ = 'effects.StandardWeapon'

    def __init__(self, trigger, *args):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None
        if trigger.graphicInfo is not None and ABILITY_SLOT_ID_KEY in trigger.graphicInfo:
            self.moduleID = trigger.graphicInfo[ABILITY_SLOT_ID_KEY]
        else:
            self.moduleID = trigger.moduleID
        self.otherTypeID = trigger.otherTypeID
        self.fxSequencer = sm.GetService('FxSequencer')
        return

    def Prepare(self):
        pass

    def Shoot(self, shipBall, targetBall):
        if getattr(self, 'turret', None) is not None:
            self.turret.SetTarget(shipBall, targetBall)
            self.turret.StartShooting()
        return

    def Start(self, duration):
        if not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return
        else:
            shipID = self.ballIDs[0]
            shipBall = self.fxSequencer.GetBall(shipID)
            targetID = self.ballIDs[1]
            targetBall = self.fxSequencer.GetBall(targetID)
            if targetBall is None:
                return
            if shipBall is None:
                return
            if not hasattr(shipBall, 'fitted'):
                self.fxSequencer.LogError(self.__guid__ + str(shipBall.id) + ' Turrets: Error! can not fit turrets. No fitted attribute ')
                return
            shipBall.FitHardpoints(blocking=True)
            if not shipBall.fitted:
                return
            if shipBall.modules is None:
                return
            shipBall.PrepareForFiring()
            self.turret = shipBall.modules.get(self.moduleID)
            if not self.turret:
                self.fxSequencer.LogError('StandardWeapon: Turret not fitted on shipID', shipID)
                return
            if hasattr(self.turret, 'SetAmmoColor'):
                self.SetAmmoColor()
            uthread.worker('FxSequencer::ShootTurrets', self.Shoot, shipID, targetID)
            return

    def SetAmmoColor(self):
        if self.otherTypeID is not None:
            self.turret.SetAmmoColorByTypeID(self.otherTypeID)
        return

    def Stop(self, reason=STOP_REASON_DEFAULT):
        if getattr(self, 'turret', None) is None:
            return
        else:
            self.turret.StopShooting()
            self.turret.shooting = 0
            self.turret = None
            return

    def Repeat(self, duration):
        if getattr(self, 'turret', None) is None:
            return
        else:
            shipID = self.ballIDs[0]
            shipBall = self.fxSequencer.GetBall(shipID)
            targetID = self.ballIDs[1]
            targetBall = self.fxSequencer.GetBall(targetID)
            if targetBall is None:
                self.turret.Rest()
                self.turret.shooting = 0
                return
            if shipBall is None:
                self.turret.Rest()
                self.turret.shooting = 0
                return
            shipBall.PrepareForFiring()
            uthread.worker('FxSequencer::ShootTurrets', self.Shoot, shipID, targetID)
            return


class CloudMining(StandardWeapon):
    __guid__ = 'effects.CloudMining'

    def SetAmmoColor(self):
        targetBall = self.GetEffectTargetBall()
        targetModel = getattr(targetBall, 'model', None)
        color = (1.0, 1.0, 1.0, 1.0)
        emitters = targetModel.Find('trinity.EveEmitterStatic')
        if len(emitters):
            if len(emitters[0].particleData):
                color = emitters[0].particleData[0].color
        self.turret.SetAmmoColor(color)
        return


class MissileLaunch(GenericEffect):
    __guid__ = 'effects.MissileLaunch'

    def __init__(self, trigger, *args):
        self.ballIDs = [trigger.shipID, trigger.targetID]
        self.gfx = None
        self.gfxModel = None
        self.moduleID = trigger.moduleID
        self.otherTypeID = trigger.otherTypeID
        self.fxSequencer = sm.GetService('FxSequencer')
        return

    def Prepare(self):
        pass

    def Shoot(self, shipBall, targetBall):
        if getattr(self, 'turret', None) is not None:
            self.turret.SetTarget(shipBall, targetBall)
        return

    def Start(self, duration):
        if not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
            return
        else:
            shipID = self.ballIDs[0]
            shipBall = self.fxSequencer.GetBall(shipID)
            targetID = self.ballIDs[1]
            targetBall = self.fxSequencer.GetBall(targetID)
            if targetBall is None:
                return
            if shipBall is None:
                return
            if shipBall == targetBall:
                return
            if not hasattr(shipBall, 'fitted'):
                return
            shipBall.FitHardpoints(blocking=True)
            if not shipBall.fitted:
                return
            if shipBall.modules is None:
                return
            self.turret = shipBall.modules.get(self.moduleID)
            if not self.turret:
                self.turret = shipBall.modules.get(0)
                if not self.turret:
                    self.fxSequencer.LogError('MissileLaunch: Turret not fitted on shipID', shipID, self.moduleID)
                    return
            uthread.worker('FxSequencer::ShootTurrets', self.Shoot, shipID, targetID)
            return

    def SetAmmoColor(self):
        pass

    def Stop(self, reason=STOP_REASON_DEFAULT):
        if getattr(self, 'turret', None) is None:
            return
        else:
            self.turret.StopShooting()
            self.turret.shooting = 0
            self.turret = None
            return

    def Repeat(self, duration):
        if getattr(self, 'turret', None) is None:
            return
        else:
            shipID = self.ballIDs[0]
            shipBall = self.fxSequencer.GetBall(shipID)
            targetID = self.ballIDs[1]
            targetBall = self.fxSequencer.GetBall(targetID)
            if targetBall is None:
                self.turret.Rest()
                self.turret.shooting = 0
                return
            if shipBall is None:
                self.turret.Rest()
                self.turret.shooting = 0
                return
            if shipBall == targetBall:
                return
            uthread.worker('FxSequencer::ShootTurrets', self.Shoot, shipID, targetID)
            return