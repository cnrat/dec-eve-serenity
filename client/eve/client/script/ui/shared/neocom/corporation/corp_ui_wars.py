# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\corporation\corp_ui_wars.py
import uiprimitives
import uicontrols
import util
import uix
import form
import listentry
import uicls
import carbonui.const as uiconst
import localization
import blue
import facwarCommon
import const
from collections import defaultdict
from eve.common.script.sys.rowset import IndexRowset

class CorpWars(uiprimitives.Container):
    __guid__ = 'form.CorpWars'
    __nonpersistvars__ = []

    def Load(self, args):
        if not self.sr.Get('inited', 0):
            self.ourWarsScroll = None
            self.allWarsScroll = None
            self.killReportsScroll = None
            self.sr.inited = 1
            self.maxWarID = const.maxInt
            self.warbatches = []
            self.ourWarsCont = uiprimitives.Container(name='ourWarsCont', parent=self, align=uiconst.TOALL)
            toolbarContainer = uiprimitives.Container(name='toolbarContainer', align=uiconst.TOBOTTOM, parent=self.ourWarsCont, height=22)
            declareButton = uicontrols.ButtonGroup(btns=[[localization.GetByLabel('UI/Corporations/CorporationWindow/Alliances/Rankings/DeclareWar'),
              self.DeclareWar,
              None,
              None]], parent=toolbarContainer)
            self.ourWarsScroll = uicontrols.Scroll(parent=self.ourWarsCont, padding=const.defaultPadding)
            self.allWarsCont = uiprimitives.Container(name='allWarsCont', parent=self, align=uiconst.TOALL)
            allWarsSettingsCont = uiprimitives.Container(name='allWarsSettingsCont', parent=self.allWarsCont, align=uiconst.TOTOP, height=18, top=2)
            browseCont = uiprimitives.Container(name='browseCont', parent=self.allWarsCont, align=uiconst.TOBOTTOM, height=22, padding=(const.defaultPadding,
             0,
             const.defaultPadding,
             0), state=uiconst.UI_NORMAL)
            self.prevBtn = uicls.BrowseButton(parent=browseCont, prev=True, state=uiconst.UI_NORMAL, func=self.BrowseAllWars)
            self.nextBtn = uicls.BrowseButton(parent=browseCont, prev=False, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, func=self.BrowseAllWars)
            self.showCryForHelpCb = uicontrols.Checkbox(parent=allWarsSettingsCont, align=uiconst.TOPLEFT, left=const.defaultPadding, height=14, width=300, configName='allwars_showcryforhelp', text=localization.GetByLabel('UI/Corporations/Wars/ShowCryForHelp'), checked=settings.user.ui.Get('allwars_showcryforhelp', 0), callback=self.CheckBoxChange)
            self.showCryForHelpCb.hint = localization.GetByLabel('UI/Corporations/Wars/NotFilterWhenSearching')
            self.searchButton = uicontrols.Button(parent=allWarsSettingsCont, label=localization.GetByLabel('UI/Corporations/CorporationWindow/Standings/Search'), align=uiconst.TOPRIGHT, pos=(const.defaultPadding,
             2,
             0,
             0), func=self.Search, btn_default=1)
            self.searchEdit = uicontrols.SinglelineEdit(name='edit', parent=allWarsSettingsCont, left=self.searchButton.width + const.defaultPadding * 2, width=150, align=uiconst.TOPRIGHT, maxLength=32)
            self.searchEdit.OnReturn = self.Search
            self.allWarsScroll = uicontrols.Scroll(parent=self.allWarsCont, padding=const.defaultPadding)
            self.killReportsCont = uiprimitives.Container(name='killReportsCont', parent=self, align=uiconst.TOALL)
            killSettingsContainer = uiprimitives.Container(name='killSettingsContainer', parent=self.killReportsCont, align=uiconst.TOTOP, height=20)
            self.killReportQuickFilter = uicls.QuickFilterEdit(parent=killSettingsContainer, left=const.defaultPadding, align=uiconst.CENTERRIGHT, width=150)
            self.killReportQuickFilter.ReloadFunction = self.ReloadKillReports
            combatValues = ((localization.GetByLabel('UI/Corporations/Wars/Killmails/ShowKills'), 0), (localization.GetByLabel('UI/Corporations/Wars/Killmails/ShowLosses'), 1))
            selectedCombatType = settings.user.ui.Get('CorpCombatLogCombo', 0)
            self.combatCombo = uicontrols.Combo(parent=killSettingsContainer, name='combo', select=selectedCombatType, align=uiconst.TOPLEFT, callback=self.OnCombatChange, options=combatValues, idx=0, adjustWidth=True, top=const.defaultPadding, left=const.defaultPadding)
            self.killReportsScroll = uicontrols.Scroll(parent=self.killReportsCont, padding=const.defaultPadding)
            warTabs = [[localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/OurWars'),
              self.ourWarsCont,
              self,
              'our'], [localization.GetByLabel('UI/Corporations/Wars/AllWars'),
              self.allWarsCont,
              self,
              'all'], [localization.GetByLabel('UI/Corporations/Wars/Killmails/KillReports'),
              self.killReportsCont,
              self,
              'killreports']]
            btnContainer = uiprimitives.Container(name='pageBtnContainer', parent=self, align=uiconst.TOBOTTOM, idx=0, padBottom=const.defaultPadding)
            btn = uix.GetBigButton(size=22, where=btnContainer, left=4, top=0, align=uiconst.TORIGHT)
            btn.hint = localization.GetByLabel('UI/Common/ViewMore')
            btn.state = uiconst.UI_HIDDEN
            btn.sr.icon.LoadIcon('ui_23_64_2')
            btn = uix.GetBigButton(size=22, where=btnContainer, left=4, top=0, align=uiconst.TOLEFT)
            btn.hint = localization.GetByLabel('UI/Common/Previous')
            btn.state = uiconst.UI_HIDDEN
            btn.sr.icon.LoadIcon('ui_23_64_1')
            btnContainer.height = max([ c.height for c in btnContainer.children ])
            self.btnContainer = btnContainer
            btnContainer.state = uiconst.UI_HIDDEN
            tabs = uicontrols.TabGroup(name='tabparent', parent=self, idx=0)
            tabs.Startup(warTabs, 'corporationwars')
            self.tabs = tabs
            self.killentries = 25
        sm.GetService('corpui').LoadTop('res:/ui/Texture/WindowIcons/wars.png', localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/WarsTitle'))
        self.myWars = 1
        if not hasattr(self, 'viewingOwnerID'):
            self.viewingOwnerID = eve.session.allianceid or eve.session.corpid
        if not hasattr(self, 'searchOwnerID'):
            self.searchOwnerID = None
        extrahint = ''
        if args != 'wars':
            self._HideNextPrevBtns()
        if args == 'all':
            self.ourWarsCont.display = False
            self.allWarsCont.display = True
            self.killReportsCont.display = False
            self.ShowAllWars()
        elif args == 'our':
            self.ourWarsCont.display = True
            self.allWarsCont.display = False
            self.killReportsCont.display = False
            self.ShowWars()
        elif args == 'killreports':
            self.ourWarsCont.display = False
            self.allWarsCont.display = False
            self.killReportsCont.display = True
            self.prevIDs = []
            self.combatPageNum = 0
            selectedCombatType = settings.user.ui.Get('CorpCombatLogCombo', 0)
            if selectedCombatType == 0:
                self.ShowCombatKills()
            else:
                self.ShowCombatLosses()
            extrahint = localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/DelayedKillboardDetails')
        sm.GetService('corpui').LoadTop('res:/ui/Texture/WindowIcons/wars.png', localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/WarsTitle'), extrahint)
        return

    def _HideNextPrevBtns(self):
        if self.btnContainer:
            prevbtn = self.btnContainer.children[1]
            nextbtn = self.btnContainer.children[0]
            prevbtn.state = nextbtn.state = uiconst.UI_HIDDEN
            self.btnContainer.state = uiconst.UI_HIDDEN

    def ShowCombatKills(self, offset=None, pageChange=0, *args):
        recent = sm.GetService('corp').GetRecentKills(self.killentries, offset)
        self.combatPageNum = max(0, self.combatPageNum + pageChange)
        self.ShowKillsEx(recent, self.ShowCombatKills, 'kills', pageNum=self.combatPageNum)

    def ShowCombatLosses(self, offset=None, pageChange=0, *args):
        recent = sm.GetService('corp').GetRecentLosses(self.killentries, offset)
        self.combatPageNum = max(0, self.combatPageNum + pageChange)
        self.ShowKillsEx(recent, self.ShowCombatLosses, 'losses', pageNum=self.combatPageNum)

    def ReloadKillReports(self):
        if self.prevIDs and self.combatPageNum:
            offset = self.prevIDs[self.combatPageNum]
        else:
            offset = None
        combatSetting = self.combatCombo.GetValue()
        if combatSetting == 0:
            self.ShowCombatKills(offset)
        else:
            self.ShowCombatLosses(offset)
        return

    def ShowKillsEx(self, recent, func, combatType, pageNum):
        filterText = self.killReportQuickFilter.GetValue().strip().lower()
        scrolllist, headers = sm.GetService('charactersheet').GetCombatEntries(recent, filterText=filterText)
        for c in self.btnContainer.children:
            c.state = uiconst.UI_HIDDEN

        self.btnContainer.state = uiconst.UI_HIDDEN
        killIDs = [ k.killID for k in recent ]
        prevbtn = self.btnContainer.children[1]
        nextbtn = self.btnContainer.children[0]
        if pageNum > 0:
            self.btnContainer.state = uiconst.UI_NORMAL
            prevbtn.state = uiconst.UI_NORMAL
            pageIndex = min(pageNum, len(self.prevIDs) - 1)
            prevbtn.OnClick = (func, self.prevIDs[pageIndex - 1], -1)
        if pageNum + 1 > len(self.prevIDs):
            maxKillIDs = max(killIDs) + 1 if killIDs else 0
            self.prevIDs.append(maxKillIDs)
        if len(recent) >= self.killentries:
            self.btnContainer.state = uiconst.UI_NORMAL
            nextbtn.state = uiconst.UI_NORMAL
            nextbtn.OnClick = (func, min(killIDs), 1)
        noContentHintText = ''
        if combatType == 'kills':
            noContentHintText = localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/NoKillsFound')
        elif combatType == 'losses':
            noContentHintText = localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/NoLossesFound')
        self.killReportsScroll.Load(contentList=scrolllist, headers=headers, noContentHint=noContentHintText)

    def GetWarAllyContractMenu(self, entry, *args):
        warNegotiation = entry.sr.node.warNegotiation
        myWarEntityID = session.allianceid if session.allianceid else session.corpid
        menu = []
        if warNegotiation.ownerID1 == myWarEntityID:
            menu.append(('Retract Offer', lambda *args: None))
        else:
            menu.append(('Accept Offer', sm.GetService('war').AcceptAllyNegotiation, (warNegotiation.warNegotiationID,)))
        return menu

    def OnWarChanged(self, war, ownerIDs, change):
        if not getattr(self, 'tabs', None):
            return
        else:
            selectedTab = self.tabs.GetSelectedArgs()
            if selectedTab == 'all':
                self.ShowAllWars()
            elif selectedTab == 'our':
                self.ShowWars()
            return

    def GetEntry(self, warID, scroll):
        for entry in scroll.GetNodes():
            if entry is None or entry.war is None:
                continue
            if entry.panel is None or entry.panel.destroyed:
                continue
            if entry.war.warID == warID:
                return entry

        return

    def __AddToList(self, war, scrolllist):
        data = util.KeyVal()
        data.label = ''
        data.war = war
        if self.myWars:
            data.myWars = True
        else:
            data.myWars = False
        scrolllist.append(listentry.Get('WarEntry', data=data))

    def ShowWars(self, *args):
        self.myWars = 1
        self.PopulateView(eve.session.allianceid or eve.session.corpid, self.ourWarsScroll)

    def ShowAllWars(self, *args):
        self.myWars = 0
        searchValue = self.searchEdit.GetValue()
        if searchValue:
            self.PopulateView(self.searchOwnerID, self.allWarsScroll)
        else:
            self.PopulateTop50()

    def BrowseAllWars(self, btn, *args):
        browse = btn.backforth
        self.PopulateTop50(browse)

    def GetFactionWars(self, corpID, *args):
        factionWars = {}
        warFactionID = sm.StartService('facwar').GetCorporationWarFactionID(corpID)
        if warFactionID:
            factions = [ each for each in sm.StartService('facwar').GetWarFactions() ]
            factionWars = IndexRowset(['warID',
             'declaredByID',
             'againstID',
             'timeDeclared',
             'timeFinished',
             'retracted',
             'retractedBy',
             'billID',
             'mutual'], [], 'warID')
            for i, faction in enumerate(factions):
                if facwarCommon.IsEnemyFaction(faction, warFactionID):
                    factionWars[i * -1] = [None,
                     faction,
                     warFactionID,
                     None,
                     None,
                     None,
                     None,
                     None,
                     True]

        return factionWars

    def PopulateTop50(self, browse=None):
        try:
            sm.GetService('corpui').ShowLoad()
            cryForHelp = settings.user.ui.Get('allwars_showcryforhelp', 0)
            if cryForHelp:
                allWars = sm.RemoteSvc('warsInfoMgr').GetWarsRequiringAssistance()
            elif browse == -1 and len(self.warbatches) > 1:
                allWars = self.warbatches[-2]
                self.warbatches = self.warbatches[:-1]
            elif browse == 1 and len(self.warbatches):
                lastWar = self.warbatches[-1][-1]
                allWars = sm.RemoteSvc('warsInfoMgr').GetTop50(lastWar.warID)
                if len(allWars):
                    self.warbatches += [allWars]
            else:
                allWars = sm.RemoteSvc('warsInfoMgr').GetTop50(self.maxWarID)
                if len(allWars):
                    self.warbatches = [allWars]
            scrolllist = []
            ownerIDsToPrime = set()
            for war in allWars:
                ownerIDsToPrime.update({war.declaredByID, war.againstID})

            cfg.eveowners.Prime(ownerIDsToPrime)
            cfg.corptickernames.Prime(ownerIDsToPrime)
            if allWars:
                for wars in sorted(allWars, key=lambda x: x.warID, reverse=True):
                    self.__AddToList(wars, scrolllist)

                if len(self.warbatches) <= 1:
                    scrolllist.insert(0, listentry.Get('Header', {'label': localization.GetByLabel('UI/Corporations/Wars/NumRecentWars', numWars=len(scrolllist))}))
            self.allWarsScroll.Load(contentList=scrolllist, headers=[], noContentHint='')
            if len(allWars) < const.WARS_PER_PAGE:
                self.nextBtn.Disable()
            else:
                self.nextBtn.Enable()
            if len(self.warbatches) > 1:
                self.prevBtn.Enable()
            else:
                self.prevBtn.Disable()
        finally:
            sm.GetService('corpui').HideLoad()

    def PopulateView(self, ownerID, scroll):
        try:
            sm.GetService('corpui').ShowLoad()
            self.viewingOwnerID = ownerID
            regwars = sm.GetService('war').GetWars(self.viewingOwnerID)
            facwars = {}
            if not util.IsAlliance(self.viewingOwnerID) and util.IsCorporation(self.viewingOwnerID) and sm.StartService('facwar').GetCorporationWarFactionID(self.viewingOwnerID):
                facwars = self.GetFactionWars(self.viewingOwnerID)
            owners = set()
            for wars in (regwars, facwars):
                for war in wars.itervalues():
                    owners.add(war.declaredByID)
                    owners.add(war.againstID)
                    owners.update(getattr(war, 'allies', {}).keys())

            if len(owners):
                cfg.eveowners.Prime(owners)
                cfg.corptickernames.Prime(owners)
            if self.destroyed:
                return
            scrolllist = []
            allyNegotiationsByWarID = defaultdict(list)
            for row in sm.GetService('war').GetAllyNegotiations():
                allyNegotiationsByWarID[row.warID].append(row)

            for wars in (regwars, facwars):
                for war in wars.itervalues():
                    activeAllies = set()
                    self.__AddToList(war, scrolllist)
                    try:
                        for allyID, allyRow in war.allies.iteritems():
                            if blue.os.GetWallclockTime() > allyRow.timeFinished:
                                continue
                            activeAllies.add(allyID)
                            scrolllist.append(listentry.Get('AllyEntry', {'warID': war.warID,
                             'allyID': allyID,
                             'isAlly': True,
                             'allyRow': allyRow}))

                    except AttributeError:
                        pass

                    if war.warID in allyNegotiationsByWarID:
                        for neg in allyNegotiationsByWarID[war.warID]:
                            if neg.ownerID1 in activeAllies:
                                continue
                            scrolllist.append(listentry.Get('AllyEntry', {'warID': neg.warID,
                             'allyID': neg.ownerID1,
                             'warNegotiation': neg}))

            if self.tabs.GetSelectedArgs() == 'all' and len(scrolllist):
                searchValue = self.searchEdit.GetValue()
                scrolllist.insert(0, listentry.Get('HeaderClear', {'label': localization.GetByLabel('UI/Corporations/Wars/SearchResult', searchResult=searchValue),
                 'func': self.ClearSearch}))
            corpName = cfg.eveowners.Get(self.viewingOwnerID).ownerName
            notContentHint = localization.GetByLabel('UI/Corporations/CorporationWindow/Wars/CorpOrAllianceNotInvolvedInWars', corpName=corpName)
            scroll.Load(contentList=scrolllist, headers=[], noContentHint=notContentHint)
        finally:
            sm.GetService('corpui').HideLoad()

    def ClearSearch(self, *args):
        self.searchEdit.SetValue('')
        self.searchOwnerID = None
        self.PopulateTop50()
        return

    def CheckBoxChange(self, *args):
        cryForHelp = self.showCryForHelpCb.GetValue()
        settings.user.ui.Set('allwars_showcryforhelp', cryForHelp)
        self.PopulateTop50()

    def Search(self, *args):
        str = self.searchEdit.GetValue()
        if not str or str == '':
            return
        dlg = form.CorporationOrAlliancePickerDailog.Open(warableEntitysOnly=True, searchStr=str)
        dlg.ShowModal()
        if dlg.ownerID:
            self.searchOwnerID = dlg.ownerID
            self.PopulateView(dlg.ownerID, self.allWarsScroll)

    def DeclareWar(self, *args):
        sm.GetService('menu').DeclareWar()
        self.ShowWars()

    def CreateAllyContract(self, war):
        form.WarAssistanceOfferWnd.CloseIfOpen()
        requesterID = session.corpid if session.allianceid is None else session.allianceid
        form.WarAssistanceOfferWnd.Open(war=war, requesterID=requesterID, isRequest=True, iskValue=getattr(war, 'reward', 0))
        return

    def RequestAlly(self, war, *args):
        form.NegotiationWnd.CloseIfOpen()
        requesterID = session.corpid if session.allianceid is None else session.allianceid
        form.NegotiationWnd.Open(war=war, requesterID=requesterID, isSurrender=False, isAllyRequest=True, isRequest=True)
        return

    def SurrenderWar(self, war, *args):
        form.WarSurrenderWnd.CloseIfOpen()
        requesterID = session.corpid if session.allianceid is None else session.allianceid
        form.WarSurrenderWnd.Open(war=war, requesterID=requesterID, isSurrender=True, isAllyRequest=False, isRequest=True)
        return

    def OnCombatChange(self, *args):
        combatSetting = self.combatCombo.GetValue()
        settings.user.ui.Set('CorpCombatLogCombo', combatSetting)
        self.combatPageNum = 0
        if combatSetting == 0:
            self.ShowCombatKills()
        else:
            self.ShowCombatLosses()