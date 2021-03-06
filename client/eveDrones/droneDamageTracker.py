# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveDrones\droneDamageTracker.py
from eveDrones.droneConst import DAMAGESTATE_NOT_READY
from inventorycommon.const import flagDroneBay, flagNone
import uthread2
import blue

class InBayDroneDamageTracker(object):
    __notifyevents__ = ['OnItemChange',
     'OnRepairDone',
     'OnDamageStateChange',
     'OnDroneControlLost']

    def __init__(self, dogmaLM, clientDogmaLM):
        self.droneDamageStatesByDroneIDs = {}
        sm.RegisterNotify(self)
        self.fetchingInfoForDrones = set()
        self.clearTimestamp = None
        self.SetDogmaLM(dogmaLM)
        self.clientDogmaLM = clientDogmaLM
        return

    def SetDogmaLM(self, dogmaLM):
        self.dogmaLM = dogmaLM

    def FetchInBayDroneDamageToServer(self, droneIDs):
        droneIDsMissingDamage = self.FindDronesMissingDamageState(droneIDs)
        if not droneIDsMissingDamage:
            return
        self.fetchingInfoForDrones.update(droneIDsMissingDamage)
        callMadeTime = blue.os.GetSimTime()
        damageStateForDrones = {}
        damagesForDrones = self.dogmaLM.GetLayerDamageValuesByItems(droneIDsMissingDamage)
        for droneID, droneDamage in damagesForDrones.iteritems():
            maxHull = self.clientDogmaLM.dogmaItems[droneID].attributes[const.attributeHp].GetValue()
            maxArmor = self.clientDogmaLM.dogmaItems[droneID].attributes[const.attributeArmorHP].GetValue()
            damageStateForDrones[droneID] = [droneDamage.shieldInfo, 1.0 - droneDamage.armorDamage / maxArmor, 1.0 - droneDamage.hullDamage / maxHull]

        if not self.HasDictBeenClearedAfterCall(callMadeTime):
            damageStateDict = ConvertDroneStateToCorrectFormat(damageStateForDrones)
            self.droneDamageStatesByDroneIDs.update(damageStateDict)
        self.fetchingInfoForDrones.difference_update(droneIDsMissingDamage)

    def FindDronesMissingDamageState(self, droneIDs):
        droneIDsMissingDamage = {x for x in droneIDs if x not in self.droneDamageStatesByDroneIDs}
        return droneIDsMissingDamage - self.fetchingInfoForDrones

    def HasDictBeenClearedAfterCall(self, callMadeTime):
        if self.clearTimestamp and self.clearTimestamp > callMadeTime:
            return True
        else:
            return False

    def GetDamageStateForDrone(self, droneID):
        if self.IsDroneDamageReady(droneID):
            return self.droneDamageStatesByDroneIDs.get(droneID, None)
        else:
            droneIDsMissingDamage = self.FindDronesMissingDamageState([droneID])
            if droneIDsMissingDamage:
                uthread2.StartTasklet(self.FetchInBayDroneDamageToServer, droneIDsMissingDamage)
            return DAMAGESTATE_NOT_READY

    def IsDroneDamageReady(self, droneID):
        return droneID in self.droneDamageStatesByDroneIDs

    def OnItemChange(self, change, *args):
        if change.itemID not in self.droneDamageStatesByDroneIDs:
            return
        if change.flagID not in (flagDroneBay, flagNone):
            del self.droneDamageStatesByDroneIDs[change.itemID]

    def OnDroneControlLost(self, droneID):
        self.droneDamageStatesByDroneIDs.pop(droneID, None)
        return

    def OnRepairDone(self, itemIDs, *args):
        for itemID in itemIDs:
            self.droneDamageStatesByDroneIDs.pop(itemID, None)

        return

    def OnDamageStateChange(self, itemID, damageState):
        droneDamageInfo = self.droneDamageStatesByDroneIDs.get(itemID, None)
        if droneDamageInfo is None:
            return
        else:
            timestamp = blue.os.GetSimTime()
            droneDamageInfo.UpdateInfo(timestamp, damageState)
            return


def ConvertDroneStateToCorrectFormat(damageStateForDrones):
    newDroneDamageDict = {}
    for itemID, ds in damageStateForDrones.iteritems():
        if ds is None:
            continue
        shieldInfo = ds[0]
        shieldHealth = shieldInfo[0]
        shieldTau = shieldInfo[1]
        timestamp = shieldInfo[2]
        d = DroneDamageObject(itemID, shieldTau, timestamp, shieldHealth, ds[1], ds[2])
        newDroneDamageDict[itemID] = d

    return newDroneDamageDict


class DroneDamageObject:

    def __init__(self, itemID, shieldTau, timestamp, shieldHealth, armorHealth, hullHealth):
        self.itemID = itemID
        self.shieldTau = shieldTau
        self.timestamp = timestamp
        self.shieldHealth = shieldHealth
        self.armorHealth = armorHealth
        self.hullHealth = hullHealth

    def UpdateInfo(self, timestamp, damageValues):
        self.timestamp = timestamp
        self.shieldHealth = damageValues[0]
        self.armorHealth = damageValues[1]
        self.hullHealth = damageValues[2]

    def GetInfoInMichelleFormat(self):
        return [(self.shieldHealth, self.shieldTau, self.timestamp), self.armorHealth, self.hullHealth]