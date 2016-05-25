# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\lpstore.py
import blue
import const
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.control.infoIcon import InfoIcon
import inventorycommon.typeHelpers
import localization
import service
import uiprimitives
import uicontrols
import uix
import uiutil
import uthread
import util
import uicls
import carbonui.const as uiconst
import weakref
import math
import log
import trinity
import evetypes
from lpstoreRequirement import LpRequirement, ISKRequirement, AnalysisKreditsRequirement, getContainerName, getNotFulfilledIconName, getLabelName
REWARD_COLUMN_WIDTH = 200
COST_COLUMN_WIDTH = 115
REQUIRED_ITEMS_COLUMN_WIDTH = 200
BUY_OPTION_COLUMN_WIDTH = 80
REWARD_COLUMN_WIDTH_MIN = 200
COST_COLUMN_WIDTH_MIN = 115
REQUIRED_ITEMS_COLUMN_WIDTH_MIN = 100
BUY_OPTION_COLUMN_WIDTH_MIN = 80
REQUIREMENT_NOT_FULFILLED_ICON_PATH = 'ui_38_16_194'
REQUIREMENT_NOT_FULFILLED_ICON_SIZE = 16
REQUIREMENT_NOT_FULFILLED_ICON_PADDING = 2

class LPStoreLabel(uicontrols.EveLabelMedium):
    __guid__ = 'lpstore.LPStoreLabel'
    default_align = uiconst.TOTOP


class LPStoreEntryLabel(uicontrols.EveLabelMedium):
    __guid__ = 'lpstore.LPStoreEntryLabel'
    default_align = uiconst.CENTERRIGHT
    default_maxLines = None


class LPStoreHeaderLabel(uicontrols.EveLabelSmall):
    __guid__ = 'lpstore.LPStoreHeaderLabel'
    default_align = uiconst.TOTOP


class LPStoreButton(uiprimitives.Container):
    __guid__ = 'lpstore.LPStoreButton'
    default_state = uiconst.UI_PICKCHILDREN
    default_align = uiconst.TOLEFT
    default_name = 'BtnParent'
    default_label = 'unnamed'

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        self.sr.btn = uicontrols.Button(parent=self, name='btn', align=uiconst.CENTER, label=attributes.get('label', self.default_label))


def GetItemText(typeID, qty, numberOfOffers=1, checkIsBlueprint=True):
    isBlueprint = False
    if checkIsBlueprint:
        if evetypes.GetCategoryID(typeID) == const.categoryBlueprint:
            isBlueprint = True
    if isBlueprint:
        txt = localization.GetByLabel('UI/LPStore/BlueprintRunsLeft', quantity=numberOfOffers, typeID=typeID, numRuns=qty)
    else:
        txt = localization.GetByLabel('UI/LPStore/RewardItem', quantity=qty * numberOfOffers, rewardItem=typeID)
    return txt


