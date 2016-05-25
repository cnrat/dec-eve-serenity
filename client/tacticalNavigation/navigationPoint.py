# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\tacticalNavigation\navigationPoint.py
import navigationBracket
import tacticalNavigation.ui as tacticalui
from ballparkFunctions import AddClientBall, RemoveClientBall

class NavigationPoint:

    def __init__(self, globalPosition):
        self.globalPosition = globalPosition
        self.clientBall = AddClientBall(globalPosition)
        self.bracket = navigationBracket.NavigationPointBracket.Create(self.clientBall)
        self.referrers = []
        self.connectors = {}

    def GetNavBall(self):
        return self.clientBall

    def AddReferrer(self, ball):
        self.referrers.append(ball.id)
        connector = tacticalui.CreateMovementConnector(ball, self.clientBall)
        self.connectors[ball.id] = connector

    def RemoveReferrer(self, ballId):
        self.referrers.remove(ballId)
        self.connectors[ballId].Destroy()
        del self.connectors[ballId]

    def HasReferrers(self):
        return len(self.referrers) > 0

    def Destroy(self):
        self.bracket.Close()
        RemoveClientBall(self.clientBall)