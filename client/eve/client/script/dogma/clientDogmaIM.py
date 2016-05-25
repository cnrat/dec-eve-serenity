# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\dogma\clientDogmaIM.py
import service
import uthread
from clientDogmaLocation import DogmaLocation

class ClientDogmaInstanceManager(service.Service):
    __guid__ = 'svc.clientDogmaIM'
    __startupdependencies__ = ['clientEffectCompiler', 'invCache', 'godma']
    __notifyevents__ = ['ProcessSessionChange']

    def Run(self, *args):
        service.Service.Run(self, *args)
        self.dogmaLocation = None
        self.fittingDogmaLocation = None
        return

    def GetDogmaLocation(self, charBrain=None, *args):
        uthread.Lock('GetDogmaLocation')
        try:
            if self.dogmaLocation is None:
                self.dogmaLocation = DogmaLocation(self, charBrain)
                self.LogInfo('Created client dogmaLocation', id(self.dogmaLocation))
        finally:
            uthread.UnLock('GetDogmaLocation')

        return self.dogmaLocation

    def GetFittingDogmaLocation(self, force=False, *args):
        uthread.Lock('GetFittingDogmaLocation')
        try:
            if self.fittingDogmaLocation is None or force:
                from eve.client.script.ui.shared.fittingGhost.fittingDogmaLocation import FittingDogmaLocation
                self.fittingDogmaLocation = FittingDogmaLocation(self)
                self.LogInfo('Created client fittingDogmaLocation', id(self.fittingDogmaLocation))
        finally:
            uthread.UnLock('GetFittingDogmaLocation')

        return self.fittingDogmaLocation

    def GodmaItemChanged(self, item, change):
        if item.itemID == session.charid:
            return
        else:
            if self.dogmaLocation is not None:
                shipID = self.dogmaLocation.GetCurrentShipID()
                if item.locationID == shipID:
                    self.dogmaLocation.OnItemChange(item, change)
                elif change.get(const.ixLocationID, None) == shipID:
                    self.dogmaLocation.OnItemChange(item, change)
            return

    def ProcessSessionChange(self, isRemote, session, change):
        if self.dogmaLocation is None:
            return
        else:
            if 'stationid2' in change or 'solarsystemid' in change:
                self.dogmaLocation.UpdateRemoteDogmaLocation()
            return

    def GetCapacityForItem(self, itemID, attributeID):
        if self.dogmaLocation is None:
            return
        elif not self.dogmaLocation.IsItemLoaded(itemID):
            return
        else:
            return self.dogmaLocation.GetAttributeValue(itemID, attributeID)