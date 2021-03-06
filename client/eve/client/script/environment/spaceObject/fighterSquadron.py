# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\spaceObject\fighterSquadron.py
import trinity
import Drone
import evegraphics.settings as gfxsettings
from ExplosionManager import ExplosionManager
from fighters.client import GetSquadronSizeFromSlimItem
from fighters import GetTurretGraphicIDsForFighter
import eve.client.script.environment.model.turretSet as turretSet

class FighterSquadronError(Exception):
    pass


class FighterSquadron(Drone.Drone):

    def __init__(self):
        Drone.Drone.__init__(self)
        self.squadronSize = 0

    def Assemble(self):
        if not self.IsDroneModelEnabled():
            return
        else:
            self.FitBoosters(alwaysOn=False)
            self.SetupAmbientAudio()
            self.model.EnableSwarming(True)
            self.squadronSize = GetSquadronSizeFromSlimItem(self.typeData['slimItem'])
            if self.squadronSize is None:
                self.squadronSize = 1
            self.model.SetCount(self.squadronSize)
            return

    def FitHardpoints(self, blocking=False):
        if self.fitted:
            return
        elif self.model is None:
            self.LogWarn('FitHardpoints - No model')
            return
        else:
            self.fitted = True
            if not gfxsettings.Get(gfxsettings.UI_TURRETS_ENABLED):
                return
            slotIDtoGraphicID = GetTurretGraphicIDsForFighter(self.GetTypeID())
            for slotID, graphicID in slotIDtoGraphicID.iteritems():
                ts = turretSet.TurretSet.AddTurretToModel(self.model, graphicID)
                if ts is not None and self.modules is not None:
                    self.modules[slotID] = ts

            return

    def SpawnClientBall(self, position):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        else:
            egopos = bp.GetCurrentEgoPos()
            explosionPosition = (position[0] + egopos[0], position[1] + egopos[1], position[2] + egopos[2])
            return bp.AddClientSideBall(explosionPosition)

    def DestroyClientBall(self, ball):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is not None and ball.ballpark is not None:
            bp.RemoveBall(ball.id)
        return

    def _ClearExplosion(self, model):
        if model is None:
            return
        else:
            if model.translationCurve is not None:
                self.DestroyClientBall(model.translationCurve)
                model.translationCurve = None
            scene = sm.StartService('sceneManager').GetRegisteredScene('default')
            scene.objects.fremove(model)
            return

    def SpawnExplosion(self, position):
        path, (delay, scale) = self.GetExplosionInfo()
        ball = self.SpawnClientBall(position)
        em = ExplosionManager()
        gfx = em.GetExplosion(path, scale, callback=self._ClearExplosion)
        gfx.translationCurve = ball
        scene = sm.StartService('sceneManager').GetRegisteredScene('default')
        scene.objects.append(gfx)

    def DestroyFighter(self):
        if self.model is None:
            return
        elif not self.IsDroneModelEnabled():
            return
        else:
            try:
                position = self.model.RemoveSwarmer()
                self.SpawnExplosion(position)
            except:
                self._RaiseFighterException('DestroyFighter failed!')

            return

    def OnSlimItemUpdated(self, slimItem):
        if self.model is None:
            return
        elif not self.IsDroneModelEnabled():
            return
        else:
            newSquadronSize = GetSquadronSizeFromSlimItem(slimItem)
            if newSquadronSize > self.squadronSize:
                self.model.SetCount(newSquadronSize)
            else:
                for i in range(self.squadronSize - newSquadronSize):
                    self.DestroyFighter()

            self.squadronSize = newSquadronSize
            return

    def Explode(self):
        if not self.IsDroneModelEnabled() or not gfxsettings.Get(gfxsettings.UI_EXPLOSION_EFFECTS_ENABLED):
            return False
        if self.exploded:
            return
        while self.squadronSize > 0:
            self.DestroyFighter()
            self.squadronSize -= 1

        self.exploded = True
        return False

    def _RaiseFighterException(self, header=''):
        message = header + '\n'
        message += 'typeID: ' + str(self.typeData.get('typeID', 'None')) + '\n'
        message += 'bluetype: ' + getattr(self.model, '__bluetype__', 'None')
        raise FighterSquadronError(message)

    def PrepareForFiring(self):
        if self.model is None:
            return
        elif not self.IsDroneModelEnabled():
            return
        else:
            try:
                self.model.PickFiringOrigin()
            except:
                self._RaiseFighterException('PickFiringOrigin failed!')

            return

    def GetPositionCurve(self):
        if self.model is None:
            return self
        else:
            curve = trinity.EveLocalPositionCurve()
            curve.parent = self.model
            curve.behavior = trinity.EveLocalPositionBehavior.centerBounds
            return curve