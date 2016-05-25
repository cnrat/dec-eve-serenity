# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\tacticalNavigation\tacticalNavigationService.py
import blue
import destiny
import carbon.common.script.sys.service as service
import uthread2
import navigationPoint
import tacticalNavigation.ui as tacitcalui
from ballparkFunctions import GetBall
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState

class FighterActionDisplay:

    def __init__(self):
        self.fighters = []
        self.targetConnectors = {}
        self.positionToNavPoint = {}
        self.ballIdToNavPoint = {}
        self.abilityTargets = {}
        self._updateThreadRunning = False
        self.shipFighterState = None
        return

    def _SetNavigationPoint(self, ball, globalPosition):
        ballId = ball.id
        if self._HasCorrectNavPoint(ballId, globalPosition):
            return self.ballIdToNavPoint[ballId]
        self._RemoveNavPointForBall(ballId)
        if globalPosition not in self.positionToNavPoint:
            navPoint = navigationPoint.NavigationPoint(globalPosition)
            self.positionToNavPoint[globalPosition] = navPoint
            sm.GetService('tactical').tacticalOverlay.RegisterNavBall(navPoint.GetNavBall())
        self.ballIdToNavPoint[ballId] = self.positionToNavPoint[globalPosition]
        self.ballIdToNavPoint[ballId].AddReferrer(ball)
        return self.ballIdToNavPoint[ballId]

    def _RemoveNavPointForBall(self, ballId):
        if ballId in self.ballIdToNavPoint:
            oldNavPoint = self.ballIdToNavPoint[ballId]
            oldNavPoint.RemoveReferrer(ballId)
            del self.ballIdToNavPoint[ballId]
            if not oldNavPoint.HasReferrers():
                sm.GetService('tactical').tacticalOverlay.UnregisterNavBall(oldNavPoint.GetNavBall())
                oldNavPoint.Destroy()
                del self.positionToNavPoint[oldNavPoint.globalPosition]

    def _HasCorrectNavPoint(self, ballId, globalPosition):
        if ballId in self.ballIdToNavPoint:
            oldNavPoint = self.ballIdToNavPoint[ballId]
            if oldNavPoint.globalPosition == globalPosition:
                return True
        return False

    def _ClearUIForFighter(self, fighterID):
        if fighterID in self.ballIdToNavPoint:
            self._RemoveNavPointForBall(fighterID)
        if fighterID in self.targetConnectors:
            self._RemoveMovementLine(fighterID)
        if fighterID in self.abilityTargets:
            for targetID in self.abilityTargets[fighterID]:
                connector = self.abilityTargets[fighterID][targetID]
                connector.Destroy()

            del self.abilityTargets[fighterID]

    def ClearAll(self):
        for fighterID in self.fighters:
            self._ClearUIForFighter(fighterID)

        self.positionToNavPoint = {}
        self.ballIdToNavPoint = {}
        self.abilityTargets = {}

    def _AddMovementLine(self, fighterBall, targetBallId):
        targetBall = GetBall(targetBallId)
        if targetBall is None:
            return
        else:
            if fighterBall.id in self.targetConnectors:
                self.targetConnectors[fighterBall.id].SetDestinationCurve(targetBall)
            else:
                connector = tacitcalui.CreateMovementConnector(fighterBall, targetBall)
                self.targetConnectors[fighterBall.id] = connector
            return

    def _RemoveMovementLine(self, fighterID):
        if fighterID in self.targetConnectors:
            connector = self.targetConnectors[fighterID]
            connector.Destroy()
            del self.targetConnectors[fighterID]

    def AddFighter(self, fighterID):
        if fighterID in self.fighters:
            return
        else:
            if self.shipFighterState is None:
                self.shipFighterState = GetShipFighterState()
                self.shipFighterState.ConnectFighterTargetUpdatedHandler(self._OnFighterTargetUpdate)
            self.fighters.append(fighterID)
            self._RebuildConnectorsForFighter(fighterID)
            if not self._updateThreadRunning:
                self._updateThreadRunning = True
                uthread2.StartTasklet(self._UpdateThread)
            return

    def _OnFighterTargetUpdate(self, fighterID, abilitySlotID, targetID):
        self._RebuildConnectorsForFighter(fighterID)

    def _RebuildConnectorsForFighter(self, fighterID):
        if fighterID not in self.abilityTargets:
            self.abilityTargets[fighterID] = {}
        fighterBall = GetBall(fighterID)
        if fighterBall is None:
            return
        else:
            targets = self.shipFighterState.GetAbilityTargetsForFighter(fighterID)
            for targetID in self.abilityTargets[fighterID]:
                connector = self.abilityTargets[fighterID][targetID]
                connector.Destroy()

            self.abilityTargets[fighterID] = {}
            for targetID in targets:
                targetBall = GetBall(targetID)
                if targetBall is not None:
                    connector = tacitcalui.CreateAgressionConnector(fighterBall, targetBall)
                    self.abilityTargets[fighterID][targetID] = connector

            self._UpdateFighter(fighterID)
            return

    def RemoveFighter(self, fighterID):
        self.fighters.remove(fighterID)
        self._ClearUIForFighter(fighterID)
        if len(self.fighters) == 0:
            self._updateThreadRunning = False

    def _GetMode(self, ball):
        mode = None
        if ball.mode == destiny.DSTBALL_GOTO:
            mode = destiny.DSTBALL_GOTO
        elif ball.followId != 0:
            mode = destiny.DSTBALL_FOLLOW
        return mode

    def _UpdateFighter(self, fighterID):
        ball = GetBall(fighterID)
        if ball is None:
            self._ClearUIForFighter(fighterID)
            return
        else:
            followBall = None
            mode = self._GetMode(ball)
            if mode == destiny.DSTBALL_FOLLOW:
                followBall = GetBall(ball.followId)
                self._RemoveNavPointForBall(fighterID)
            elif mode == destiny.DSTBALL_GOTO:
                globalPosition = (ball.gotoX, ball.gotoY, ball.gotoZ)
                followBall = self._SetNavigationPoint(ball, globalPosition).GetNavBall()
            else:
                self._RemoveNavPointForBall(fighterID)
            if followBall is None:
                self._RemoveMovementLine(fighterID)
            elif fighterID in self.abilityTargets and followBall.id in self.abilityTargets[fighterID]:
                self._RemoveMovementLine(fighterID)
            else:
                self._AddMovementLine(ball, followBall.id)
            return

    def _UpdateThread(self):
        while self._updateThreadRunning:
            for each in self.fighters:
                self._UpdateFighter(each)

            blue.synchro.SleepSim(500)


