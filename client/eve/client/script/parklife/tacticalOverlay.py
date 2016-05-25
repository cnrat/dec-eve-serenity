# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\tacticalOverlay.py
import states as state
import tacticalNavigation.tacticalCompass as tacticalCompass
import tacticalNavigation.ui as tacticalUI
import tacticalNavigation.ballparkFunctions as ballpark

class TacticalOverlay:
    _interestStates = [state.targeting,
     state.targeted,
     state.mouseOver,
     state.selected]

    def __init__(self, tactical):
        self.tactical = tactical
        self.useNewOverlay = True
        self.tacticalCompass = None
        self.initialized = False
        self.selectedID = None
        self.selectedConnector = None
        self.rootPosition = None
        self.navBalls = []
        self._ballInterests = {}
        return

    def Initialize(self):
        if self.initialized:
            return
        self.tacticalCompass = tacticalCompass.TacticalCompass()
        self.InitConnectors()
        self.initialized = True
        self.UpdateTargetingRanges()
        self.OnShipChange()

    def EnableMoveMode(self, curve):
        if not self.initialized:
            return
        else:
            self.tacticalCompass.SetMoveMode(True, curve)
            ego = ballpark.GetBall(session.shipid)
            if ego is not None:
                self.AddConnector(ego)
            return

    def DisableMoveMode(self):
        if not self.initialized:
            return
        else:
            ego = ballpark.GetBall(session.shipid)
            if ego is not None:
                self.RemoveConnector(ego)
            self.tacticalCompass.SetMoveMode(False, ego)
            return

    def RegisterNavBall(self, ball):
        if ball not in self.navBalls:
            self.navBalls.append(ball)
            self.AddConnector(ball)

    def UnregisterNavBall(self, ball):
        if ball in self.navBalls:
            self.navBalls.remove(ball)
            self.RemoveConnector(ball.id)

    def TearDown(self):
        if self.initialized:
            self.tacticalCompass.ClearAll()
        self._ClearSelection()
        self.tacticalCompass = None
        self.initialized = False
        return

    def AddConnector(self, ball):
        if self.initialized:
            self.tacticalCompass.AddConnector(ball)

    def RemoveConnector(self, ballID):
        if not self.initialized:
            return
        self.tacticalCompass.RemoveConnector(ballID)
        if ballID == self.selectedID:
            self._ClearSelection()
        self._ClearInterest(ballID)

    def _UpdateInterest(self, ballID, state, flag):
        if ballID not in self._ballInterests:
            if flag:
                self._ballInterests[ballID] = set([state])
            return
        if not flag and state in self._ballInterests[ballID]:
            self._ballInterests[ballID].remove(state)
        if flag and state not in self._ballInterests[ballID]:
            self._ballInterests[ballID].add(state)

    def _ClearInterest(self, ballID):
        if ballID in self._ballInterests:
            del self._ballInterests[ballID]

    def _IsInteresting(self, ballID):
        return ballID in self._ballInterests and len(self._ballInterests[ballID]) > 0

    def CheckInterest(self, ballID, state, flag):
        if state not in self._interestStates:
            return
        elif not self.initialized:
            return
        elif ballID == session.shipid:
            return
        else:
            self._UpdateInterest(ballID, state, flag)
            if self._IsInteresting(ballID):
                ball = ballpark.GetBall(ballID)
                if ball is None:
                    return
                self.AddConnector(ball)
            else:
                self._ClearInterest(ballID)
                bp = ballpark.GetBallpark()
                if bp is None:
                    return
                slimItem = bp.GetInvItem(ballID)
                filtered = self.tactical.GetFilteredStatesFunctionNames()
                alwaysShown = self.tactical.GetAlwaysShownStatesFunctionNames()
                if not self.tactical.WantIt(slimItem, filtered, alwaysShown):
                    self.RemoveConnector(ballID)
            return

    def InitConnectors(self):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return
        else:
            self.tacticalCompass.ClearConnectors()
            selected = None
            filtered = self.tactical.GetFilteredStatesFunctionNames()
            alwaysShown = self.tactical.GetAlwaysShownStatesFunctionNames()
            for itemID, ball in ballpark.balls.items():
                if itemID < 0 or itemID == eve.session.shipid:
                    continue
                if ballpark is None:
                    break
                slimItem = ballpark.GetInvItem(itemID)
                if slimItem and self.tactical.WantIt(slimItem, filtered, alwaysShown):
                    self.tacticalCompass.AddConnector(ball)
                interestStates = sm.GetService('state').GetStates(itemID, self._interestStates)
                for intrState in interestStates:
                    self.CheckInterest(itemID, intrState, True)
                    if intrState == state.selected:
                        selected = itemID

            for ball in self.navBalls:
                self.tacticalCompass.AddConnector(ball)

            if selected:
                self.ShowDirectionTo(selected)
            return

    def _ClearSelection(self):
        if self.selectedConnector is not None:
            self.selectedConnector.Destroy()
            self.selectedConnector = None
        self.selectedID = None
        return

    def ShowDirectionTo(self, ballID):
        if self.selectedID == ballID:
            return
        else:
            self._ClearSelection()
            targetBall = ballpark.GetBall(ballID)
            if targetBall is None:
                return
            self.selectedConnector = tacticalUI.CreateStraightConnector(tacticalUI.STYLE_FAINT, tacticalUI.COLOR_GENERIC, None, targetBall)
            self.selectedID = ballID
            return

    def OnShipChange(self):
        if not self.initialized:
            return
        ball = ballpark.GetBall(session.shipid)
        self.tacticalCompass.SetRootBall(ball)
        self.UpdateTargetingRanges()

    def UpdateTargetingRanges(self, module=None, charge=None):
        if not self.initialized:
            return
        else:
            self.tacticalCompass.HideBombRange()
            if not session.shipid:
                self.tacticalCompass.compassDisc.HideFiringRange()
                return
            ship = sm.GetService('godma').GetItem(session.shipid)
            self.tacticalCompass.SetTargetingRange(ship.maxTargetRange)
            if module is None:
                self.tacticalCompass.compassDisc.HideFiringRange()
                return
            maxRange, falloff, bombRadius = self.tactical.FindMaxRange(module, charge)
            if not bombRadius:
                self.tacticalCompass.SetFiringRange(maxRange, falloff)
                return
            self.tacticalCompass.compassDisc.HideFiringRange()
            ball = ballpark.GetBall(session.shipid)
            self.tacticalCompass.ShowBombRange(bombRadius, maxRange, ball)
            return

    def SetFixedRange(self, range):
        self.tacticalCompass.SetFixedRange(range)