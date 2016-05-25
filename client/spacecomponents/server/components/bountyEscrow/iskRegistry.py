# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\bountyEscrow\iskRegistry.py
from collections import defaultdict

class IskRegistry(object):

    def __init__(self, initialBounties):
        self.bounties = defaultdict(float)
        self.bounties.update(initialBounties)
        self.listener = None
        return

    def RegisterIsk(self, charID, amount):
        self.bounties[charID] += amount
        if self.listener is not None:
            self.listener(charID, amount)
        return

    def GetBountyAmount(self):
        return sum(self.bounties.itervalues())

    def GetIskContributors(self):
        return self.bounties

    def ClearIsk(self):
        self.bounties.clear()

    def RegisterForRegisterIskEvents(self, func):
        self.listener = func