class TacticalNavigationService(service.Service):
    __guid__ = 'svc.tacticalNavigation'
    __servicename__ = 'tacticalNavigationService'
    __displayname__ = 'Tactical Navigation Service'
    __notifyevents__ = ['OnFighterAddedToController', 'OnFighterRemovedFromController', 'OnSessionChanged']
    __dependencies__ = ['michelle', 'fighters']
    __startupdependencies__ = []

    def Run(self, *args):
        service.Service.Run(self, *args)
        self._fighterActionDisplay = FighterActionDisplay()
        self._ReloadFighters()

    def _ReloadFighters(self):
        if not (session.shipid and session.solarsystemid2):
            return
        self._fighterActionDisplay.ClearAll()
        _, fighterIDs = self.fighters.GetFightersForShip()
        for fighterID in fighterIDs:
            self._fighterActionDisplay.AddFighter(fighterID)

    def OnSessionChanged(self, isremote, session, change):
        if 'shipid' not in change:
            return
        self._ReloadFighters()

    def OnFighterAddedToController(self, fighterID, fighterTypeID, tubeFlagID, squadronSize, abilitySlotStates):
        self._fighterActionDisplay.AddFighter(fighterID)

    def OnFighterRemovedFromController(self, fighterID, tubeFlagID):
        self._fighterActionDisplay.RemoveFighter(fighterID)