class LPStoreSvc(service.Service):
    __guid__ = 'svc.lpstore'
    __notifyevents__ = ['OnAccountChange',
     'ProcessSessionChange',
     'OnLPChange',
     'OnAnalysisKreditsChange',
     'OnUIRefresh',
     'OnLPStorePriceChange']
    __dependencies__ = ['settings']
    settingsVersion = 4

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.cache = uiutil.Bunch()
        self.defaultPreset = localization.GetByLabel('UI/LPStore/PresetAffordable')

    def GetCurrentFilters(self):
        return self.currentFilters.copy()

    def GetCurrentPresetLabel(self):
        return self.currentPreset

    def GetMyLPs(self, corpID=None):
        if self.cache.lps is None:
            if corpID is None:
                if self.cache.corpID:
                    corpID = self.cache.corpID
            if not corpID and util.IsNPC(eve.stationItem.ownerID):
                corpID = eve.stationItem.ownerID
            if corpID:
                self.cache.lps = sm.RemoteSvc('LPSvc').GetLPForCharacterCorp(corpID)
            else:
                self.cache.lps = 0
        return self.cache.lps

    def GetMyConcordLPs(self):
        if self.cache.concordLps is None:
            self.cache.concordLps = sm.RemoteSvc('LPSvc').GetLPForCharacterCorp(const.ownerCONCORD)
        return self.cache.concordLps

    def OpenConcordExchange(self, corpID):
        exchangeRate = self.GetConcordLPExchangeRate()
        myConcordLP = self.GetMyConcordLPs()
        corporationLPs = self.GetMyLPs(corpID)
        LPExhangeDialog.CloseIfOpen(windowID='LPExhangeDialog_%s' % corpID)
        wnd = LPExhangeDialog.Open(windowID='LPExhangeDialog_%s' % corpID, currentFromCorpLPs=myConcordLP, currentToCorpLPs=corporationLPs, exchangeRate=exchangeRate, toCorpID=corpID)

    def GetConcordLPExchangeRate(self, corpID=None):
        if corpID is None:
            if self.cache.corpID:
                corpID = self.cache.corpID
        if not corpID and util.IsNPC(eve.stationItem.ownerID):
            corpID = eve.stationItem.ownerID
        if self.cache.exchangeRates is None:
            self.cache.exchangeRates = sm.RemoteSvc('LPSvc').GetLPExchangeRates()
        if const.ownerCONCORD in self.cache.exchangeRates and corpID in self.cache.exchangeRates[const.ownerCONCORD]:
            return self.cache.exchangeRates[const.ownerCONCORD][corpID]
        else:
            return

    def OnLPStorePriceChange(self):
        self.cache.offers = None
        self.GetOffers()
        self.DirtyWindow()
        return

    def GetOffers(self):
        if self.cache.offers is None:
            self.cache.offers = sm.RemoteSvc('LPSvc').GetAvailableOffersFromCorp(self.cache.corpID)
            self._RefreshOfferSortValues()
        return self.cache.offers

    def ConvertConcordLP(self, corpID, amount):
        sm.RemoteSvc('LPSvc').ExchangeConcordLP(corpID, amount)

    def GetCurrentCorpName(self):
        return cfg.eveowners.Get(self.cache.corpID).name

    def ChangeFilters(self, newFilters):
        self.currentFilters = newFilters
        self.currentPreset = localization.GetByLabel('UI/LPStore/PresetNone')
        self._PersistFilters()
        sm.ScatterEvent('OnLPStoreCurrentPresetChange')
        sm.ScatterEvent('OnLPStoreFilterChange')

    def ChangeCurrentPreset(self, newPreset):
        self.currentPreset = newPreset
        self.currentFilters = self._GetPresetFilters(newPreset)
        self._PersistFilters()
        sm.ScatterEvent('OnLPStoreCurrentPresetChange')
        sm.ScatterEvent('OnLPStoreFilterChange')

    def GetPresets(self):
        ret = self._GetDefaultPresets() + self.userPresets
        if self.currentPreset == localization.GetByLabel('UI/LPStore/PresetNone'):
            ret.insert(0, uiutil.Bunch(label=localization.GetByLabel('UI/LPStore/PresetNone'), filters=None, editable=False))
        return ret

    def AddPreset(self, name, filters):
        self.userPresets.append(uiutil.Bunch(label=name, filters=filters, editable=True))
        self._PersistPresets()
        sm.ScatterEvent('OnLPStorePresetsChange')

    def OverwritePreset(self, label, filters):
        for i, p in enumerate(self.userPresets):
            if p.label == label:
                self.userPresets[i] = uiutil.Bunch(label=label, filters=filters.copy(), editable=True)
                self.ChangeCurrentPreset(label)
                self._PersistPresets()
                return
        else:
            log.LogError('svc.lpstore.OverwritePreset: Preset not found.')

    def DeletePreset(self, label):
        if label == self.currentPreset:
            self.ChangeCurrentPreset(self.defaultPreset)
        for p in self.userPresets:
            if p.label == label:
                self.userPresets.remove(p)
                self._PersistPresets()
                sm.ScatterEvent('OnLPStorePresetsChange')
                return
        else:
            log.LogError('svc.lpstore.DeletePreset: Preset not found.')

    def _GetSetting(self, key, default):
        return settings.user.ui.Get('%s_%s' % (key, self.settingsVersion), default)

    def _SetSetting(self, key, value):
        return settings.user.ui.Set('%s_%s' % (key, self.settingsVersion), value)

    def _InitPresets(self):
        if hasattr(self, 'initedPresets'):
            return
        self.userPresets = [ uiutil.Bunch(**d) for d in self._GetSetting('lpStoreFilterPresets', []) ]
        self.currentPreset = self._GetSetting('lpStoreCurrentPreset', self.defaultPreset)
        if self.currentPreset == localization.GetByLabel('UI/LPStore/PresetNone'):
            self.currentFilters = settings.user.ui.Get('lpStoreCurrentFilters', self._GetPresetFilters(self.defaultPreset))
        else:
            self.currentFilters = self._GetPresetFilters(self.currentPreset)
        self.initedPresets = True

    def _GetPresetFilters(self, label):
        if label == localization.GetByLabel('UI/LPStore/PresetNone'):
            return self.currentFilters
        for preset in self.GetPresets():
            if preset.label == label:
                return preset.filters

        return self._GetPresetFilters(self.defaultPreset)

    def _PersistPresets(self):
        self._SetSetting('lpStoreFilterPresets', [ {'label': preset.label,
         'filters': preset.filters,
         'editable': True} for preset in self.userPresets ])
        self.settings.SaveSettings()

    def _PersistFilters(self):
        self._SetSetting('lpStoreCurrentPreset', self.currentPreset)
        if self.currentPreset == localization.GetByLabel('UI/LPStore/PresetNone'):
            self._SetSetting('lpStoreCurrentFilters', self.currentFilters)
        self.settings.SaveSettings()

    def _GetDefaultPresets(self):
        affordableFilters = {'reqNotInHangar': True,
         'dynamicMaxLP': True,
         'dynamicMaxISK': True,
         'dynamicMaxAnalysisKredits': True}
        return [uiutil.Bunch(label=localization.GetByLabel('UI/LPStore/PresetAffordable'), filters=affordableFilters, editable=False), uiutil.Bunch(label=localization.GetByLabel('UI/LPStore/PresetAll'), filters={}, editable=False)]

    def _RefreshOfferSortValues(self):
        for offer in self.cache.offers:
            self._SetOfferDataSortOrder(offer)

    def AcceptOffer(self, data, numberOfOffers=1):
        if getattr(self, 'acceptingOffer', False) == True:
            return
        try:
            self.acceptingOffer = True
            offer = GetItemText(data.typeID, data.qty, numberOfOffers).replace('<br>', ' ')
            price = self._GetPrice(data, numberOfOffers)
            if eve.Message('ConfirmAcceptLPOffer', {'offer': offer,
             'price': price}, uiconst.OKCANCEL, uiconst.ID_OK) != uiconst.ID_OK:
                return False
            ret = sm.RemoteSvc('LPSvc').TakeOffer(self.cache.corpID, data.offerID, numberOfOffers)
            if ret:
                eve.Message('LPStoreOfferAccepted', {'name': cfg.eveowners.Get(eve.session.charid).name})
            if self.cache.lps:
                del self.cache.lps
            if self.cache.analysisKredits:
                del self.cache.analysisKredits
            if len(data.reqItems) > 0 and self.cache.hangarInv:
                del self.cache.hangarInv
            self.DirtyWindow()
            sm.ScatterEvent('OnLPStoreAcceptOffer')
        finally:
            self.acceptingOffer = False

        return True

    def _GetPrice(self, data, numberOfOffers):
        price = ''
        for requirement in self.LpOfferRequirements:
            requirementName = requirement.name
            if requirementName:
                cost = data.Get(requirementName, 0)
                if cost > 0:
                    totalCost = requirement.formatAmount(cost * numberOfOffers)
                    if requirement.priceLabelPath:
                        keywords = {requirementName: totalCost}
                        price += localization.GetByLabel(requirement.priceLabelPath, **keywords) + '<br>'
                    else:
                        price += localization.GetByLabel('UI/LPStore/OfferItems', itemText=totalCost) + '<br>'

        for item in data.reqItems:
            price += localization.GetByLabel('UI/LPStore/OfferItems', itemText=GetItemText(item[0], item[1], numberOfOffers)) + '<br>'

        return price

    def HaveItem(self, typeID, qty):
        if self.cache.hangarInv is None:
            hi = {}
            inv = sm.GetService('invCache').GetInventory(const.containerHangar).List(const.flagHangar)
            for item in inv:
                if not item.singleton:
                    hi[item.typeID] = max(hi.get(item.typeID, 0), item.stacksize)

            self.cache.hangarInv = hi
        return self.cache.hangarInv.get(typeID, 0) >= qty

    def GetMyISK(self):
        return sm.GetService('wallet').GetWealth()

    def GetMyAnalysisKredits(self):
        if self.cache.analysisKredits is None:
            self.cache.analysisKredits = sm.RemoteSvc('ProjectDiscovery').get_player_analysis_kredits()
        return self.cache.analysisKredits

    def OpenLPStore(self, corpID):
        if self.cache.corpID and corpID != self.cache.corpID:
            if self.cache.lps:
                del self.cache.lps
        self.cache.corpID = corpID
        self._InitPresets()
        self.cache.hangarInv = None
        wnd = LPStoreWindow.ToggleOpenClose()
        if wnd:
            wnd.RefreshIfNotAlready()
        return

    def OnUIRefresh(self):
        wnd = LPStoreWindow.GetIfOpen()
        if wnd:
            wnd.Close()
            self.OpenLPStore(self.cache.corpID)

    def DirtyWindow(self):
        if not getattr(self, 'refreshpending', False):
            self.refreshpending = True
            uthread.pool('lpStore::ReportDirtyWindow', self.__DirtyWindow)

    def __DirtyWindow(self):
        blue.pyos.synchro.SleepWallclock(1000)
        if self.cache.offers:
            self._RefreshOfferSortValues()
        w = self._GetWnd()
        if w is not None:
            w.Refresh()
        self.refreshpending = False
        return

    def _GetWnd(self):
        return LPStoreWindow.GetIfOpen()

    def OnAccountChange(self, accountKey, ownerID, balance):
        if accountKey == 'cash' and ownerID == eve.session.charid:
            self.DirtyWindow()

    def ProcessSessionChange(self, isremote, session, change):
        if 'stationid2' in change:
            self.cache.clear()
            w = self._GetWnd()
            if w:
                w.Close()

    def OnLPChange(self, what):
        currentLPs = self.cache.lps
        if self.cache.lps is not None:
            del self.cache.lps
        if self.cache.concordLps is not None:
            del self.cache.concordLps
        self.DirtyWindow()
        if session.stationid2 and currentLPs == 0:
            sm.GetService('station').ReloadLobby()
        return

    def OnAnalysisKreditsChange(self):
        currentAnalysisKredits = self.cache.analysisKredits
        if self.cache.analysisKredits is not None:
            del self.cache.analysisKredits
        self.DirtyWindow()
        if session.stationid2 and currentAnalysisKredits == 0:
            sm.GetService('station').ReloadLobby()
        return

    def _SetOfferDataSortOrder(self, data):
        offerData = []
        offerData.append((localization.GetByLabel('UI/LPStore/Reward'), evetypes.GetName(data.typeID)))
        for requirement in self.GetRequirements():
            requirementName = requirement.name
            cost = data.Get(requirementName, 0)
            if requirement.costLabelPath:
                costLabel = localization.GetByLabel(requirement.costLabelPath)
                if not cost:
                    cost = 0
                offerData.append((costLabel, cost))

        offerData.append((localization.GetByLabel('UI/LPStore/RequiredItems'), self._GetRequiredItemsSortValues(data)))
        offerData.append((localization.GetByLabel('UI/VirtualGoodsStore/Buttons/Buy'), not self.CanAcceptOffer(data)))
        for label, sortval in offerData:
            data.Set('sort_%s' % label, sortval)

    def _GetRequiredItemsSortValues(self, data):
        reqItems = data.Get('reqItems', [])
        typeNames = [ evetypes.GetName(typeID) for typeID, qty in reqItems ]
        typeNames.sort()
        return (len(typeNames), tuple(typeNames))

    def GetRequirements(self):
        if not getattr(self, 'LpOfferRequirements', None):
            self._CreateRequirements()
        return self.LpOfferRequirements

    def _CreateRequirements(self):
        self.LpOfferRequirements = [LpRequirement(checkAmountFunction=self.GetMyLPs), ISKRequirement(checkAmountFunction=self.GetMyISK), AnalysisKreditsRequirement(checkAmountFunction=self.GetMyAnalysisKredits)]

    def CanAcceptOffer(self, data):
        requiredItems = data.Get('reqItems', [])
        missingItems = [ 1 for typeID, qty in requiredItems if not self.HaveItem(typeID, qty) ]
        areCostRequirementsFulfilled = self.AreRequirementsFulfilled(data)
        return areCostRequirementsFulfilled and not missingItems

    def AreRequirementsFulfilled(self, data):
        for requirement in self.LpOfferRequirements:
            if not self._IsRequirementFulfilled(data, requirement):
                return False

        return True

    def _IsRequirementFulfilled(self, data, requirement):
        requirementName = requirement.name
        if not requirementName:
            return True
        cost = data.Get(requirementName, 0)
        return requirement.checkAmount(cost)


