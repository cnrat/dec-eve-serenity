# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\services\clonejumpsvc.py
import carbonui.const as uiconst
import service
import util
import sys
import form
import localization

class CloneJump(service.Service):
    __exportedcalls__ = {'GetClones': [],
     'GetCloneImplants': [],
     'GetShipClones': [],
     'GetStationClones': [],
     'HasCloneReceivingBay': [],
     'GetCloneAtLocation': [],
     'GetImplantsForClone': [],
     'DestroyInstalledClone': [],
     'CloneJump': [],
     'OfferShipCloneInstallation': [],
     'LastCloneJumpTime': [],
     'ValidateInstallJumpClone': []}
    __guid__ = 'svc.clonejump'
    __displayname__ = 'Clone Jump Service'
    __notifyevents__ = ['OnShipJumpCloneInstallationOffered',
     'OnShipJumpCloneInstallationDone',
     'OnJumpCloneCacheInvalidated',
     'OnShipJumpCloneCacheInvalidated',
     'OnStationJumpCloneCacheInvalidated',
     'OnShipJumpCloneInstallationCanceled']
    __dependencies__ = []
    __update_on_reload__ = 0

    def Run(self, ms):
        service.Service.Run(self, ms)
        self.jumpClones = None
        self.jumpCloneImplants = None
        self.shipJustClonesShipID = None
        self.shipJumpClones = None
        self.timeLastJump = None
        self.stationJumpClones = None
        self.cloneInstallOfferActive = 0
        self.lastCloneJumpTime = None
        return

    def GetClones(self):
        self.GetCloneState()
        return self.jumpClones

    def GetCloneImplants(self):
        self.GetCloneState()
        return self.jumpCloneImplants

    def SetJumpCloneName(self, cloneID, newName):
        lm = self.GetLM()
        lm.SetJumpCloneName(cloneID, newName)

    def GetLM(self):
        if session.solarsystemid or session.structureid:
            return util.Moniker('jumpCloneSvc', (session.solarsystemid, const.groupSolarSystem))
        else:
            return util.Moniker('jumpCloneSvc', (session.stationid2, const.groupStation))

    def GetCloneState(self):
        if self.jumpClones is None:
            lm = self.GetLM()
            kv = lm.GetCloneState()
            self.jumpClones = kv.clones
            self.jumpCloneImplants = kv.implants
            self.timeLastJump = kv.timeLastJump
        return

    def GetShipClones(self):
        shipID = util.GetActiveShip()
        if not self.shipJumpClones or shipID != self.shipJustClonesShipID:
            lm = self.GetLM()
            self.shipJustClonesShipID = shipID
            self.shipJumpClones = lm.GetShipCloneState()
        return self.shipJumpClones

    def GetStationClones(self):
        if not self.stationJumpClones:
            lm = self.GetLM()
            self.stationJumpClones = lm.GetStationCloneState()
        return self.stationJumpClones

    def OfferShipCloneInstallation(self, charID):
        lm = self.GetLM()
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CloneJump/WaitingForAck'), localization.GetByLabel('UI/CloneJump/InstallationInviteSent', player=charID), 1, 2, abortFunc=self.CancelShipCloneInstallation)
        try:
            lm.OfferShipCloneInstallation(charID)
        except UserError as e:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CloneJump/CloneInstallAborted'), '', 1, 1)
            raise

    def LastCloneJumpTime(self):
        self.GetCloneState()
        return self.timeLastJump

    def DestroyInstalledClone(self, cloneID):
        message = None
        myClones = self.GetClones()
        if myClones:
            myClones = myClones.Index('jumpCloneID')
            if cloneID in myClones:
                if myClones[cloneID].locationID == session.stationid2:
                    message = localization.GetByLabel('UI/CloneJump/ReallyDestroyCloneAtCurrentStation')
                else:
                    cfg.evelocations.Prime([myClones[cloneID].locationID])
                    message = localization.GetByLabel('UI/CloneJump/ReallyDestroyCloneAtSomewhereElse', location=myClones[cloneID].locationID)
        if not message:
            if util.GetActiveShip():
                shipClones = self.GetShipClones()
                if shipClones:
                    shipClones = shipClones.Index('jumpCloneID')
                    if cloneID in shipClones:
                        cfg.eveowners.Prime([shipClones[cloneID].ownerID])
                        cfg.evelocations.Prime([shipClones[cloneID].locationID])
                        message = localization.GetByLabel('UI/CloneJump/ReallyDestroyCloneInShip', owner=shipClones[cloneID].ownerID, ship=shipClones[cloneID].locationID)
        if not message:
            return
        else:
            ret = eve.Message('AskAreYouSure', {'cons': message}, uiconst.YESNO)
            if ret == uiconst.ID_YES:
                lm = self.GetLM()
                lm.DestroyInstalledClone(cloneID)
            return

    def InstallCloneInStation(self):
        if not self.CanJumpCloneFromCurrentLocation():
            return
        lm = self.GetLM()
        ret = eve.Message('AskAcceptJumpCloneCost', {'cost': lm.GetPriceForClone()}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            if session.stationid2:
                lm.InstallCloneInStation()
            else:
                lm.InstallCloneInStructure()

    def CancelShipCloneInstallation(self, *args):
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CloneJump/CloneInstallAborted'), '', 1, 1)
        lm = self.GetLM()
        lm.CancelShipCloneInstallation()

    def CanJumpCloneFromCurrentLocation(self):
        if session.stationid2:
            return True
        if session.structureid:
            return True
        return False

    def CloneJump(self, destLocationID):
        if not self.CanJumpCloneFromCurrentLocation():
            eve.Message('NotAtStation')
            return
        for each in uicore.registry.GetWindows()[:]:
            if isinstance(each, form.Inventory):
                each.CloseByUser()

        lm = self.GetLM()
        cost = lm.GetPriceForClone()
        if eve.Message('AskAcceptJumpCloneCost', {'cost': cost}, uiconst.YESNO) != uiconst.ID_YES:
            return
        try:
            sm.GetService('sessionMgr').PerformSessionChange('clonejump', lm.CloneJump, destLocationID, cost, False)
        except UserError as e:
            if e.msg not in ('JumpCheckWillLoseExistingCloneAndImplants', 'JumpCheckWillLoseExistingClone', 'JumpCheckIntoShip', 'JumpCheckIntoStructure'):
                raise e
            if eve.Message(e.msg, {}, uiconst.YESNO) == uiconst.ID_YES:
                eve.session.ResetSessionChangeTimer('Retrying with confirmation approval')
                sm.GetService('sessionMgr').PerformSessionChange('clonejump', lm.CloneJump, destLocationID, cost, True)
            sys.exc_clear()

    def GetCloneAtLocation(self, locationID):
        clones = self.GetClones()
        if clones:
            for c in clones:
                if locationID == c.locationID:
                    return (c.jumpCloneID, c.cloneName)

        return (None, None)

    def GetImplantsForClone(self, cloneID):
        cloneImplants = self.GetCloneImplants()
        if not cloneImplants:
            return []
        implantsByCloneID = cloneImplants.Filter('jumpCloneID')
        return implantsByCloneID.get(cloneID, [])

    def HasCloneReceivingBay(self):
        if eve.session.shipid:
            ship = sm.GetService('godma').GetItem(eve.session.shipid)
            for module in ship.modules:
                if const.typeCloneVatBayI == module.typeID:
                    return True

        return False

    def ProcessSessionChange(self, isRemote, session, change):
        if 'shipid' in change:
            self.shipJumpClones = None
        if 'solarsystemid2' in change or 'solarsystemid' in change or 'stationid2' in change:
            self.stationJumpClones = None
        return

    def OnJumpCloneCacheInvalidated(self):
        self.jumpClones = None
        self.jumpCloneImplants = None
        self.timeLastJump = None
        sm.ScatterEvent('OnCloneJumpUpdate')
        return

    def OnShipJumpCloneCacheInvalidated(self, locationID, charID):
        if util.GetActiveShip() == locationID:
            self.shipJumpClones = None
            sm.ScatterEvent('OnShipCloneJumpUpdate')
        return

    def OnStationJumpCloneCacheInvalidated(self, locationID, charID):
        if session.stationid2 == locationID:
            self.stationJumpClones = None
            sm.ScatterEvent('OnStationCloneJumpUpdate')
        return

    def OnShipJumpCloneInstallationOffered(self, args):
        offeringCharID, targetCharID, shipID, b = (args[0],
         args[1],
         args[2],
         args[3])
        self.cloneInstallOfferActive = 1
        cfg.eveowners.Prime([offeringCharID, targetCharID])
        offeringChar = cfg.eveowners.Get(offeringCharID)
        cfg.evelocations.Prime([shipID])
        ship = cfg.evelocations.Get(shipID)
        lm = self.GetLM()
        costs = lm.GetPriceForClone()
        ret = eve.Message('JumpCloneInstallationOffered', {'offerer': offeringChar.name,
         'shipname': ship.name,
         'costs': util.FmtISK(costs)}, uiconst.YESNO)
        try:
            if ret == uiconst.ID_YES:
                lm.AcceptShipCloneInstallation()
            elif ret != uiconst.ID_CLOSE:
                lm.CancelShipCloneInstallation()
        except UserError as e:
            eve.Message(e.msg, e.dict)
            sys.exc_clear()

        self.cloneInstallOfferActive = 0

    def OnShipJumpCloneInstallationDone(self, args):
        offeringCharID, targetCharID, shipID, b = (args[0],
         args[1],
         args[2],
         args[3])
        self.cloneInstallOfferActive = 0
        sm.ScatterEvent('OnShipJumpCloneUpdate')
        sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CloneJump/CloneInstallFinished'), '', 1, 1)

    def OnShipJumpCloneInstallationCanceled(self, args):
        try:
            sm.GetService('loading').ProgressWnd(localization.GetByLabel('UI/CloneJump/CloneInstallAborted'), '', 1, 1)
            lm = self.GetLM()
            lm.CancelShipCloneInstallation()
        except UserError as e:
            self.LogInfo('Ignoring usererror', e.msg, 'while cancelling ship clone installation')
            sys.exc_clear()

    def ValidateInstallJumpClone(self):
        error_labels = self.GetLM().ValidateInstallJumpClone()
        errors = []
        for label in error_labels:
            if isinstance(label, basestring):
                errors.append(localization.GetByLabel(label))
            else:
                with util.ExceptionEater():
                    label, args = label
                    print label, args
                    errors.append(localization.GetByLabel(label, **args))

        return errors