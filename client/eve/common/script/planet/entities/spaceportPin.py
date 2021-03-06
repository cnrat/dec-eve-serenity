# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\planet\entities\spaceportPin.py
import const
from eve.common.script.planet.entities.storagePin import StoragePin
from eve.common.script.planet.entities.basePin import BasePin
import blue
import eve.common.script.util.planetCommon as planetCommon

class SpaceportPin(StoragePin):
    __guid__ = 'planet.SpaceportPin'
    __slots__ = ['lastLaunchTime']

    def __init__(self, typeID):
        StoragePin.__init__(self, typeID)

    def OnStartup(self, id, ownerID, latitude, longitude):
        StoragePin.OnStartup(self, id, ownerID, latitude, longitude)
        self.lastLaunchTime = None
        return

    def IsSpaceport(self):
        return True

    def GetLaunchCycleTime(self):
        return 60 * const.SEC

    def GetNextLaunchTime(self):
        if self.lastLaunchTime is not None:
            return self.lastLaunchTime + self.GetLaunchCycleTime()
        else:
            return

    def CanLaunch(self, commodities, launchTime=None):
        for commodityTypeID, commodityQty in commodities.iteritems():
            if commodityTypeID not in self.contents or self.contents[commodityTypeID] < 1:
                return False

        lt = launchTime
        if launchTime is None:
            lt = blue.os.GetWallclockTime()
        nextLaunchTime = self.GetNextLaunchTime()
        if nextLaunchTime is None or nextLaunchTime <= lt:
            return True
        else:
            return False

    def FetchLaunchCommodities(self, commodities):
        commodsToLaunch = {}
        for commodityTypeID, commodityQty in commodities.iteritems():
            qtyLaunched = int(self.RemoveCommodity(commodityTypeID, int(commodityQty)))
            if qtyLaunched is not None and qtyLaunched > 0:
                commodsToLaunch[commodityTypeID] = qtyLaunched

        return commodsToLaunch

    def CanImportCommodities(self, commodities):
        volume = planetCommon.GetCommodityTotalVolume(commodities)
        if self.capacityUsed + volume > self.GetCapacity():
            return False
        return True

    def Serialize(self, full=False):
        data = StoragePin.Serialize(self, full)
        data.lastLaunchTime = self.lastLaunchTime
        return data

    def GetImportTax(self, commodities, taxRate=0.05):
        importTaxRate = self.eventHandler.GetTypeAttribute(self.typeID, const.attributeImportTax)
        totalTax = 0.0
        for typeID, qty in commodities.iteritems():
            multiplier = self.eventHandler.GetTypeAttribute(typeID, const.attributeImportTaxMultiplier)
            totalTax += qty * importTaxRate * multiplier

        return totalTax * taxRate

    def GetExportTax(self, commodities, taxRate=0.05):
        exportTaxRate = self.eventHandler.GetTypeAttribute(self.typeID, const.attributeExportTax)
        totalTax = 0.0
        for typeID, qty in commodities.iteritems():
            multiplier = self.eventHandler.GetTypeAttribute(typeID, const.attributeImportTaxMultiplier)
            totalTax += qty * exportTaxRate * multiplier

        return totalTax * taxRate

    def HasDifferingState(self, otherPin):
        if self.lastLaunchTime != getattr(otherPin, 'lastLaunchTime', None):
            return True
        else:
            return BasePin.HasDifferingState(self, otherPin)


exports = {'planet.SpaceportPin': SpaceportPin}