class LPOfferEntry(uicontrols.SE_BaseClassCore):
    __guid__ = 'listentry.LPOffer'
    iconSize = 64
    iconMargin = 2
    lineHeight = 1
    labelMargin = 6
    reqItemEntryHeight = 16
    entryHeight = reqItemEntryHeight * 5 + lineHeight

    def ApplyAttributes(self, attributes):
        self.lpOfferRequirementColumns = sm.GetService('lpstore').GetRequirements()
        uicontrols.SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.amountEdit = None
        self._AddRewardColumn()
        self._AddRequirementColumns()
        self._AddRequiredItemsColumn()
        self._AddBuyColumn()
        return

    def _AddRewardColumn(self):
        self.sr.rewardParent = uiprimitives.Container(parent=self, name='rewardParent', align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN)
        self.sr.rewardIconParent = uiprimitives.Container(parent=self.sr.rewardParent, name='rewardIconParent', align=uiconst.TOLEFT, width=self.entryHeight)
        self.sr.rewardInfoIcon = InfoIcon(parent=self.sr.rewardIconParent, align=uiconst.TOPRIGHT, left=10, top=10)
        self.sr.icon = uicontrols.Icon(parent=self.sr.rewardIconParent, size=self.iconSize, ignoreSize=True, align=uiconst.CENTER, state=uiconst.UI_DISABLED)
        rewardLabelClipper = uiprimitives.Container(parent=self.sr.rewardParent, name='rewardLabelClipper', state=uiconst.UI_PICKCHILDREN, align=uiconst.TOALL, clipChildren=True)
        self.sr.rewardLabel = LPStoreEntryLabel(parent=rewardLabelClipper, left=self.labelMargin, align=uiconst.CENTERLEFT)

    def _AddRequirementColumns(self):
        for requirement in self.lpOfferRequirementColumns:
            self._AddRequirementColumn(requirement)

    def _AddRequirementColumn(self, requirement):
        parentContainerName = getContainerName(requirement)
        iconName = getNotFulfilledIconName(requirement)
        labelName = getLabelName(requirement)
        notFulfilledHintPath = requirement.notFulfilledHintPath
        parentContainer = uiprimitives.Container(name=parentContainerName, parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=True)
        if notFulfilledHintPath:
            notFulfilledHint = localization.GetByLabel(notFulfilledHintPath)
            requirementNotFulfilledIcon = uicontrols.Icon(name=iconName, parent=parentContainer, icon=REQUIREMENT_NOT_FULFILLED_ICON_PATH, hint=notFulfilledHint, size=REQUIREMENT_NOT_FULFILLED_ICON_SIZE, left=REQUIREMENT_NOT_FULFILLED_ICON_PADDING, align=uiconst.CENTERLEFT)
            self.sr[iconName] = requirementNotFulfilledIcon
        label = LPStoreEntryLabel(parent=parentContainer, name=labelName, left=self.labelMargin)
        self.sr[labelName] = label

    def _AddRequiredItemsColumn(self):
        parentContainer = uiprimitives.Container(name='reqItemsParent', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=True)
        self.sr.reqItems = uiprimitives.Container(name='reqItems', parent=parentContainer, align=uiconst.CENTERLEFT)

    def _AddBuyColumn(self):
        parentContainer = uiprimitives.Container(name='acceptParent', parent=self, state=uiconst.UI_PICKCHILDREN, align=uiconst.TOLEFT, clipChildren=True)
        self.sr.buyBtn = uicontrols.Button(name='buyBtn', parent=parentContainer, label=localization.GetByLabel('UI/VirtualGoodsStore/Buttons/Buy'), align=uiconst.CENTER, texturePath=None, func=self.OnBuyBtn)
        uicontrols.Frame(bgParent=self.sr.buyBtn, name='dot', texturePath='res:/UI/Texture/Shared/windowButtonDOT.png', cornerSize=6, spriteEffect=trinity.TR2_SFX_DOT)
        self.sr.cannotAcceptIcon = uicontrols.Icon(parent=parentContainer, icon='ui_38_16_194', name='cannotAcceptIcon', size=16, hint=localization.GetByLabel('UI/LPStore/HintCannotAccept'), align=uiconst.CENTER)
        return

    def OnBuyBtn(self, *args):
        self.utilMenu = uicls.ExpandedUtilMenu(parent=uicore.layer.utilmenu, controller=self.sr.buyBtn, menuAlign=uiconst.TOPLEFT, GetUtilMenu=self.GetUtilMenu)

    def GetUtilMenu(self, menuParent):
        cont = uicontrols.ContainerAutoSize(parent=menuParent, align=uiconst.TOTOP, padding=const.defaultPadding)
        cont.GetEntryWidth = lambda mc=cont: 80
        self.amountEdit = uicontrols.SinglelineEdit(name='amountEdit', parent=cont, align=uiconst.TOTOP, ints=[1, const.maxLoyaltyStoreBulkOffers], setvalue=1, label=localization.GetByLabel('UI/Common/Amount'), padding=(5, 10, 5, 0), OnReturn=self.Buy)
        uicontrols.Button(name='buyButton', parent=cont, align=uiconst.TOTOP, label=localization.GetByLabel('UI/LPStore/Accept'), func=self.Buy, padding=(5, 5, 5, 5))
        uicore.registry.SetFocus(self.amountEdit)

    def Buy(self, *args):
        accepted = sm.GetService('lpstore').AcceptOffer(self.sr.node, self.amountEdit.GetValue())
        if accepted and self.utilMenu:
            self.utilMenu.Close()

    def Startup(self, *etc):
        pass

    def Load(self, data):
        uthread.pool('lpStore::LPOfferEntry.Load_Thread', self.Load_Thread, data)

    def Load_Thread(self, data):
        anyMiss = set()
        abstractInfo = None
        isCopy = False
        if evetypes.GetCategoryID(data.typeID) == const.categoryBlueprint:
            bpData = sm.GetService('blueprintSvc').GetBlueprintTypeCopy(typeID=data.typeID, runsRemaining=data.qty, original=False)
            abstractInfo = util.KeyVal(bpData=bpData)
            isCopy = True
        self.sr.rewardInfoIcon.OnClick = (uix.ShowInfo,
         data.typeID,
         None,
         abstractInfo)
        self.sr.icon.LoadIconByTypeID(typeID=data.typeID, size=64, ignoreSize=True, isCopy=isCopy)
        self.sr.rewardLabel.SetText(GetItemText(data.typeID, data.Get('qty', 1)))
        self._LoadRequirementColumns(data)
        if sm.GetService('lpstore').CanAcceptOffer(data):
            alpha = 1.0
            self.sr.buyBtn.state = uiconst.UI_NORMAL
            self.sr.cannotAcceptIcon.state = uiconst.UI_HIDDEN
        else:
            alpha = 0.4
            self.sr.buyBtn.state = uiconst.UI_HIDDEN
            self.sr.cannotAcceptIcon.state = uiconst.UI_NORMAL
        self.sr.icon.color.a = self.sr.rewardLabel.color.a = alpha
        self.hint = self._GetRewardCostHint()
        return

    def _GetRewardCostHint(self):
        requirements = {}
        for requirementColumn in self.lpOfferRequirementColumns:
            costLabelPath = requirementColumn.costLabelPath
            if costLabelPath:
                costName = requirementColumn.name
                costNameText = localization.GetByLabel(costLabelPath)
                costLabel = getLabelName(requirementColumn)
                costLabelText = self.sr[costLabel].text
                requirements[costName] = costNameText
                requirements[costLabel] = costLabelText

        return localization.GetByLabel('UI/LPStore/HintRewardCost', rewardLabel=self.sr.rewardLabel.text, **requirements)

    def _LoadRequirementColumns(self, data):
        for requirementColumn in self.lpOfferRequirementColumns:
            self._LoadRequirementColumn(data, requirementColumn)

        self._LoadRequiredItems(data)

    def _LoadRequirementColumn(self, data, requirementColumn):
        requirementName = requirementColumn.name
        cost = data.Get(requirementName, 0)
        labelName = getLabelName(requirementColumn)
        amountName = requirementColumn.amountName
        amount = requirementColumn.formatAmount(cost)
        amountHintPath = requirementColumn.amountHintPath
        amountText = amount
        if amountHintPath:
            keywords = {amountName: amount}
            amountText = localization.GetByLabel(amountHintPath, **keywords)
        self.sr[labelName].SetText(amountText)
        requirementNotFulfilledIcon = getNotFulfilledIconName(requirementColumn)
        if requirementColumn.checkAmount(cost):
            self.sr[requirementNotFulfilledIcon].state = uiconst.UI_HIDDEN
        else:
            self.sr[requirementNotFulfilledIcon].state = uiconst.UI_NORMAL

    def _LoadRequiredItems(self, data):
        reqItems = data.Get('reqItems', [])
        self.sr.reqItems.Flush()
        for idx, (typeID, qty) in enumerate(reqItems):
            if idx >= len(self.sr.reqItems.children):
                entry = RequiredItem(parent=self.sr.reqItems, height=self.reqItemEntryHeight)
            else:
                entry = self.sr.reqItems.children[idx]
                entry.state = uiconst.UI_PICKCHILDREN
            entry.sr.infoIcon.OnClick = (uix.ShowInfo, typeID, None)
            entry.sr.label.SetText(GetItemText(typeID, qty, checkIsBlueprint=False))
            if sm.GetService('lpstore').HaveItem(typeID, qty):
                entry.sr.cannotIcon.state = uiconst.UI_HIDDEN
            else:
                entry.sr.cannotIcon.state = uiconst.UI_NORMAL

        for entry in self.sr.reqItems.children[len(reqItems):]:
            entry.state = uiconst.UI_HIDDEN

        self.sr.reqItems.height = self.reqItemEntryHeight * len(reqItems)
        return

    def OnColumnResize(self, newCols):
        for container, width in zip(self.children[:], newCols):
            container.width = width

        self.sr.reqItems.width = self.sr.reqItems.parent.width
        self.sr.rewardLabel.width = self.sr.rewardParent.width - self.sr.rewardIconParent.width - self.sr.rewardLabel.left - self.labelMargin

    def GetHeight(_self, node, width):
        node.height = LPOfferEntry.entryHeight
        return node.height

    def GetColumnWidth(_self, node, column):
        if not hasattr(LPOfferEntry, 'columnWidths'):
            LPOfferEntry.columnWidths = {}
            LPOfferEntry.columnWidths[localization.GetByLabel('UI/LPStore/Reward')] = REWARD_COLUMN_WIDTH
            requirements = sm.GetService('lpstore').GetRequirements()
            for requirementColumn in requirements:
                costLabelPath = requirementColumn.costLabelPath
                if costLabelPath:
                    costLabel = localization.GetByLabel(costLabelPath)
                    columnWidth = COST_COLUMN_WIDTH
                    LPOfferEntry.columnWidths[costLabel] = columnWidth

            LPOfferEntry.columnWidths[localization.GetByLabel('UI/LPStore/RequiredItems')] = REQUIRED_ITEMS_COLUMN_WIDTH
            LPOfferEntry.columnWidths[localization.GetByLabel('UI/VirtualGoodsStore/Buttons/Buy')] = BUY_OPTION_COLUMN_WIDTH
        return LPOfferEntry.columnWidths[column]


