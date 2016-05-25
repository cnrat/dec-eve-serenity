# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\squadrons\squadronController.py
from carbonui.util.color import Color
from eve.client.script.ui.inflight.squadrons.shipFighterState import GetShipFighterState
from eve.common.script.mgt.fighterConst import LABEL_BY_STATE, COLOR_OPEN, COLOR_BY_STATE
import fighters
import gametime

class SquadronController(object):

    def __init__(self):
        self.shipFighterState = GetShipFighterState()
        self.michelle = sm.GetService('michelle')

    def GetSquadronVelocity(self, tubeFlagID):
        ball = self.GetSquadronBallInfo(tubeFlagID)
        if ball:
            velocity = ball.GetVectorDotAt(self.GetTimeNow()).Length()
            return velocity
        else:
            return None

    def GetSquadronDistance(self, tubeFlagID):
        ball = self.GetSquadronBallInfo(tubeFlagID)
        if ball:
            ball.GetVectorAt(self.GetTimeNow())
            return ball.surfaceDist
        else:
            return None

    def GetSquadronBallInfo(self, tubeFlagID):
        fightersItemID = self.GetFightersInSpaceItemID(tubeFlagID)
        if fightersItemID:
            ball = self.GetFightersBall(fightersItemID)
            return ball
        else:
            return None

    def GetFightersBall(self, fightersItemID):
        return self.michelle.GetBall(fightersItemID)

    def GetTimeNow(self):
        return gametime.GetSimTime()

    def GetFightersInSpaceItemID(self, tubeFlagID):
        fightersInSpace = self.shipFighterState.GetFightersInSpace(tubeFlagID)
        if fightersInSpace:
            return fightersInSpace.itemID
        else:
            return None

    def GetIsInSpace(self, tubeFlagID):
        fightersInSpace = self.shipFighterState.GetFightersInSpace(tubeFlagID)
        if fightersInSpace:
            return True
        return False

    def GetSquadronAction(self, tubeFlagID):
        tubeStatus = self.shipFighterState.GetTubeStatus(tubeFlagID)
        stateText = LABEL_BY_STATE[tubeStatus.statusID]
        if session.stationid2:
            stateColor = Color(*COLOR_OPEN)
        else:
            stateColor = Color(*COLOR_BY_STATE[tubeStatus.statusID])
        stateColor.a = 0.8
        return (stateText, stateColor)

    def GetAbilities(self, fighterTypeID):
        if fighterTypeID:
            abilities = fighters.IterTypeAbilities(fighterTypeID)
            return abilities

    def GetIncomingEwarEffects(self, fighterID):
        return self.shipFighterState.GetIncomingFighterEwar(fighterID)

    def GetSquadronHealth(self):
        pass