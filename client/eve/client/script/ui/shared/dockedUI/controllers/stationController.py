# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\dockedUI\controllers\stationController.py
from eve.client.script.ui.shared.dockedUI.controllers.baseController import BaseStationController
from eve.common.script.util.structuresCommon import GetServicesFromMask
import invCtrl
import sys
from brennivin import itertoolsext
import carbonui.const as uiconst
from eve.client.script.ui.station import stationServiceConst
import structures
import blue
import invCont
import evegraphics.settings as gfxsettings

class StationController(BaseStationController):

    def __init__(self, itemID=None):
        self.corpStationMgr = None
        self.serviceAccessCache = {}
        return

    def Undock(self):
        return sm.GetService('station').Exit()

    def ChangeDockedMode(self, viewState):
        if viewState.HasActiveTransition():
            return
        if self._IsInCQ():
            sm.GetService('cmd').CmdEnterHangar()
        else:
            sm.GetService('cmd').CmdEnterCQ()

    def CorpsWithOffices(self):
        return sm.GetService('corp').GetCorporationsWithOfficesAtStation()

    def GetNumberOfUnrentedOffices(self):
        return sm.GetService('corp').GetCorpStationManager().GetNumberOfUnrentedOffices()

    def DoesOfficeExist(self):
        return sm.GetService('corp').GetOffice() is not None

    def CanRent(self):
        return self._HasRole(const.corpRoleCanRentOffice)

    def CanMoveHQ(self):
        return self._HasRole(const.corpRoleDirector)

    def _HasRole(self, corpRole):
        return session.corprole & corpRole == corpRole

    def IsMyHQ(self):
        return sm.GetService('corp').GetCorporation().stationID == session.stationid2

    def MyCorpIsOwner(self):
        return sm.GetService('corp').DoesCharactersCorpOwnThisStation()

    def GetCostForOpeningOffice(self):
        return sm.GetService('corp').GetCorpStationManager().GetQuoteForRentingAnOffice()

    def RentOffice(self, cost):
        return sm.GetService('corp').GetCorpStationManager().RentOffice(cost)

    def GetMyCorpOffice(self):
        return sm.GetService('corp').GetOffice()

    def CorpHasItemsInstaton(self):
        items = invCtrl.StationCorpHangar(divisionID=None).GetItems()
        hasItems = itertoolsext.any(items, lambda x: x.ownerID == session.corpid)
        return hasItems

    def UnrentOffice(self):
        corpStationMgr = sm.GetService('corp').GetCorpStationManager()
        sm.GetService('corp').hasImpoundedItemsCacheTime = None
        corpStationMgr.CancelRentOfOffice()
        return

    def SetHQ(self):
        if sm.GetService('godma').GetType(eve.stationItem.stationTypeID).isPlayerOwnable == 1:
            raise UserError('CanNotSetHQAtPlayerOwnedStation')
        if eve.Message('MoveHQHere', {}, uiconst.YESNO) == uiconst.ID_YES:
            sm.GetService('corp').GetCorpStationManager().MoveCorpHQHere()

    def GetCostForGettingCorpJunkBack(self):
        corpStationMgr = sm.GetService('corp').GetCorpStationManager()
        cost = corpStationMgr.GetQuoteForGettingCorpJunkBack()
        return cost

    def HasCorpImpountedItems(self):
        return sm.GetService('corp').HasCorpImpoundedItemsAtStation()

    def ReleaseImpoundedItems(self, cost):
        corpStationMgr = sm.GetService('corp').GetCorpStationManager()
        corpStationMgr.PayForReturnOfCorpJunk(cost)
        sm.GetService('corp').hasImpoundedItemsCacheTime = None
        return

    def OpenStationMgmt(self):
        uicore.cmd.OpenStationManagement()

    def GetServicesInStation(self):
        serviceMask = eve.stationItem.serviceMask
        servicesAtStation = GetServicesFromMask(serviceMask)
        haveServices = self._GetServiceInfoAvailable(servicesAtStation)
        for serviceData in stationServiceConst.serviceData:
            if serviceData not in haveServices:
                continue
            if serviceData.serviceID == structures.SERVICE_FACTION_WARFARE:
                if not sm.GetService('facwar').CheckStationElegibleForMilitia():
                    haveServices.remove(serviceData)
            elif serviceData.serviceID == structures.SERVICE_SECURITY_OFFICE:
                if not sm.GetService('securityOfficeSvc').CanAccessServiceInStation(session.stationid2):
                    haveServices.remove(serviceData)

        return haveServices

    def GetGuests(self):
        return sm.GetService('station').GetGuests()

    def PerformAndGetErrorForStandingCheck(self, stationServiceID):
        time, result = self._GetResultFromCache(stationServiceID)
        now = blue.os.GetWallclockTime()
        if time and time + const.MIN * 5 > now:
            return result
        else:
            try:
                self._DoStandingCheckForServices(stationServiceID)
                result = None
            except Exception as e:
                sys.exc_clear()
                result = e

            self._AddServiceToCache(stationServiceID, now, result)
            return result

    def _DoStandingCheckForServices(self, stationServiceID):
        if self.corpStationMgr is None:
            self.corpStationMgr = sm.GetService('corp').GetCorpStationManager()
        self.corpStationMgr.DoStandingCheckForStationService(stationServiceID)
        return

    def _AddServiceToCache(self, serviceID, timestamp, error):
        self.serviceAccessCache[serviceID] = (timestamp, error)

    def RemoveServiceFromCache(self, serviceID):
        if serviceID in self.serviceAccessCache:
            del self.serviceAccessCache[serviceID]

    def _GetResultFromCache(self, serviceID):
        if serviceID in self.serviceAccessCache:
            time, result = self.serviceAccessCache[serviceID]
            return (time, result)
        else:
            return (None, None)

    def GetAgents(self):
        return sm.GetService('agents').GetAgentsByStationID()[session.stationid2]

    def GetOwnerID(self):
        return eve.stationItem.ownerID

    def GetStationItemsAndShipsClasses(self):
        return (invCont.StationItems, invCont.StationShips)

    def GetItemID(self):
        return eve.stationItem.itemID

    def InProcessOfUndocking(self):
        return sm.GetService('station').PastUndockPointOfNoReturn()

    def IsRestrictedByGraphicsSettings(self):
        return False

    def IsExiting(self):
        return sm.GetService('station').exitingstation

    def GetDockedModeTextPath(self, viewName=None):
        if viewName is not None:
            isInCQ = viewName == 'station'
        else:
            isInCQ = self._IsInCQ()
        if isInCQ:
            textPath = 'UI/Commands/EnterHangar'
        else:
            textPath = 'UI/Commands/EnterCQ'
        return textPath

    def _IsInCQ(self):
        viewStateSvc = sm.GetService('viewState')
        currentView = viewStateSvc.GetCurrentView()
        if currentView is not None and currentView.name == 'station':
            return True
        else:
            return False
            return

    def GetDisabledDockingModeHint(self):
        pass

    def GetCurrentStateForService(self, serviceID):
        return sm.GetService('station').GetServiceState(serviceID)

    def IsControlable(self):
        return False