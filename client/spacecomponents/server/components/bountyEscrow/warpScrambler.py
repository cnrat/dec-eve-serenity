# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\server\components\bountyEscrow\warpScrambler.py
import uthread2
import logging
import dogma.const as dgmconst
from eveexceptions import UserError
logger = logging.getLogger(__name__)

class WarpScrambler(object):

    def __init__(self, bountyEscrowID, lock, dogmaLM):
        self.bountyEscrowID = bountyEscrowID
        self.scrambledShipID = None
        self.scramblingShipThread = None
        lock.RegisterForUnlockEvents(self.OnUnlocking)
        lock.RegisterForPossiblyLockEvents(self.OnLocking)
        self.dogmaLM = dogmaLM
        return

    def _UnscrambleShip(self, shipID):
        self.dogmaLM.RemoveTarget(self.bountyEscrowID, shipID)
        self.dogmaLM.StopEffect(dgmconst.effectEssWarpScramble, self.bountyEscrowID, forced=True)
        self.dogmaLM.RemoveTarget(self.bountyEscrowID, shipID)
        self.scrambledShipID = None
        return

    def OnLocking(self, charID, shipID, reason):
        if self.scramblingShipThread:
            self.scramblingShipThread.Kill()
            self.scramblingShipThread = None
            self.scrambledShipID = None
            return
        elif self.scrambledShipID is None:
            return
        else:
            self._UnscrambleShip(shipID)
            return

    def _LockTarget(self, shipID):
        for i in xrange(20):
            try:
                self.dogmaLM.AddTargetEx(self.bountyEscrowID, shipID, countBias=1, silent=1)
                break
            except UserError as e:
                logger.debug('Failed getting a lock because of %s will try again in 1 second', e.msg)

            uthread2.Sleep(1)
        else:
            logger.error('Failed getting a lock in time ')
            return False

        return True

    def _ScrambleShip(self, shipID):
        try:
            if self._LockTarget(shipID):
                self.dogmaLM.ActivateWithContext(None, self.bountyEscrowID, dgmconst.effectEssWarpScramble, repeat=1000, targetid=shipID)
                self.scrambledShipID = shipID
        finally:
            self.scramblingShipThread = None

        return

    def OnUnlocking(self, charID, shipID):
        if self.scrambledShipID is not None:
            if self.scrambledShipID == shipID:
                return
            self._UnscrambleShip(self.scrambledShipID)
        self.scramblingShipThread = uthread2.StartTasklet(self._ScrambleShip, shipID)
        return