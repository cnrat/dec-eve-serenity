# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\planet\entities\extractorPin.py
import const
from eve.common.script.planet.entities.basePin import BasePin
from eve.common.script.planet.entities.basePin import STATE_ACTIVE, STATE_IDLE
import math
import blue
EXTRACTOR_MAX_CYCLES = 120

class ExtractorPin(BasePin):
    __guid__ = 'planet.ExtractorPin'
    __slots__ = ['products',
     'depositType',
     'depositQtyPerCycle',
     'depositQtyRemaining',
     'depositExpiryTime',
     'cycleTime',
     'installTime']

    def __init__(self, typeID):
        BasePin.__init__(self, typeID)
        self.products = {}
        self.depositType = None
        self.depositQtyPerCycle = 0
        self.depositQtyRemaining = 0
        self.depositExpiryTime = None
        self.cycleTime = None
        self.installTime = None
        return

    def GetCycleTime(self):
        return self.cycleTime

    def GetBaseCycleTime(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributePinCycleTime)

    def GetBaseExtractionQty(self):
        return self.eventHandler.GetTypeAttribute(self.typeID, const.attributePinExtractionQuantity)

    def CanAccept(self, typeID, quantity):
        pass

    def AddCommodity(self, typeID, quantity):
        pass

    def Run(self, runTime):
        self.lastRunTime = runTime
        if self.depositType is None:
            return {}
        else:
            products = {}
            if self.IsActive():
                products[self.depositType] = self.depositQtyPerCycle if self.depositQtyPerCycle < self.depositQtyRemaining else self.depositQtyRemaining
                self.depositQtyRemaining -= products[self.depositType]
                if self.depositQtyRemaining <= 0:
                    self.ClearDeposit()
            return products

    def CanInstallDeposit(self):
        if self.depositType is None:
            return True
        elif self.depositQtyRemaining <= 0:
            return True
        else:
            return False

    def InstallDeposit(self, cycleTime, depositProductTypeID, depositQtyPerCycle, depositTotalQty, depositExpiryTime, lastRunTime=None, installTime=None):
        self.depositType = int(depositProductTypeID)
        self.depositQtyPerCycle = depositQtyPerCycle
        if self.depositQtyPerCycle <= 0:
            self.LogError('ownerID', self.ownerID, '| Extractor pin error, zero depositQtyPerCycle. Defaulting to', EXTRACTOR_MAX_CYCLES, 'cycles to extract')
            self.depositQtyPerCycle = int(math.ceil(depositTotalQty / EXTRACTOR_MAX_CYCLES))
        if depositTotalQty / self.depositQtyPerCycle > EXTRACTOR_MAX_CYCLES:
            self.LogError('ownerID', self.ownerID, '| Extractor pin error, number of cycles from', depositTotalQty, '/', self.depositQtyPerCycle, 'exceeds acceptable limit. Clamping to', EXTRACTOR_MAX_CYCLES, 'cycles.')
            depositTotalQty = self.depositQtyPerCycle * EXTRACTOR_MAX_CYCLES
        self.depositQtyRemaining = depositTotalQty
        self.depositExpiryTime = depositExpiryTime
        self.cycleTime = cycleTime
        self.SetState(STATE_ACTIVE)
        if lastRunTime is not None:
            self.lastRunTime = lastRunTime
        else:
            self.lastRunTime = blue.os.GetWallclockTime()
        if installTime is not None:
            self.installTime = installTime
        else:
            self.installTime = self.lastRunTime
        return self.lastRunTime

    def ClearDeposit(self):
        self.depositType = None
        self.depositQtyPerCycle = 0
        self.depositQtyRemaining = 0
        self.depositExpiryTime = None
        self.installTime = None
        self.SetState(STATE_IDLE)
        return

    def CanActivate(self):
        if self.activityState < STATE_IDLE:
            return False
        else:
            return self.depositType is not None and self.depositQtyRemaining > 0

    def IsActive(self):
        return self.depositType is not None and self.activityState > STATE_IDLE

    def GetDepositInformation(self):
        if self.depositType is None:
            return
        else:
            return [self.id,
             int(self.depositType),
             self.cycleTime / const.SEC,
             self.depositQtyPerCycle,
             self.depositQtyRemaining,
             self.installTime,
             self.depositExpiryTime]

    def IsProducer(self):
        return True

    def IsExtractor(self):
        return True

    def GetProducts(self):
        if self.depositType is None:
            return {}
        else:
            return {self.depositType: self.depositQtyPerCycle}
            return

    def GetTimeToDepletion(self):
        if self.depositType is not None and self.depositQtyPerCycle > 0:
            currCycle = blue.os.GetWallclockTime() - self.lastRunTime
            currCycleTimeLeft = self.cycleTime - currCycle
            numCyclesLeft = math.ceil((self.depositQtyRemaining - self.depositQtyPerCycle) / float(self.depositQtyPerCycle))
            totalTimeLeft = numCyclesLeft * self.cycleTime + currCycleTimeLeft
        else:
            totalTimeLeft = None
        return totalTimeLeft

    def GetTimeToExpiry(self):
        return self.depositExpiryTime - blue.os.GetWallclockTime()

    def Serialize(self, full=False):
        data = BasePin.Serialize(self, full)
        data.cycleTime = self.cycleTime
        data.depositType = int(self.depositType) if self.depositType is not None else None
        data.depositQtyPerCycle = self.depositQtyPerCycle
        data.depositQtyRemaining = self.depositQtyRemaining
        data.depositExpiryTime = self.depositExpiryTime
        data.installTime = self.installTime
        return data

    def GetExtractionType(self):
        return int(self.eventHandler.GetTypeAttribute(self.typeID, const.attributeHarvesterType))

    def HasDifferingDeposit(self, otherPin):
        if self.installTime != otherPin.installTime:
            return True
        if self.GetCycleTime() != otherPin.GetCycleTime():
            return True
        if self.depositQtyPerCycle != otherPin.depositQtyPerCycle:
            return True
        if self.depositQtyRemaining != otherPin.depositQtyRemaining:
            return True
        if self.depositExpiryTime != otherPin.depositExpiryTime:
            return True
        return False