class RequiredItem(uiprimitives.Container):
    __guid__ = 'lpstore.RequiredItem'
    default_name = 'reqItemEntry'
    default_align = uiconst.TOTOP
    default_height = 16
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        uiprimitives.Container.ApplyAttributes(self, attributes)
        par = uiprimitives.Container(name='cannotParent', parent=self, state=uiconst.UI_PICKCHILDREN, width=18, align=uiconst.TOLEFT)
        self.sr.cannotIcon = uicontrols.Icon(icon='ui_38_16_194', parent=par, hint=localization.GetByLabel('UI/LPStore/HintRequiredItemsMissing'), align=uiconst.CENTER, name='cannotIcon')
        par = uiprimitives.Container(name='infoParent', state=uiconst.UI_PICKCHILDREN, parent=self, align=uiconst.TORIGHT, width=18)
        self.sr.infoIcon = InfoIcon(name='infoIcon', parent=par, align=uiconst.CENTER)
        par = uiprimitives.Container(parent=self, name='labelClipper', clipChildren=True, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.sr.label = LPStoreEntryLabel(parent=par, name='label', maxLines=1, align=uiconst.CENTERLEFT)


class LPStoreWindow(uicontrols.Window):
    __guid__ = 'form.LPStore'
    __notifyevents__ = ['OnLPStoreFilterChange', 'OnLPStoreCurrentPresetChange', 'OnLPStorePresetsChange']
    default_windowID = 'lpstore'
    default_captionLabelPath = 'Tooltips/StationServices/LPStore'
    default_descriptionLabelPath = 'Tooltips/StationServices/LPStore_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/lpstore.png'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetWndIcon(self.iconNum)
        self.SetTopparentHeight(61)
        self.SetMinSize((685, 300))
        self.ConstructHeader()
        self.ConstructContent()

    def OnUIRefresh(self):
        pass

    def ConstructHeader(self):
        self.sr.topParent.state = uiconst.UI_PICKCHILDREN
        self.sr.corpLabel = uicontrols.Label(parent=self.sr.topParent, name='corpLabel', align=uiconst.TOPRIGHT, fontsize=18, left=10, state=uiconst.UI_NORMAL)
        self.sr.corpLPsLabel = uicontrols.EveLabelMedium(parent=self.sr.topParent, name='corpLPsLabel', align=uiconst.TOPRIGHT, left=10, state=uiconst.UI_NORMAL)
        xchangeRate = sm.GetService('lpstore').GetConcordLPExchangeRate()
        self.sr.exchangeButton = uicontrols.Button(parent=self.sr.topParent, name='exchangeBtn', align=uiconst.TOPRIGHT, left=5, label=localization.GetByLabel('UI/LPStore/ConcordExchange'))
        filterParent = uiprimitives.Container(parent=self.sr.topParent, name='filterParent', pos=(60, 0, 200, 55), align=uiconst.RELATIVE)
        self.sr.presetCombo = uicontrols.Combo(parent=filterParent, name='presetCombo', left=5, top=20, adjustWidth=True, label=localization.GetByLabel('UI/LPStore/OfferFilter'))
        self.sr.filterBtn = uicontrols.Button(parent=filterParent, name='filterBtn', left=5, top=self.sr.presetCombo.top + self.sr.presetCombo.height + const.defaultPadding, label=localization.GetByLabel('UI/LPStore/EditFilters'))

    def ConstructContent(self):
        self.sr.lpStoreScroll = uicontrols.Scroll(parent=self.sr.main, name='lpStoreScroll', align=uiconst.TOALL, padding=const.defaultPadding)
        self.sr.lpStoreScroll.sr.id = 'blada'

    def RefreshIfNotAlready(self):
        self.sr.filterBtn.OnClick = lambda *blah: self.OpenFilters()
        self.InitOfferRefreshDespammer()
        self.Refresh()
        self.sr.presetCombo.OnChange = self.OnPresetComboChange

    RefreshIfNotAlready = util.RunOnceMethod(RefreshIfNotAlready)

    def Refresh(self):
        self.ShowLoad()
        try:
            self.factionID = sm.GetService('map').GetItem(eve.session.solarsystemid2).factionID
            self.RefreshPresets()
            self.sr.corpLabel.text = sm.GetService('lpstore').GetCurrentCorpName()
            self.sr.corpLPsLabel.text = localization.GetByLabel('UI/LPStore/CurrentLPs', lpAmount=sm.GetService('lpstore').GetMyLPs())
            self.sr.corpLPsLabel.top = self.sr.corpLabel.top + self.sr.corpLabel.height
            self.sr.exchangeButton.top = self.sr.corpLPsLabel.top + self.sr.corpLPsLabel.height
            self.SetTopparentHeight(self.sr.exchangeButton.top + self.sr.exchangeButton.height + 4)
        finally:
            self.HideLoad()

        lpSvc = sm.GetService('lpstore')
        exchangeRate = lpSvc.GetConcordLPExchangeRate()
        if exchangeRate is not None and exchangeRate > 0.0 and lpSvc.GetMyConcordLPs() * exchangeRate > 1:
            self.EnableExchangeButton()
        else:
            self.DisableExchangeButton()
        self.RefreshOffers()
        return

    def _OnClose(self, *etc):
        self.ReleaseOfferRefreshDespammer()

    def OpenFilters(self):
        wnd = LPStoreFiltersWindow.Open()

    def OpenConcordExchange(self):
        self.DisableExchangeButton(suppressHint=True)
        sm.GetService('lpstore').OpenConcordExchange(eve.stationItem.ownerID)

    def DisableExchangeButton(self, suppressHint=False):
        self.sr.exchangeButton.Disable()
        self.sr.exchangeButton.OnClick = None
        lpSvc = sm.GetService('lpstore')
        fromCorpName = cfg.eveowners.Get(const.ownerCONCORD).ownerName
        toCorpName = cfg.eveowners.Get(lpSvc.cache.corpID).ownerName
        if suppressHint:
            self.sr.exchangeButton.SetHint('')
        else:
            exchangeRate = lpSvc.GetConcordLPExchangeRate()
            if exchangeRate is None or exchangeRate == 0.0:
                hint = localization.GetByLabel('UI/LPStore/ExchangeRateNotDefined', fromCorpName=fromCorpName, toCorpName=toCorpName)
            elif fromCorpName == toCorpName:
                hint = localization.GetByLabel('UI/LPStore/ExchangeProhibited', fromCorpName=fromCorpName)
            else:
                hint = localization.GetByLabel('UI/LPStore/ExchangeUnavailable', fromCorpName=fromCorpName, toCorpName=toCorpName)
            self.sr.exchangeButton.SetHint(hint)
        return

    def EnableExchangeButton(self):
        self.sr.exchangeButton.Enable()
        self.sr.exchangeButton.OnClick = lambda *discard: self.OpenConcordExchange()
        fromCorpName = cfg.eveowners.Get(const.ownerCONCORD).ownerName
        toCorpName = cfg.eveowners.Get(sm.GetService('lpstore').cache.corpID).ownerName
        exchangeRate = sm.GetService('lpstore').GetConcordLPExchangeRate()
        self.sr.exchangeButton.SetHint(localization.GetByLabel('UI/LPStore/ConvertLPMsg', toCorpName=toCorpName, exchangeRate=exchangeRate, fromCorpName=fromCorpName))

    def InitOfferRefreshDespammer(self):

        def RefreshOffers():
            self.ShowLoad()
            try:
                filters = sm.GetService('lpstore').GetCurrentFilters()
                scroll = self.sr.lpStoreScroll
                pos = scroll.GetScrollProportion()
                offers = [ listentry.Get('LPOffer', offer) for offer in sm.GetService('lpstore').GetOffers() if self.Check(offer, filters) ]
                self.sr.lpStoreScroll.sr.minColumnWidth = self._GetMinColumnWidths()
                scroll.LoadContent(headers=self._GetHeaders(), contentList=offers, customColumnWidths=True, noContentHint=localization.GetByLabel('UI/LPStore/NoMatchingOffers'))
                columnWidthSettingsVersion = 1
                settingsKey = 'columnWidthsReset_%s' % columnWidthSettingsVersion
                if offers and not settings.user.ui.Get(settingsKey, False):
                    scroll.ResetColumnWidths()
                    settings.user.ui.Set(settingsKey, True)
                scroll.ScrollToProportion(pos)
            finally:
                self.HideLoad()

        self.offerRefreshDespammer = util.Despammer(RefreshOffers, delay=200)
        self.RefreshOffers = self.offerRefreshDespammer.Send

    def _GetHeaders(self):
        headers = []
        headers.append(localization.GetByLabel('UI/LPStore/Reward'))
        requirements = sm.GetService('lpstore').GetRequirements()
        for requirementColumn in requirements:
            costLabelPath = requirementColumn.costLabelPath
            if costLabelPath:
                costLabel = localization.GetByLabel(costLabelPath)
                headers.append(costLabel)

        headers.append(localization.GetByLabel('UI/LPStore/RequiredItems'))
        headers.append(localization.GetByLabel('UI/VirtualGoodsStore/Buttons/Buy'))
        return headers

    def _GetMinColumnWidths(self):
        minColumnWidths = {}
        minColumnWidths[localization.GetByLabel('UI/LPStore/Reward')] = REWARD_COLUMN_WIDTH_MIN
        requirements = sm.GetService('lpstore').GetRequirements()
        for requirementColumn in requirements:
            costLabelPath = requirementColumn.costLabelPath
            if costLabelPath:
                costLabel = localization.GetByLabel(costLabelPath)
                minColumnWidths[costLabel] = COST_COLUMN_WIDTH_MIN

        minColumnWidths[localization.GetByLabel('UI/LPStore/RequiredItems')] = REQUIRED_ITEMS_COLUMN_WIDTH_MIN
        minColumnWidths[localization.GetByLabel('UI/VirtualGoodsStore/Buttons/Buy')] = BUY_OPTION_COLUMN_WIDTH_MIN
        return minColumnWidths

    def ReleaseOfferRefreshDespammer(self):
        uthread.new(self.offerRefreshDespammer.Stop)
        del self.offerRefreshDespammer

    def OnPresetComboChange(self, blah, bleh, label):
        if label == localization.GetByLabel('UI/LPStore/PresetNone'):
            self.OpenFilters()
        else:
            sm.GetService('lpstore').ChangeCurrentPreset(label)

    def OnLPStoreFilterChange(self):
        self.RefreshOffers()

    def OnLPStorePresetsChange(self):
        self.RefreshPresets()

    def OnLPStoreCurrentPresetChange(self):
        self.RefreshPresets()

    def RefreshPresets(self):
        self.ShowLoad()
        try:
            self.sr.presetCombo.LoadOptions([ (preset.label, preset.label) for preset in sm.GetService('lpstore').GetPresets() ], select=sm.GetService('lpstore').GetCurrentPresetLabel())
        finally:
            self.HideLoad()

    def Check(self, offer, filters):
        for name, val in filters.iteritems():
            if not getattr(self, 'Check_%s' % name)(offer, val):
                return False

        return True

    def CategoryFromType(self, typeID):
        return evetypes.GetCategoryID(typeID)

    def GroupFromType(self, typeID):
        return evetypes.GetGroupID(typeID)

    def Check_rewardCategory(self, offer, val):
        return self.CategoryFromType(offer.typeID) == val

    def Check_rewardGroup(self, offer, val):
        return self.GroupFromType(offer.typeID) == val

    def Check_rewardType(self, offer, val):
        return offer.typeID == val

    def Check_reqCategory(self, offer, val):
        for typeID, qty in offer.reqItems:
            if self.CategoryFromType(typeID) == val:
                return True

        return False

    def Check_reqGroup(self, offer, val):
        for typeID, qty in offer.reqItems:
            if self.GroupFromType(typeID) == val:
                return True

        return False

    def Check_reqType(self, offer, val):
        for typeID, qty in offer.reqItems:
            if typeID == val:
                return True

        return False

    def Check_reqIllegal(self, offer, val):
        for typeID, qty in offer.reqItems:
            if self.factionID in inventorycommon.typeHelpers.GetIllegality(typeID):
                return False

        return True

    def Check_reqNotInHangar(self, offer, val):
        for typeID, qty in offer.reqItems:
            if not sm.GetService('lpstore').HaveItem(typeID, qty):
                return False

        return True

    def Check_minLP(self, offer, val):
        return offer.lpCost >= val

    def Check_maxLP(self, offer, val):
        return offer.lpCost <= val

    def Check_minISK(self, offer, val):
        return offer.iskCost >= val

    def Check_maxISK(self, offer, val):
        return offer.iskCost <= val

    def Check_minAnalysisKredits(self, offer, val):
        analysisKreditsCost = getattr(offer, 'akCost', None)
        if analysisKreditsCost:
            return analysisKreditsCost >= val
        else:
            return False

    def Check_maxAnalysisKredits(self, offer, val):
        analysisKreditsCost = getattr(offer, 'akCost', None)
        if analysisKreditsCost:
            return analysisKreditsCost <= val
        else:
            return True

    def Check_dynamicMaxLP(self, offer, val):
        return self.Check_maxLP(offer, sm.GetService('lpstore').GetMyLPs())

    def Check_dynamicMaxISK(self, offer, val):
        return self.Check_maxISK(offer, sm.GetService('lpstore').GetMyISK())

    def Check_dynamicMaxAnalysisKredits(self, offer, val):
        return self.Check_maxAnalysisKredits(offer, sm.GetService('lpstore').GetMyAnalysisKredits())


class LPStoreFiltersWindow(uicontrols.Window):
    __guid__ = 'form.LPStoreFilters'
    __notifyevents__ = ['OnLPStoreCurrentPresetChange', 'OnLPStorePresetsChange']
    comboParentHeight = 40
    editParentHeight = 40
    checkboxParentHeight = 20
    comboSeparatorHeight = 16
    editSeparatorHeight = 18
    labelSeparatorHeight = 2
    labelParentHeight = 15
    scrollSeparatorHeight = 6
    comboWidth = 120
    default_windowID = 'lpfilter'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/LPStore/Filters'))
        self.SetMinSize([380, 260])
        self.SetTopparentHeight(0)
        self.SetScope('station')
        try:
            self.ConstructContent()
        except Exception as e:
            import log
            log.LogException(e)
            raise

        self.filters = {}
        self.resetters = []
        self.OnEdited = self.OnEdited_Inactive
        self.HookCombos()
        self.HookEdits()
        self.HookCheckboxes()
        self.MakeButtons()
        self.InitPresetsScroll()
        self.RefreshCurrentPresetLabel()
        self.OnEdited = self.OnEdited_Active
        self.SyncInputs()

    def ConstructContent(self):
        main = uiprimitives.Container(parent=self.sr.main, name='TabPanelGroupParent', align=uiconst.TOALL)
        tabGroup = uicontrols.TabGroup(parent=main, name='tabs')
        margin = 0
        xmargin = 6
        ymargin = 6
        innermargin = 4
        panelParent = uiprimitives.Container(parent=main, align=uiconst.TOALL, name='panelParent', state=uiconst.UI_PICKCHILDREN, padding=[const.defaultPadding] * 4)
        tabs = []
        self._MakeRewardTab(tabs, panelParent)
        self._MakeLpCostTab(tabs, panelParent)
        self._MakeIskCostTab(tabs, panelParent)
        self._MakeAnalysisKreditsCostTab(tabs, panelParent)
        self._MakeRequiredItemsTab(tabs, panelParent)
        self._MakeFilterPresetsTab(tabs, panelParent)
        tabGroup.Startup(tabs)

    def _MakeTab(self, tabs, panelParent, caption):

        def MakeOnTabSelect(panelWr):

            def OnTabSelect(*args):
                panel = panelWr()
                panel.state = uiconst.UI_PICKCHILDREN
                for sibling in panel.parent.children:
                    if sibling is not panelWr():
                        sibling.state = uiconst.UI_HIDDEN

            return OnTabSelect

        panel = uiprimitives.Container(parent=panelParent, name=caption, align=uiconst.TOALL)
        panel.OnTabSelect = MakeOnTabSelect(weakref.ref(panel))
        tabs.append((caption,
         panel,
         None,
         (caption + '_args',)))
        return panel

    def _MakeRewardTab(self, tabs, panelParent):
        tab = self._MakeTab(tabs, panelParent, localization.GetByLabel('UI/LPStore/Reward'))
        uiprimitives.Container(parent=tab, name='rewardComboSeparator', height=self.comboSeparatorHeight, align=uiconst.TOTOP, state=uiconst.UI_DISABLED)
        rewardCategoryComboParent = uiprimitives.Container(parent=tab, name='rewardCategoryComboParent', height=self.comboParentHeight, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        self.sr.rewardCategoryCombo = uicontrols.Combo(parent=rewardCategoryComboParent, name='rewardCategoryCombo', label=localization.GetByLabel('UI/Common/Category'), width=self.comboWidth, align=uiconst.RELATIVE)
        rewardGroupComboParent = uiprimitives.Container(parent=tab, name='rewardGroupComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.rewardGroupCombo = uicontrols.Combo(parent=rewardGroupComboParent, name='rewardGroupCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Group'))
        rewardTypeComboParent = uiprimitives.Container(parent=tab, name='rewardTypeComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.rewardTypeCombo = uicontrols.Combo(parent=rewardTypeComboParent, name='rewardTypeCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Type'))

    def _MakeLpCostTab(self, tabs, panelParent):
        tab = self._MakeTab(tabs, panelParent, localization.GetByLabel('UI/LPStore/LPCost'))
        uiprimitives.Container(parent=tab, name='lpCostEditSeparator', height=self.editSeparatorHeight, align=uiconst.TOTOP)
        minLPEditParent = uiprimitives.Container(parent=tab, name='minLPEditParent', height=self.editParentHeight, align=uiconst.TOTOP)
        self.sr.minLPEdit = uicontrols.SinglelineEdit(parent=minLPEditParent, name='minLPEdit', label=localization.GetByLabel('UI/LPStore/MinLPCost'), ints=[0, None])
        maxLPEditParent = uiprimitives.Container(parent=tab, name='maxLPEditParent', height=self.editParentHeight, align=uiconst.TOTOP)
        self.sr.maxLPEdit = uicontrols.SinglelineEdit(parent=maxLPEditParent, name='maxLPEdit', label=localization.GetByLabel('UI/LPStore/MaxLPCost'), ints=[0, None])
        return

    def _MakeIskCostTab(self, tabs, panelParent):
        tab = self._MakeTab(tabs, panelParent, localization.GetByLabel('UI/LPStore/ISKCost'))
        uiprimitives.Container(parent=tab, name='iskCostEditSeparator', height=self.editSeparatorHeight, align=uiconst.TOTOP)
        minISKEditParent = uiprimitives.Container(parent=tab, name='minISKEditParent', height=self.editParentHeight, align=uiconst.TOTOP)
        self.sr.minISKEdit = uicontrols.SinglelineEdit(parent=minISKEditParent, name='minISKEdit', label=localization.GetByLabel('UI/LPStore/MinISKCost'), ints=[0, None])
        maxISKEditParent = uiprimitives.Container(parent=tab, name='maxISKEditParent', height=self.editParentHeight, align=uiconst.TOTOP)
        self.sr.maxISKEdit = uicontrols.SinglelineEdit(parent=maxISKEditParent, name='maxISKEdit', label=localization.GetByLabel('UI/LPStore/MaxISKCost'), ints=[0, None])
        return

    def _MakeAnalysisKreditsCostTab(self, tabs, panelParent):
        tab = self._MakeTab(tabs, panelParent, localization.GetByLabel('UI/LPStore/AKCost'))
        uiprimitives.Container(parent=tab, name='akCostEditSeparator', height=self.editSeparatorHeight, align=uiconst.TOTOP)
        minAnalysisKreditsEditParent = uiprimitives.Container(parent=tab, name='minAnalysisKreditsEditParent', height=self.editParentHeight, align=uiconst.TOTOP)
        self.sr.minAnalysisKreditsEdit = uicontrols.SinglelineEdit(parent=minAnalysisKreditsEditParent, name='minAnalysisKreditsEdit', label=localization.GetByLabel('UI/LPStore/MinAKCost'), ints=[0, None])
        maxAnalysisKreditsEditParent = uiprimitives.Container(parent=tab, name='maxAnalysisKreditsEditParent', height=self.editParentHeight, align=uiconst.TOTOP)
        self.sr.maxAnalysisKreditsEdit = uicontrols.SinglelineEdit(parent=maxAnalysisKreditsEditParent, name='maxAnalysisKreditsEdit', label=localization.GetByLabel('UI/LPStore/MaxAKCost'), ints=[0, None])
        return

    def _MakeRequiredItemsTab(self, tabs, panelParent):
        tab = self._MakeTab(tabs, panelParent, localization.GetByLabel('UI/LPStore/RequiredItems'))
        reqItemsHeaderParent = uiprimitives.Container(parent=tab, name='reqItemsHeaderParent', height=18, align=uiconst.TOTOP)
        LPStoreHeaderLabel(parent=reqItemsHeaderParent, text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsHeader'))
        reqIllegalCbParent = uiprimitives.Container(parent=tab, name='reqIllegalCbParent', height=self.checkboxParentHeight, align=uiconst.TOTOP)
        self.sr.reqIllegalCb = uicontrols.Checkbox(parent=reqIllegalCbParent, name='reqIllegalCb', text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsAreIllegal'), align=uiconst.TOTOP)
        reqNotInHangarCbParent = uiprimitives.Container(parent=tab, name='reqNotInHangarCbParent', height=self.checkboxParentHeight, align=uiconst.TOTOP)
        self.sr.reqNotInHangarCb = uicontrols.Checkbox(parent=reqNotInHangarCbParent, name='reqNotInHangarCb', text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsNotInHangar'), align=uiconst.TOTOP)
        uiprimitives.Container(parent=tab, name='reqItemsOrMatchTypeLabelSeparator', height=10, align=uiconst.TOTOP)
        reqItemsOrMatchTypeLabelParent = uiprimitives.Container(parent=tab, name='reqItemsOrMatchTypeLabelParent', height=16, align=uiconst.TOTOP)
        LPStoreHeaderLabel(parent=reqItemsOrMatchTypeLabelParent, text=localization.GetByLabel('UI/LPStore/FilterRequiredItemsType'), height=16)
        uiprimitives.Container(parent=tab, name='reqComboSeparator', height=self.comboSeparatorHeight, align=uiconst.TOTOP)
        reqCategoryComboParent = uiprimitives.Container(parent=tab, name='reqCategoryComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.reqCategoryCombo = uicontrols.Combo(parent=reqCategoryComboParent, name='reqCategoryCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Category'))
        reqGroupComboParent = uiprimitives.Container(parent=tab, name='reqGroupComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.reqGroupCombo = uicontrols.Combo(parent=reqGroupComboParent, name='reqGroupCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Group'))
        reqTypeComboParent = uiprimitives.Container(parent=tab, name='reqTypeComboParent', height=self.comboParentHeight, align=uiconst.TOTOP)
        self.sr.reqTypeCombo = uicontrols.Combo(parent=reqTypeComboParent, name='reqTypeCombo', width=self.comboWidth, label=localization.GetByLabel('UI/Common/Type'))

    def _MakeFilterPresetsTab(self, tabs, panelParent):
        tab = self._MakeTab(tabs, panelParent, localization.GetByLabel('UI/LPStore/FilterPresets'))
        uiprimitives.Container(parent=tab, name='presetsHeaderSeparator', height=self.labelSeparatorHeight, align=uiconst.TOTOP)
        currentPresetHeaderParent = uiprimitives.Container(parent=tab, name='currentPresetHeaderParent', height=16, align=uiconst.TOTOP)
        LPStoreHeaderLabel(name='currentPresetHeader', parent=currentPresetHeaderParent, text=localization.GetByLabel('UI/LPStore/ActivePresetName'))
        currentPresetLabelParent = uiprimitives.Container(parent=tab, name='currentPresetLabelParent', height=16, align=uiconst.TOTOP)
        self.sr.currentPresetLabel = LPStoreLabel(name='currentPresetLabel', parent=currentPresetLabelParent, text=localization.GetByLabel('UI/LPStore/PresetAll'))
        btnsGrandParent = uiprimitives.Container(parent=tab, name='btnsGrandParent', height=15, align=uiconst.TOBOTTOM)
        self.sr.btnsParent = uiprimitives.Container(parent=btnsGrandParent, name='btnsParent', height=20, width=200, align=uiconst.CENTER, state=uiconst.UI_PICKCHILDREN)
        uiprimitives.Container(parent=tab, name='presetsScrollSeparator', height=self.scrollSeparatorHeight, align=uiconst.TOTOP)
        uiprimitives.Container(parent=tab, name='presetsScrollSeparator', height=self.scrollSeparatorHeight, align=uiconst.TOBOTTOM)
        self.sr.presetsScroll = uicontrols.Scroll(name='presetsScroll', parent=tab, align=uiconst.TOALL)

    def HookCombos(self):
        all = [(localization.GetByLabel('UI/Common/All'), 'all')]

        def MakeOnTypeComboChange(filterKey):

            def OnTypeComboChange(blah, bleh, id):
                if id == 'all':
                    util.TryDel(self.filters, filterKey)
                else:
                    self.filters[filterKey] = id
                self.OnEdited()

            return OnTypeComboChange

        def GetGroupChoices(categoryID):
            ret = []
            for groupID in evetypes.GetGroupIDsByCategory(categoryID):
                if evetypes.IsGroupPublishedByGroup(groupID):
                    ret.append((evetypes.GetGroupNameByGroup(groupID), groupID))

            ret.sort()
            return ret

        def GetTypeChoices(groupID):
            ret = []
            for typeID in evetypes.GetTypeIDsByGroup(groupID):
                if evetypes.IsPublished(typeID):
                    ret.append((evetypes.GetName(typeID), typeID))

            ret.sort()
            return ret

        def MakeOnCategoryComboChange(filterKey, dependant):

            def OnCategoryComboChange(blah, bleh, id):
                if id == 'all':
                    util.TryDel(self.filters, filterKey)
                else:
                    self.filters[filterKey] = id
                if dependant is not None:
                    if id == 'all':
                        dependant.state = uiconst.UI_HIDDEN
                    else:
                        dependant.state = uiconst.UI_NORMAL
                        dependant.LoadOptions(all + GetGroupChoices(id))
                    dependant.OnChange(None, None, 'all')
                self.OnEdited()
                return

            return OnCategoryComboChange

        def MakeOnGroupComboChange(filterKey, dependant):

            def OnCategoryComboChange(blah, bleh, id):
                if id == 'all':
                    util.TryDel(self.filters, filterKey)
                else:
                    self.filters[filterKey] = id
                if dependant is not None:
                    if id == 'all':
                        dependant.state = uiconst.UI_HIDDEN
                    else:
                        dependant.state = uiconst.UI_NORMAL
                        dependant.LoadOptions(all + GetTypeChoices(id))
                    dependant.OnChange(None, None, 'all')
                self.OnEdited()
                return

            return OnCategoryComboChange

        categories = []
        for categoryID in evetypes.GetAllCategoryIDs():
            if evetypes.IsCategoryPublishedByCategory(categoryID):
                categories.append((evetypes.GetCategoryNameByCategory(categoryID), categoryID))

        categories.sort()
        typeSuites = ('reward', 'req')
        for typeSuite in typeSuites:
            typeCombo = self.sr.Get('%sTypeCombo' % typeSuite)
            groupCombo = self.sr.Get('%sGroupCombo' % typeSuite)
            categCombo = self.sr.Get('%sCategoryCombo' % typeSuite)
            typeCombo.OnChange = MakeOnTypeComboChange(typeSuite + 'Type')
            groupCombo.OnChange = MakeOnGroupComboChange(typeSuite + 'Group', typeCombo)
            categCombo.OnChange = MakeOnCategoryComboChange(typeSuite + 'Category', groupCombo)
            categCombo.LoadOptions(all + categories)
            categCombo.OnChange(None, None, 'all')

        def ResetCombos():
            for typeSuite in typeSuites:
                for metaType in ('Type', 'Group', 'Category'):
                    combo = self.sr.Get('%s%sCombo' % (typeSuite, metaType))
                    setting = self.filters.get(typeSuite + metaType, 'all')
                    combo.SelectItemByValue(setting)
                    combo.OnChange(None, None, setting)

            return

        self.resetters.append(ResetCombos)
        return

    def HookEdits(self):

        def MakeOnEditChange(key, type_):

            def OnEditChange(s):
                if s and s != '-':
                    self.filters[key] = type_(s)
                else:
                    util.TryDel(self.filters, key)
                self.OnEdited()

            return OnEditChange

        keysTypes = [('minLP', int),
         ('maxLP', int),
         ('minISK', int),
         ('maxISK', int),
         ('minAnalysisKredits', int),
         ('maxAnalysisKredits', int)]
        for key, type_ in keysTypes:
            self.sr.Get(key + 'Edit').OnChange = MakeOnEditChange(key, type_)

        def ResetEdits():
            for key, type_ in keysTypes:
                edit = self.sr.Get(key + 'Edit')
                if key in self.filters:
                    edit.SetValue(self.filters[key])
                else:
                    edit.SetText('', format=False)

        self.resetters.append(ResetEdits)

    def HookCheckboxes(self):

        def MakeOnCheckboxChange(key):

            def OnCheckboxChange(cb):
                if cb.checked:
                    self.filters[key] = True
                else:
                    util.TryDel(self.filters, key)
                self.OnEdited()

            return OnCheckboxChange

        keys = ('reqIllegal', 'reqNotInHangar')
        for key in keys:
            self.sr.Get(key + 'Cb').OnChange = MakeOnCheckboxChange(key)

        def ResetCheckboxes():
            for key in keys:
                self.sr.Get(key + 'Cb').SetChecked(self.filters.get(key, False))

        self.resetters.append(ResetCheckboxes)

    def MakeButtons(self):
        buttonSeparation = 0
        for btnID, labelString, OnClick, hint in [('new',
          localization.GetByLabel('UI/Common/Buttons/New'),
          self.OnClickNew,
          localization.GetByLabel('UI/LPStore/HintNewPreset')),
         ('load',
          localization.GetByLabel('UI/Common/Buttons/Load'),
          self.OnClickLoad,
          localization.GetByLabel('UI/LPStore/HintLoadPreset')),
         ('overwrite',
          localization.GetByLabel('UI/Common/Buttons/Overwrite'),
          self.OnClickOverwrite,
          localization.GetByLabel('UI/LPStore/HintOverwritePreset')),
         ('del',
          localization.GetByLabel('UI/Common/Buttons/Delete'),
          self.OnClickDelete,
          localization.GetByLabel('UI/LPStore/HintDeletePreset'))]:
            parent = LPStoreButton(parent=self.sr.btnsParent, name='%sbtnParent' % btnID, label=labelString, hint=localization.GetByLabel('UI/LPStore/HintDeletePreset'))
            btn = parent.sr.btn
            setattr(self.sr, '%sBtn' % btnID, btn)
            btn.sr.hint = hint
            btn.OnClick = OnClick

        maxw = max([ par.sr.btn.width for par in self.sr.btnsParent.children ])
        for par in self.sr.btnsParent.children:
            par.sr.btn.width = maxw
            par.width = maxw + buttonSeparation

        self.sr.btnsParent.width = sum([ child.width for child in self.sr.btnsParent.children ])
        self.RefreshVisibleButtons()

    def InitPresetsScroll(self):
        self.sr.presetsScroll.multiSelect = False
        self.sr.presetsScroll.OnSelectionChange = self.OnPresetsScrollSelectionChange
        self.RefreshPresetsScroll()

    def OnLPStorePresetsChange(self):
        self.RefreshPresetsScroll()

    def RefreshPresetsScroll(self):
        self.sr.presetsScroll.Load(contentList=[ listentry.Get('Generic', data=preset) for preset in sm.GetService('lpstore').GetPresets() if preset.label != localization.GetByLabel('UI/LPStore/PresetNone') ])

    def OnPresetsScrollSelectionChange(self, *etc):
        self.RefreshVisibleButtons()

    def RefreshVisibleButtons(self):
        sel = self.sr.presetsScroll.GetSelected()
        if not sel:
            self.sr.loadBtn.state = uiconst.UI_HIDDEN
            self.sr.overwriteBtn.state = uiconst.UI_HIDDEN
            self.sr.delBtn.state = uiconst.UI_HIDDEN
        elif not sel[0].editable:
            self.sr.loadBtn.state = uiconst.UI_NORMAL
            self.sr.overwriteBtn.state = uiconst.UI_HIDDEN
            self.sr.overwriteBtn.state = uiconst.UI_HIDDEN
            self.sr.delBtn.state = uiconst.UI_HIDDEN
        else:
            self.sr.loadBtn.state = uiconst.UI_NORMAL
            self.sr.overwriteBtn.state = uiconst.UI_NORMAL
            self.sr.delBtn.state = uiconst.UI_NORMAL

    def OnClickNew(self, *blah):

        def Validate(data):
            name = data
            if not name:
                return localization.GetByLabel('UI/LPStore/ErrorNoName', cancelLabel=localization.GetByLabel('UI/Common/Buttons/Cancel'))
            if name in [ preset.label for preset in sm.GetService('lpstore').GetPresets() ]:
                return localization.GetByLabel('UI/LPStore/ErrorExistingName', overwriteLabel=localization.GetByLabel('UI/Common/Buttons/Overwrite'))

        result = uiutil.NamePopup(maxLength=50, validator=Validate)
        if result:
            sm.GetService('lpstore').AddPreset(result, self.filters.copy())

    def SelectedPreset(self):
        return self.sr.presetsScroll.GetSelected()[0]

    def OnClickLoad(self, *blah):
        self.LoadPreset(self.SelectedPreset())

    def LoadPreset(self, preset):
        sm.GetService('lpstore').ChangeCurrentPreset(preset.label)

    def OnLPStoreCurrentPresetChange(self):
        self.RefreshCurrentPresetLabel()
        if sm.GetService('lpstore').GetCurrentPresetLabel() != localization.GetByLabel('UI/LPStore/PresetNone'):
            self.SyncInputs()

    def SyncInputs(self):
        self.OnEdited = self.OnEdited_Inactive
        try:
            self.filters = sm.GetService('lpstore').GetCurrentFilters()
            for Reset in self.resetters:
                Reset()

        finally:
            self.OnEdited = self.OnEdited_Active

    def RefreshCurrentPresetLabel(self):
        self.sr.currentPresetLabel.text = sm.GetService('lpstore').GetCurrentPresetLabel()

    def OnClickOverwrite(self, *blah):
        self.OverwritePreset(self.SelectedPreset())

    def OverwritePreset(self, preset):
        if eve.Message('ConfirmOverwriteLPStoreFilterPreset', {}, uiconst.OKCANCEL, uiconst.ID_OK) == uiconst.ID_OK:
            sm.GetService('lpstore').OverwritePreset(preset.label, self.filters)

    def OnClickDelete(self, *blah):
        self.DeletePreset(self.SelectedPreset())
        self.RefreshVisibleButtons()

    def DeletePreset(self, preset):
        if eve.Message('ConfirmDeleteLPStoreFilterPreset', {}, uiconst.OKCANCEL, uiconst.ID_OK) == uiconst.ID_OK:
            sm.GetService('lpstore').DeletePreset(preset.label)
            self.RefreshPresetsScroll()

    def OnEdited_Active(self):
        sm.GetService('lpstore').ChangeFilters(self.filters)

    def OnEdited_Inactive(self):
        pass


class LPExhangeDialog(uicontrols.Window):
    __guid__ = 'form.LPExhangeDialog'
    __notifyevents__ = ['OnLPStoreFilterChange', 'OnLPStoreCurrentPresetChange', 'OnLPStorePresetsChange']

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.scope = 'station'
        self.SetWndIcon(None)
        self.SetTopparentHeight(0)
        self.SetSize(300, 225)
        self.MakeUnResizeable()
        self.MakeUnMinimizable()
        self.MakeUncollapseable()
        self.MakeUnpinable()
        self.toCorpID = attributes.Get('toCorpID')
        self.toCorpName = cfg.eveowners.Get(self.toCorpID).ownerName
        self.fromCorpName = cfg.eveowners.Get(attributes.get('fromCorpID', const.ownerCONCORD)).ownerName
        self.currentFromCorpLPs = attributes.get('currentFromCorpLPs')
        self.currentToCorpLPs = attributes.get('currentToCorpLPs')
        self.exchangeRate = attributes.get('exchangeRate')
        self.maxCorporationLPs = int(self.currentFromCorpLPs * self.exchangeRate)
        self.SetCaption(localization.GetByLabel('UI/LPStore/LPExchangeDialogTitle'))
        maxLPs = attributes.get('maxLPs', None)
        btns = [[localization.GetByLabel('UI/Common/Buttons/OK'),
          self.OnOK,
          (),
          81], [localization.GetByLabel('UI/Common/Buttons/Cancel'),
          self.OnCancel,
          (),
          81]]
        self.buttons = uicontrols.ButtonGroup(btns=btns, parent=self.sr.main)
        topCont = uiprimitives.Container(name='topCont', parent=self.sr.main, align=uiconst.TOALL, padding=(4, 4, 4, 4))
        LPStoreLabel(parent=topCont, maxLines=None, text=localization.GetByLabel('UI/LPStore/ConvertLPMsg', toCorpName=self.toCorpName, exchangeRate=self.exchangeRate, fromCorpName=self.fromCorpName))
        LPStoreLabel(parent=topCont, text=self.toCorpName, bold=True, top=10)
        cont = uiprimitives.Container(name='toCorpLPAmountContainer', parent=topCont, align=uiconst.TOTOP, pos=(0, 0, 100, 18), state=uiconst.UI_PICKCHILDREN)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/ExchangePurchaseAmount'), align=uiconst.CENTERLEFT)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/LP'), align=uiconst.TORIGHT)
        self.amountEdit = uicontrols.SinglelineEdit(name='lpAmountEdit', parent=cont, pos=(17, 0, 80, 0), ints=(0, self.maxCorporationLPs), align=uiconst.TOPRIGHT)
        self.amountEdit.OnInsert = self.OnChangeEdit
        zeroLP = 0.0
        cont = uiprimitives.Container(name='toCorpCurrentLPContainer', parent=topCont, align=uiconst.TOTOP, height=18)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/Common/Current'), align=uiconst.CENTERLEFT)
        self.toCorpCurrentLP = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        cont = uiprimitives.Container(name='toCorpTotalLPContainer', parent=topCont, align=uiconst.TOTOP, height=18)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/Common/Total'), align=uiconst.CENTERLEFT)
        self.toCorpTotalLP = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        LPStoreLabel(parent=topCont, text=self.fromCorpName, bold=True)
        cont = uiprimitives.Container(name='fromCorpCostLPContainer', parent=topCont, align=uiconst.TOTOP, height=18)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/Common/Cost'), align=uiconst.CENTERLEFT)
        self.fromCorpCostLP = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        cont = uiprimitives.Container(name='fromCorpFinalLPContainer', parent=topCont, align=uiconst.TOTOP, height=18)
        label = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/Common/Remaining'), align=uiconst.CENTERLEFT)
        self.fromCorpFinalLP = LPStoreEntryLabel(parent=cont, text=localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(zeroLP))), align=uiconst.CENTERRIGHT)
        self.SetDetails(1)
        return

    def SetDetails(self, lpToExchange):
        concordLPCost = int(math.ceil(lpToExchange / self.exchangeRate))
        concordLPAfter = self.currentFromCorpLPs - concordLPCost
        corporationLPAfter = self.currentToCorpLPs + lpToExchange
        self.fromCorpCostLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(concordLPCost))))
        self.fromCorpFinalLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(concordLPAfter))))
        self.toCorpTotalLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(corporationLPAfter))))
        self.toCorpCurrentLP.SetText(localization.GetByLabel('UI/LPStore/AmountLP', lpAmount=str(util.FmtAmt(self.currentToCorpLPs))))

    def OnChangeEdit(self, *args):
        self.amountEdit.ClampMinMaxValue()
        self.SetDetails(self.amountEdit.GetValue())

    def OnOK(self):
        try:
            amount = self.amountEdit.GetValue()
            if amount:
                sm.GetService('lpstore').ConvertConcordLP(self.toCorpID, int(self.amountEdit.GetValue()))
        finally:
            self.EnableButton()
            self.Close()

    def _OnClose(self, *args):
        self.EnableButton()

    def OnCancel(self):
        self.Close()

    def EnableButton(self):
        wnd = LPStoreWindow.GetIfOpen()
        if wnd:
            wnd.Refresh()