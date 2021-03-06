# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\DeployableSpaceObject.py
import blue
from eve.client.script.environment.spaceObject.spaceObject import SpaceObject
from eve.client.script.environment.model.turretSet import TurretSet
import evegraphics.settings as gfxsettings
import eve.common.lib.appConst as const
from spacecomponents.client.messages import MSG_ON_ACTIVATE_TIMER_UPDATED
from spacecomponents.common.helper import IsActiveComponent
TURRET_TYPE_ID = {const.groupAutoLooter: 24348}

class DeployableSpaceObject(SpaceObject):

    def __init__(self):
        SpaceObject.__init__(self)
        self.modules = {}
        self.fitted = False

    def Assemble(self):
        if self.ballpark is None:
            return
        else:
            registry = self._GetComponentRegistry()
            if not IsActiveComponent(registry, self.typeID, self.id):
                self.TriggerAnimation('idle')
                registry.SubscribeToItemMessage(self.id, MSG_ON_ACTIVATE_TIMER_UPDATED, self.ActivateTimerUpdate)
            else:
                self.TriggerAnimation('active')
            if gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
                self.FitHardpoints()
            self.SetupSharedAmbientAudio()
            return

    def ActivateTimerUpdate(self, component, slimItem):
        if component.isActive:
            self.TriggerAnimation('active')

    def FitHardpoints(self, blocking=False):
        if self.fitted:
            return
        elif self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return
        elif self.typeID is None:
            self.LogWarn('FitHardpoints - No typeID')
            return
        else:
            self.fitted = True
            self.modules = {}
            groupID = self.typeData.get('groupID', None)
            if groupID is not None:
                turretTypeID = TURRET_TYPE_ID.get(groupID, None)
                if turretTypeID is not None:
                    ts = TurretSet.FitTurret(self.model, turretTypeID, 1, self.typeData.get('sofFactionName', None))
                    if ts is not None:
                        self.modules[self.id] = ts
            return

    def LookAtMe(self):
        if not self.model:
            return
        if not self.fitted:
            self.FitHardpoints()

    def Release(self):
        if self.released:
            return
        else:
            self.modules = None
            SpaceObject.Release(self)
            return

    def Explode(self, explosionURL=None, scaling=1.0, managed=False, delay=0.0):
        explosionPath, (delay, scaling) = self.GetExplosionInfo()
        if not self.exploded:
            self.sm.ScatterEvent('OnShipExplode', self.GetModel())
        return SpaceObject.Explode(self, explosionURL=explosionPath, managed=True, delay=delay, scaling=scaling)