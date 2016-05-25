# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\positionalControl.py
import blue
import uthread2
import tacticalNavigation.controlPaths as controlPaths
from evegraphics.wrappers.vectorFunctions import AverageVectorFunction
from eve.client.script.ui.services.menuSvcExtras.movementFunctions import GetSelectedShipAndFighters, GoToPoint
_SW_CYLINDER = 1
_SW_SLICE = 2
_SW_CONE = 3
_SW_PROJECTED_SPHERE = 4

class PositionalControl:
    __notifyevents__ = ['OnBallparkCall']

    def __init__(self):
        self._cameraController = None
        self._currentPath = None
        self._activeIDs = []
        self._finalizeFunction = None
        self._updateRunning = False
        self._moduleID = None
        self._effectID = None
        self._isMoving = False
        sm.RegisterNotify(self)
        return

    def IsActive(self):
        return self._currentPath is not None

    def IsFirstPointSet(self):
        if self._currentPath:
            return self._currentPath.IsFirstPointSet()
        else:
            return False

    def OnSceneMouseExit(self):
        if self.IsMoveCommandActive() and not self.IsFirstPointSet():
            self.AbortCommand()

    def IsMoveCommandActive(self):
        return self._finalizeFunction == self._MoveSelected

    def SetCameraController(self, cameraController):
        self._cameraController = cameraController
        if self._currentPath is None:
            self.AbortCommand()
        return

    def AbortCommand(self, *args):
        if self._currentPath is not None:
            self._currentPath.Abort()
        self._currentPath = None
        self._activeIDs = []
        self._finalizeFunction = None
        self._EnableUpdate(False)
        if self._isMoving:
            overlay = sm.GetService('tactical').GetOverlay()
            overlay.DisableMoveMode()
            self._isMoving = False
        return

    def _GetMoveOrigin(self, activeIDs):
        lookAtID = self._cameraController.GetCamera().GetLookAtItemID()
        if lookAtID == session.shipid:
            return
        balls = []
        michelle = sm.GetService('michelle')
        for fighterID in activeIDs:
            ball = michelle.GetBall(fighterID)
            if ball is not None:
                balls.append(ball)

        if len(balls) == 0:
            return
        elif len(balls) == 1:
            return balls[0]
        else:
            return AverageVectorFunction(balls).GetBlueFunction()

    def StartMoveCommand(self):
        activeIDs = []
        shipSelected, fighterIDs = GetSelectedShipAndFighters()
        if shipSelected:
            activeIDs.append(session.shipid)
        activeIDs.extend(fighterIDs)
        if len(activeIDs) < 1:
            return
        else:
            if self._currentPath is not None:
                self._currentPath.Abort()
            originCurve = self._GetMoveOrigin(activeIDs)
            self._currentPath = controlPaths.SinglePointPath()
            self._currentPath.Start(originCurve)
            overlay = sm.GetService('tactical').GetOverlay()
            overlay.EnableMoveMode(originCurve)
            self._isMoving = True
            self._finalizeFunction = self._MoveSelected
            self._EnableUpdate(True)
            return

    def _StartTargetedEffect(self):
        destination = self._currentPath.GetEndPosition()
        sm.GetService('areaWeapon').ActivateSinglePointTargetedModule(self._moduleID, self._effectID, destination)

    def _StartSlasherEffect(self):
        p0, p1 = self._currentPath.GetPath()
        areaWeapon = sm.GetService('areaWeapon')
        areaWeapon.SetTargetingOffsets(p0, p1)
        areaWeapon.FireAreaWeaponOnServer(self._moduleID)

    def _GetModuleBehavior(self, moduleItem):
        areaIndicator = None
        doomsdayAOEShape = getattr(moduleItem, 'doomsdayAOEShape', None)
        maxRange = getattr(moduleItem, 'maxRange', None)
        fixedRange = getattr(moduleItem, 'doomsdayRangeIsFixed', False)
        aoeRange = getattr(moduleItem, 'doomsdayAOERange', None)
        damageRadius = getattr(moduleItem, 'doomsdayDamageRadius', None)
        if doomsdayAOEShape == _SW_PROJECTED_SPHERE:
            areaIndicator = controlPaths.SphereAreaIndication(aoeRange)
        elif doomsdayAOEShape == _SW_SLICE:
            areaIndicator = controlPaths.SliceAreaIndication(damageRadius)
        elif doomsdayAOEShape == _SW_CONE:
            areaIndicator = controlPaths.ConeAreaIndication()
        elif doomsdayAOEShape == _SW_CYLINDER:
            areaIndicator = controlPaths.CylinderAreaIndication(damageRadius)
        return (fixedRange, maxRange, areaIndicator)

    def StartEffectTargeting(self, sourceID, moduleID, effect, targetPointCount):
        if self._currentPath is not None:
            self._currentPath.Abort()
        self._moduleID = moduleID
        self._effectID = effect.effectID
        michelle = sm.GetService('michelle')
        ball = michelle.GetBall(sourceID)
        radius = getattr(ball, 'radius', 0)
        if targetPointCount == 2.0:
            self._currentPath = controlPaths.ArcPath(baseDistance=radius)
            self._finalizeFunction = self._StartSlasherEffect
        else:
            self._currentPath = controlPaths.SinglePointPath(agressive=True, baseDistance=radius)
            self._finalizeFunction = self._StartTargetedEffect
        module = sm.GetService('godma').GetItem(moduleID)
        fixedRange, moduleRange, areaIndicator = self._GetModuleBehavior(module)
        if moduleRange is not None:
            self._currentPath.SetMaxDistance(moduleRange)
        self._currentPath.SetFixedDistance(fixedRange)
        self._currentPath.Start(ball, areaIndicator)
        self._activeIDs = [sourceID]
        self._EnableUpdate(True)
        return

    def _StartFighterAbilites(self):
        selectedPoint = self._ConvertPositionToGlobalSpace(self._currentPath.GetEndPosition())
        sm.GetService('fighters').ActivateAbilitySlotsAtPoint(self._activeIDs, self._abilitySlotID, selectedPoint)

    def StartFighterAbilityTargeting(self, fighterIDs, abiltySlotID):
        if len(fighterIDs) < 1:
            return
        else:
            if self._currentPath is not None:
                self._currentPath.Abort()
            originCurve = self._GetMoveOrigin(fighterIDs)
            self._currentPath = controlPaths.SinglePointPath()
            self._currentPath.Start(originCurve)
            self._abilitySlotID = abiltySlotID
            self._activeIDs = fighterIDs
            self._finalizeFunction = self._StartFighterAbilites
            self._EnableUpdate(True)
            return

    def _EnableUpdate(self, enable):
        if enable and not self._updateRunning:
            uthread2.StartTasklet(self._UpdateThread)
        self._updateRunning = enable

    def _Finalize(self):
        try:
            self._finalizeFunction()
        finally:
            self.AbortCommand()

    def _ConvertPositionToGlobalSpace(self, position):
        bp = sm.GetService('michelle').GetBallpark()
        if bp is None:
            return
        else:
            egopos = bp.GetCurrentEgoPos()
            destination = (position[0] + egopos[0], position[1] + egopos[1], position[2] + egopos[2])
            return destination

    def _MoveSelected(self):
        destination = self._ConvertPositionToGlobalSpace(self._currentPath.GetEndPosition())
        if destination is None:
            return
        else:
            GoToPoint(destination)
            return

    def AddPoint(self):
        if self._currentPath is None or self._cameraController is None:
            return
        else:
            self._currentPath.UpdatePosition(self._cameraController)
            self._currentPath.AddPoint()
            sm.GetService('audio').SendUIEvent('msg_ComboEntryEnter_play')
            if self._currentPath.IsComplete():
                uthread2.StartTasklet(self._Finalize)
            return

    def _UpdateThread(self):
        while self._updateRunning:
            if self._currentPath is not None and self._cameraController is not None:
                self._currentPath.UpdatePosition(self._cameraController)
            blue.synchro.Yield()

        return

    def OnBallparkCall(self, functionName, callArgument, **kwargs):
        if functionName in ('WarpTo',):
            self.AbortCommand()

    def OnSessionChanged(self, isremote, session, change):
        self.AbortCommand()