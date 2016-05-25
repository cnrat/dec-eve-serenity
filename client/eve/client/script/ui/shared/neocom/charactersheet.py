# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\charactersheet.py
from collections import defaultdict, OrderedDict
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer, CONTENT_ALIGN_CENTER
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.themeColored import FillThemeColored, LineThemeColored
from eve.client.script.ui.shared.vgs.button import BuyButtonIsk, BuyButtonPlex
import service
import blue
import uiprimitives
import uicontrols
import uthread
import uix
import uiutil
from eve.client.script.ui.control.divider import Divider
import form
import util
import characterskills as charskills
from eve.client.script.ui.control import entries as listentry
from eve.client.script.ui.shared.killReportUtil import OpenKillReport
import base
import uicls
import carbonui.const as uiconst
import localization
import telemetry
import logConst
import const
from eve.client.script.ui.shared.neocom.charsheet.skins import CharacterSkinsPanel
import evetypes
from eve.client.script.ui.tooltips.tooltipsWrappers import TooltipHeaderDescriptionWrapper
from eve.client.script.ui.shared.monetization.events import LogCharacterSheetPilotLicenseImpression, LogMultiPilotTrainingBannerImpression
from eve.client.script.ui.skilltrading.banner import IsSkillInjectorBannerDismissed, SkillInjectorBanner
MAXBIOLENGTH = 1000

class CharacterSheet(service.Service):
    __exportedcalls__ = {'Show': [],
     'SetHint': []}
    __update_on_reload__ = 0
    __guid__ = 'svc.charactersheet'
    __notifyevents__ = ['ProcessSessionChange',
     'OnSkillsChanged',
     'OnSkillQueueChanged',
     'OnGodmaItemChange',
     'OnAttribute',
     'OnAttributes',
     'OnRankChange',
     'OnCloneJumpUpdate',
     'OnKillNotification',
     'OnSessionChanged',
     'OnUpdatedMedalsAvailable',
     'OnUpdatedMedalStatusAvailable',
     'OnRespecInfoUpdated',
     'OnSkillQueueRefreshed',
     'OnFreeSkillPointsChanged_Local',
     'OnUIRefresh',
     'OnKillRightSold',
     'OnKillRightExpired',
     'OnKillRightSellCancel',
     'OnKillRightCreated',
     'OnKillRightUsed',
     'OnMultipleCharactersTrainingRefreshed',
     'OnSkinLicenseActivated']
    __servicename__ = 'charactersheet'
    __displayname__ = 'Character Sheet Client Service'
    __dependencies__ = ['clonejump']
    __startupdependencies__ = ['settings',
     'skills',
     'neocom',
     'crimewatchSvc']

    def Run(self, memStream=None):
        self.LogInfo('Starting Character Sheet')
        sm.FavourMe(self.OnSessionChanged)
        self.Reset()
        if not sm.GetService('skillqueue').SkillInTraining():
            sm.GetService('neocom').Blink('charactersheet')

    def Stop(self, memStream=None):
        self.entryTmpl = None
        self.bio = None
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.Close()
        return

    def OnUIRefresh(self, *args):
        wnd = form.CharacterSheet.GetIfOpen()
        if wnd:
            wnd.Close()
            self.Show()

    def ProcessSessionChange(self, isremote, session, change):
        if session.charid is None:
            self.Stop()
            self.Reset()
        return

    def OnSessionChanged(self, isRemote, session, change):
        if 'corpid' in change:
            wnd = self.GetWnd()
            if wnd is not None and not wnd.destroyed:
                wnd.sr.employmentList = None
                selection = [ each for each in wnd.sr.nav.GetSelected() if each.key == 'employment' ]
                if selection:
                    self.showing = None
                    self.Load('employment')
        return

    def OnRankChange(self, oldrank, newrank):
        if not session.warfactionid:
            return
        rankLabel, _ = sm.GetService('facwar').GetRankLabel(session.warfactionid, newrank)
        if newrank > oldrank:
            blinkMsg = cfg.GetMessage('RankGained', {'rank': rankLabel}).text
        else:
            blinkMsg = cfg.GetMessage('RankLost', {'rank': rankLabel}).text
        self.ReloadMyRanks()
        sm.GetService('neocom').Blink('charactersheet', blinkMsg)

    def OnSkillsChanged(self, *args):
        sm.GetService('neocom').Blink('charactersheet')
        self._ReloadSkillTabs()
        self.LoadGeneralInfo()

    def OnSkillQueueChanged(self):
        self.OnSkillsChanged()

    def OnGodmaItemChange(self, item, change):
        if const.ixLocationID in change and item.categoryID == const.categoryImplant and item.flagID in [const.flagBooster, const.flagImplant]:
            sm.GetService('neocom').Blink('charactersheet')
            if self.showing == 'myimplants_boosters':
                self.ShowMyImplantsAndBoosters()
        elif const.ixFlag in change and item.categoryID == const.categorySkill:
            self._ReloadSkillTabs()
        self.LoadGeneralInfo()

    def OnAttribute(self, attributeName, item, value):
        if attributeName == 'skillPoints':
            self._ReloadSkillTabs()
        elif attributeName in ('memory', 'intelligence', 'willpower', 'perception', 'charisma') and self.showing == 'myattributes':
            self.UpdateMyAttributes(util.LookupConstValue('attribute%s' % attributeName.capitalize(), 0), value)

    def OnAttributes(self, changes):
        for attributeName, item, value in changes:
            self.OnAttribute(attributeName, item, value)

    def OnKillRightSold(self, killRightID):
        if self.showing == 'killrights':
            self.ShowKillRights()

    def OnKillRightExpired(self, killRightID):
        if self.showing == 'killrights':
            self.ShowKillRights()

    def OnKillRightSellCancel(self, killRightID):
        if self.showing == 'killrights':
            self.ShowKillRights()

    def OnKillRightCreated(self, killRightID, fromID, toID, expiryTime):
        if self.showing == 'killrights':
            self.ShowKillRights()

    def OnKillRightUsed(self, killRightID, toID):
        if self.showing == 'killrights':
            self.ShowKillRights()

    def OnCloneJumpUpdate(self):
        if self.showing == 'jumpclones':
            self.ShowJumpClones()

    def GetOrOpenWnd(self):
        return form.CharacterSheet.Open()

    def DeselectAllNodes(self, wnd):
        for node in wnd.sr.scroll.GetNodes():
            wnd.sr.scroll._DeselectNode(node)

    def ForceShowSkillSkill(self):
        wnd = self.GetOrOpenWnd()
        wnd.sr.nav.SetSelected(0)
        blue.pyos.synchro.SleepWallclock(50)
        wnd.sr.skilltabs.SelectByIdx(0)

    def ForceShowSkillHistoryHighlighting(self, skillTypeIds):
        uthread.new(self._HighlightSkillHistorySkills, args=skillTypeIds)

    def _HighlightSkillHistorySkills(self, args):
        trainingRecords = args
        wnd = self.GetOrOpenWnd()
        if wnd:
            blue.pyos.synchro.SleepWallclock(50)
            wnd.sr.nav.SetSelected(0)
            blue.pyos.synchro.SleepWallclock(50)
            wnd.sr.skilltabs.SelectByIdx(2)
            self.DeselectAllNodes(wnd)
            blue.pyos.synchro.SleepWallclock(500)
            skillIDsCopy = trainingRecords[:]
            for node in wnd.sr.scroll.GetNodes():
                recordKey = (node.id, node.level)
                if recordKey in skillIDsCopy:
                    wnd.sr.scroll._SelectNode(node)
                    skillIDsCopy.remove(recordKey)

    def OnMultipleCharactersTrainingRefreshed(self):
        if self.showing == 'pilotlicense':
            self.ShowPilotLicense()

    def OnKillNotification(self):
        sm.StartService('objectCaching').InvalidateCachedMethodCall('charMgr', 'GetRecentShipKillsAndLosses', 25, None)
        return

    def OnUpdatedMedalsAvailable(self):
        sm.GetService('neocom').Blink('charactersheet')
        wnd = self.GetWnd()
        if wnd is None:
            return
        else:
            wnd.sr.decoMedalList = None
            if self.showing.startswith('mydecorations_'):
                self.ShowMyDecorations(self.showing)
            return

    def OnUpdatedMedalStatusAvailable(self):
        wnd = self.GetWnd()
        if wnd is None or wnd.destroyed:
            return
        else:
            if self.showing.startswith('mydecorations_permissions'):
                wnd.sr.decoMedalList = None
                self.ShowMyDecorations(self.showing)
            return

    def OnRespecInfoUpdated(self):
        if self.showing == 'myattributes':
            self.ShowMyAttributes()

    def OnSkillQueueRefreshed(self):
        self._ReloadSkillTabs()

    def OnFreeSkillPointsChanged_Local(self):
        self._ReloadSkillTabs()

    def Reset(self):
        self.panels = []
        self.standingsinited = 0
        self.mydecorationsinited = 0
        self.standingtabs = None
        self.mydecorationstabs = None
        self.skillsinited = 0
        self.skilltabs = None
        self.killsinited = 0
        self.killstabs = None
        self.killentries = 25
        self.showing = None
        self.skillTimer = None
        self.jumpClones = False
        self.jumpCloneImplants = False
        self.bio = None
        self.daysLeft = -1
        self.loading = False
        return

    def Show(self):
        wnd = self.GetWnd(1)
        if wnd is not None and not wnd.destroyed:
            wnd.Maximize()
            return wnd
        else:
            return

    def GetWnd(self, getnew=0):
        if not getnew:
            return form.CharacterSheet.GetIfOpen()
        else:
            return form.CharacterSheet.ToggleOpenClose()

    def OpenSkillQueueWindow(self, *args):
        uicore.cmd.OpenSkillQueueWindow()

    def OpenCertificates(self):
        window = form.CharacterSheet.Open()
        if window:
            window.sr.nav.SetSelected(0)
            window.sr.skilltabs.SelectByIdx(1)
            self.Load('myskills')

    @telemetry.ZONE_METHOD
    def GetNavEntries(self, wnd):
        nav = [[localization.GetByLabel('Tooltips/CharacterSheet/Skills'),
          wnd.sr.scroll,
          'res:/ui/Texture/WindowIcons/skills.png',
          'myskills',
          settings.user.ui.Get('charsheetorder_myskills', 0),
          'characterSheetMenuSkillsBtn',
          'Tooltips/CharacterSheet/Skills_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/Decorations'),
          wnd.sr.scroll,
          'res:/ui/Texture/WindowIcons/decorations.png',
          'mydecorations',
          settings.user.ui.Get('charsheetorder_mydecorations', 2),
          'characterSheetMenuDecorationsBtn',
          'Tooltips/CharacterSheet/Decorations_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/Attributes'),
          wnd.sr.scroll,
          'res:/ui/Texture/WindowIcons/attributes.png',
          'myattributes',
          settings.user.ui.Get('charsheetorder_myattributes', 3),
          'characterSheetMenuAttributesBtn',
          'Tooltips/CharacterSheet/Attributes_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/Augmentations'),
          wnd.sr.scroll,
          'res:/ui/Texture/WindowIcons/augmentations.png',
          'myimplants_boosters',
          settings.user.ui.Get('charsheetorder_myimplants_boosters', 4),
          'characterSheetMenuImplantsBtn',
          'Tooltips/CharacterSheet/Augmentations_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/JumpClones'),
          wnd.sr.scroll,
          'res:/ui/Texture/WindowIcons/jumpclones.png',
          'jumpclones',
          settings.user.ui.Get('charsheetorder_jumpclones', 5),
          'characterSheetMenuJumpclonesBtn',
          'Tooltips/CharacterSheet/JumpClones_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/Bio'),
          wnd.sr.bioparent,
          'res:/ui/Texture/WindowIcons/biography.png',
          'bio',
          settings.user.ui.Get('charsheetorder_bio', 6),
          'characterSheetMenuBioBtn',
          'Tooltips/CharacterSheet/Bio_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/EmploymentHistory'),
          wnd.sr.scroll,
          'res:/ui/Texture/WindowIcons/employmenthistory.png',
          'employment',
          settings.user.ui.Get('charsheetorder_employment', 7),
          'characterSheetMenuEmploymentBtn',
          'Tooltips/CharacterSheet/EmploymentHistory_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/Standings'),
          wnd.sr.scroll,
          'res:/ui/Texture/WindowIcons/personalstandings.png',
          'mystandings',
          settings.user.ui.Get('charsheetorder_mystandings', 8),
          'characterSheetMenuStandingBtn',
          'Tooltips/CharacterSheet/Standings_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/SecurityStatus'),
          wnd.sr.scroll,
          'res:/ui/Texture/WindowIcons/securitystatus.png',
          'securitystatus',
          settings.user.ui.Get('charsheetorder_securitystatus', 9),
          'characterSheetMenuSecurityStatusBtn',
          'Tooltips/CharacterSheet/SecurityStatus_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/KillRights'),
          wnd.sr.scroll,
          'res:/ui/Texture/WindowIcons/killrights.png',
          'killrights',
          settings.user.ui.Get('charsheetorder_killrights', 10),
          'characterSheetMenuKillRightsBtn',
          'Tooltips/CharacterSheet/KillRights_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/CombatLog'),
          wnd.sr.scroll,
          'res:/ui/Texture/WindowIcons/combatlog.png',
          'mykills',
          settings.user.ui.Get('charsheetorder_mykills', 11),
          'characterSheetMenuKillsBtn',
          'Tooltips/CharacterSheet/CombatLog_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/PilotLicense'),
          wnd.sr.scrollContainer,
          'res:/ui/Texture/WindowIcons/pilotlicense.png',
          'pilotlicense',
          settings.user.ui.Get('charsheetorder_pilotlicense', 12),
          'characterSheetMenuPilotLicenseBtn',
          'Tooltips/CharacterSheet/PilotLicense_description'],
         [localization.GetByLabel('Tooltips/CharacterSheet/Skins'),
          None,
          'res:/ui/Texture/WindowIcons/skins.png',
          'skins',
          settings.user.ui.Get('charsheetorder_skins', 13),
          'characterSheetMenuSkinsBtn',
          'Tooltips/CharacterSheet/Skins_description']]
        navEntries = []
        for each in nav:
            navEntries.append((each[4], each))

        navEntries = uiutil.SortListOfTuples(navEntries)
        return navEntries

    def SetHint(self, hintstr=None):
        wnd = self.GetWnd()
        if wnd is not None:
            wnd.sr.scroll.ShowHint(hintstr)
        return

    def OnCloseWnd(self, wnd, *args):
        if self.showing == 'bio':
            self.AutoSaveBio()
        self.bioinited = 0
        self.showing = None
        settings.user.ui.Set('charsheetleftwidth', wnd.sr.leftSide.width)
        self.panels = []
        return

    def OnSelectEntry(self, node):
        if node != []:
            self.Load(node[0].key)
            settings.char.ui.Set('charactersheetselection', node[0].idx)

    @telemetry.ZONE_METHOD
    def HideScrolls(self):
        wnd = self.GetWnd()
        for each in [wnd.sr.scroll, wnd.sr.bioparent]:
            each.state = uiconst.UI_HIDDEN

    def Load(self, key):
        wnd = self.GetWnd()
        if not wnd:
            return
        elif self.loading or self.showing == key:
            return
        else:
            self.loading = True
            try:
                if self.showing == 'bio':
                    self.AutoSaveBio()
                self.HideScrolls()
                wnd.quickFilter.SetValue('')
                for uielement in ['standingtabs',
                 'killstabs',
                 'skilltabs',
                 'btnContainer',
                 'mydecorationstabs',
                 'buttonParDeco',
                 'skillpanel',
                 'combatlogpanel',
                 'plexContainer']:
                    e = getattr(wnd.sr, uielement, None)
                    if e:
                        e.state = uiconst.UI_HIDDEN

                e = getattr(wnd, 'skinsPanel', None)
                if e:
                    e.state = uiconst.UI_HIDDEN
                if key.startswith('mystandings'):
                    wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
                    if not wnd.sr.standingsinited:
                        wnd.sr.standingsinited = 1
                        tabs = uicontrols.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/StandingTabs/LikedBy'),
                          wnd.sr.scroll,
                          self,
                          'mystandings_to_positive'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/StandingTabs/DislikeBy'),
                          wnd.sr.scroll,
                          self,
                          'mystandings_to_negative']], groupID='cs_standings')
                        wnd.sr.standingtabs = tabs
                        wnd.sr.standingtabs.AutoSelect()
                        return
                    if getattr(wnd.sr, 'standingtabs', None):
                        wnd.sr.standingtabs.state = uiconst.UI_NORMAL
                    wnd.sr.standingtabs.state = uiconst.UI_NORMAL
                    if key == 'mystandings':
                        wnd.sr.standingtabs.AutoSelect()
                        return
                    self.SetHint()
                    if key == 'mystandings_to_positive':
                        positive = True
                    else:
                        positive = False
                    self.ShowStandings(positive)
                elif key.startswith('myskills'):
                    wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
                    if not wnd.sr.skillsinited:
                        wnd.sr.skillsinited = 1
                        wnd.sr.skilltabs = uicontrols.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Skills'),
                          wnd.sr.scroll,
                          self,
                          'myskills_skills'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/Certificates'),
                          wnd.sr.scroll,
                          self,
                          'myskills_certificates'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/History'),
                          wnd.sr.scroll,
                          self,
                          'myskills_skillhistory']], groupID='cs_skills', UIIDPrefix='characterSheetTab')
                        wnd.sr.skilltabs.AutoSelect()
                        return
                    if getattr(wnd.sr, 'skilltabs', None):
                        wnd.sr.skilltabs.state = uiconst.UI_NORMAL
                    if key == 'myskills':
                        if self.showing in ('myskills_skills', 'myskills_certificates'):
                            if getattr(wnd.sr, 'skillpanel', None):
                                wnd.sr.skillpanel.state = uiconst.UI_NORMAL
                        wnd.sr.skilltabs.AutoSelect()
                        return
                    self.SetHint()
                    self.ShowSkills(key)
                elif key.startswith('mydecorations'):
                    wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
                    if not wnd.sr.mydecorationsinited:
                        wnd.sr.mydecorationsinited = 1
                        tabs = uicontrols.TabGroup(name='tabparent', parent=wnd.sr.mainArea, idx=0, tabs=[[localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Ranks'),
                          wnd.sr.scroll,
                          self,
                          'mydecorations_ranks'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Medals'),
                          wnd.sr.scroll,
                          self,
                          'mydecorations_medals'], [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Permissions'),
                          wnd.sr.scroll,
                          self,
                          'mydecorations_permissions']], groupID='cs_decorations')
                        wnd.sr.mydecorationstabs = tabs
                        wnd.sr.mydecorationstabs.AutoSelect()
                        return
                    if getattr(wnd.sr, 'mydecorationstabs', None):
                        wnd.sr.mydecorationstabs.state = uiconst.UI_NORMAL
                    if key == 'mydecorations':
                        wnd.sr.mydecorationstabs.AutoSelect()
                        if self.showing == 'mydecorations_permissions':
                            wnd.sr.buttonParDeco.state = uiconst.UI_NORMAL
                        return
                    self.SetHint()
                    self.ShowMyDecorations(key)
                elif key.startswith('mykills'):
                    self.combatPageNum = 0
                    wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
                    if getattr(wnd.sr, 'combatlogpanel', None):
                        wnd.sr.combatlogpanel.state = uiconst.UI_NORMAL
                    if not wnd.sr.killsinited:
                        wnd.sr.killsinited = 1
                        btnContainer = Container(name='pageBtnContainer', parent=wnd.sr.mainArea, align=uiconst.TOBOTTOM, idx=0, padBottom=4)
                        btn = uix.GetBigButton(size=22, where=btnContainer, left=4, top=0)
                        btn.SetAlign(uiconst.CENTERRIGHT)
                        btn.hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/ViewMore')
                        btn.sr.icon.LoadIcon('ui_23_64_2')
                        btn = uix.GetBigButton(size=22, where=btnContainer, left=4, top=0)
                        btn.SetAlign(uiconst.CENTERLEFT)
                        btn.hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/ViewPrevious')
                        btn.sr.icon.LoadIcon('ui_23_64_1')
                        btnContainer.height = max([ c.height for c in btnContainer.children ])
                        wnd.sr.btnContainer = btnContainer
                        self.ShowKills()
                        self.showing = 'mykills'
                        return
                    self.ShowKills()
                else:
                    if wnd.sr.standingsinited:
                        wnd.sr.standingtabs.state = uiconst.UI_HIDDEN
                    if wnd.sr.skillsinited:
                        wnd.sr.skilltabs.state = uiconst.UI_HIDDEN
                    if wnd.sr.mydecorationsinited:
                        wnd.sr.mydecorationstabs.state = uiconst.UI_HIDDEN
                    self.SetHint()
                    if key == 'myattributes':
                        self.ShowMyAttributes()
                    elif key == 'myimplants_boosters':
                        self.ShowMyImplantsAndBoosters()
                    elif key == 'bio':
                        self.ShowMyBio()
                    elif key == 'securitystatus':
                        self.ShowSecurityStatus()
                    elif key == 'killrights':
                        self.ShowKillRights()
                    elif key == 'jumpclones':
                        self.ShowJumpClones()
                    elif key == 'employment':
                        self.ShowEmploymentHistory()
                    elif key == 'mysettings':
                        self.ShowSettings()
                    elif key == 'pilotlicense':
                        self.ShowPilotLicense()
                        LogOpenPilotLicense()
                    elif key == 'skins':
                        self.ShowSkins()
                self.showing = key
            finally:
                self.loading = False

            return

    def BuyPlexOnMarket(self, *args):
        uthread.new(sm.StartService('marketutils').ShowMarketDetails, const.typePilotLicence, None)
        return

    def LoadGeneralInfo(self):
        if getattr(self, 'loadingGeneral', 0):
            return
        else:
            wnd = self.GetWnd()
            if wnd is None or wnd.destroyed:
                return
            self.loadingGeneral = 1
            uix.Flush(wnd.sr.topParent)
            characterName = cfg.eveowners.Get(eve.session.charid).name
            if not getattr(self, 'charMgr', None):
                self.charMgr = sm.RemoteSvc('charMgr')
            if not getattr(self, 'cc', None):
                self.charsvc = sm.GetService('cc')
            wnd.sr.charinfo = charinfo = self.charMgr.GetPublicInfo(eve.session.charid)
            if settings.user.ui.Get('charsheetExpanded', 1):
                parent = wnd.sr.topParent
                wnd.sr.picParent = Container(name='picpar', parent=parent, align=uiconst.TOPLEFT, width=200, height=200, left=const.defaultPadding, top=16)
                wnd.sr.pic = uiprimitives.Sprite(parent=wnd.sr.picParent, align=uiconst.TOALL, left=1, top=1, height=1, width=1)
                wnd.sr.pic.OnClick = self.OpenPortraitWnd
                wnd.sr.pic.cursor = uiconst.UICURSOR_MAGNIFIER
                uicontrols.Frame(parent=wnd.sr.picParent, opacity=0.2)
                sm.GetService('photo').GetPortrait(eve.session.charid, 256, wnd.sr.pic)
                infoTextPadding = wnd.sr.picParent.width + const.defaultPadding * 4
                characterLink = localization.GetByLabel('UI/Contracts/ContractsWindow/ShowInfoLink', showInfoName=characterName, info=('showinfo', const.typeCharacterAmarr, session.charid))
                wnd.sr.nameText = uicontrols.EveCaptionMedium(text=characterLink, parent=wnd.sr.topParent, left=infoTextPadding, top=12, state=uiconst.UI_NORMAL)
                wnd.sr.raceinfo = raceinfo = cfg.races.Get(charinfo.raceID)
                wnd.sr.bloodlineinfo = bloodlineinfo = cfg.bloodlines.Get(charinfo.bloodlineID)
                wnd.sr.schoolinfo = schoolinfo = self.charsvc.GetData('schools', ['schoolID', charinfo.schoolID])
                wnd.sr.ancestryinfo = ancestryinfo = self.charsvc.GetData('ancestries', ['ancestryID', charinfo.ancestryID])
                if wnd is None or wnd.destroyed:
                    self.loadingGeneral = 0
                    return
                securityStatus = self.crimewatchSvc.GetMySecurityStatus()
                roundedSecurityStatus = localization.formatters.FormatNumeric(securityStatus, decimalPlaces=1)
                cloneLocationRow = sm.RemoteSvc('charMgr').GetHomeStationRow()
                if cloneLocationRow:
                    stationID = cloneLocationRow.stationID
                    cloneLocationSystemID = cloneLocationRow.solarSystemID
                    if cloneLocationSystemID:
                        labelPath = 'UI/CharacterSheet/CharacterSheetWindow/CloneLocationHint'
                        cloneLocationHint = localization.GetByLabel(labelPath, locationId=stationID, systemId=cloneLocationSystemID)
                        cloneLocation = cfg.evelocations.Get(cloneLocationSystemID).name
                    else:
                        cloneLocationHint = cfg.evelocations.Get(stationID).name
                        cloneLocation = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/UnknownSystem')
                else:
                    cloneLocation = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/UnknownSystem')
                    cloneLocationHint = ''
                alliance = ''
                if eve.session.allianceid:
                    cfg.eveowners.Prime([eve.session.allianceid])
                    alliance = (localization.GetByLabel('UI/Common/Alliance'), cfg.eveowners.Get(eve.session.allianceid).name, '')
                faction = ''
                if eve.session.warfactionid:
                    fac = sm.StartService('facwar').GetFactionalWarStatus()
                    faction = (localization.GetByLabel('UI/Common/Militia'), cfg.eveowners.Get(fac.factionID).name, '')
                bounty = ''
                bountyOwnerIDs = (session.charid, session.corpid, session.allianceid)
                bountyAmount = sm.GetService('bountySvc').GetBounty(*bountyOwnerIDs)
                bountyAmounts = sm.GetService('bountySvc').GetBounties(*bountyOwnerIDs)
                charBounty = 0
                corpBounty = 0
                allianceBounty = 0
                if len(bountyAmounts):
                    for ownerID, value in bountyAmounts.iteritems():
                        if util.IsCharacter(ownerID):
                            charBounty = value
                        elif util.IsCorporation(ownerID):
                            corpBounty = value
                        elif util.IsAlliance(ownerID):
                            allianceBounty = value

                bountyHint = localization.GetByLabel('UI/Station/BountyOffice/BountyHint', charBounty=util.FmtISK(charBounty, 0), corpBounty=util.FmtISK(corpBounty, 0), allianceBounty=util.FmtISK(allianceBounty, 0))
                bounty = (localization.GetByLabel('UI/Station/BountyOffice/Bounty'), util.FmtISK(bountyAmount, 0), bountyHint)
                skillPoints = int(sm.GetService('skills').GetSkillPoints())
                textList = [(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillPoints'), localization.formatters.FormatNumeric(skillPoints, useGrouping=True), ''),
                 (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/HomeSystem'), cloneLocation, cloneLocationHint),
                 (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackground'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackgroundInformation', raceName=localization.GetByMessageID(raceinfo.raceNameID), bloodlineName=localization.GetByMessageID(bloodlineinfo.bloodlineNameID), ancestryName=localization.GetByMessageID(ancestryinfo.ancestryNameID)), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CharacterBackgroundHint')),
                 (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DateOfBirth'), localization.formatters.FormatDateTime(charinfo.createDateTime, dateFormat='long', timeFormat='long'), ''),
                 (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/School'), localization.GetByMessageID(schoolinfo.schoolNameID), ''),
                 (localization.GetByLabel('UI/Common/Corporation'), cfg.eveowners.Get(eve.session.corpid).name, ''),
                 (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatus'), roundedSecurityStatus, localization.formatters.FormatNumeric(securityStatus, decimalPlaces=4))]
                if faction:
                    textList.insert(len(textList) - 1, faction)
                if alliance:
                    textList.insert(len(textList) - 1, alliance)
                if bounty:
                    textList.insert(len(textList), bounty)
                numLines = len(textList) + 2
                mtext = 'Xg<br>' * numLines
                mtext = mtext[:-4]
                th = uix.GetTextHeight(mtext)
                topParentHeight = max(220, th + const.defaultPadding * 2 + 2)
                top = max(34, wnd.sr.nameText.top + wnd.sr.nameText.height)
                leftContainer = Container(parent=wnd.sr.topParent, left=infoTextPadding, top=top, align=uiconst.TOPLEFT)
                rightContainer = Container(parent=wnd.sr.topParent, top=top, align=uiconst.TOPLEFT)
                subTop = 0
                for label, value, hint in textList:
                    label = uicontrols.EveLabelMedium(text=label, parent=leftContainer, idx=0, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, top=subTop)
                    label.hint = hint
                    label._tabMargin = 0
                    display = uicontrols.EveLabelMedium(text=value, parent=rightContainer, idx=0, state=uiconst.UI_NORMAL, align=uiconst.TOPLEFT, top=subTop)
                    display.hint = hint
                    display._tabMargin = 0
                    subTop += label.height

                leftContainer.AutoFitToContent()
                rightContainer.left = leftContainer.left + leftContainer.width + 20
                rightContainer.AutoFitToContent()
                wnd.SetTopparentHeight(max(topParentHeight, rightContainer.height, leftContainer.height))
            else:
                wnd.SetTopparentHeight(18)
            charsheetExpanded = settings.user.ui.Get('charsheetExpanded', 1)
            if not charsheetExpanded:
                uicontrols.EveLabelMedium(text=characterName, parent=wnd.sr.topParent, left=8, top=1, state=uiconst.UI_DISABLED)
            expandOptions = [localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Expand'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Collapse')]
            a = uicontrols.EveLabelSmall(text=expandOptions[charsheetExpanded], parent=wnd.sr.topParent, left=18, top=3, state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, bold=True)
            a.OnClick = self.ToggleGeneral
            expander = uiprimitives.Sprite(parent=wnd.sr.topParent, pos=(6, 2, 11, 11), name='expandericon', state=uiconst.UI_NORMAL, texturePath=['res:/UI/Texture/Shared/expanderDown.png', 'res:/UI/Texture/Shared/expanderUp.png'][charsheetExpanded], align=uiconst.TOPRIGHT)
            expander.OnClick = self.ToggleGeneral
            self.loadingGeneral = 0
            return

    def OpenPortraitWnd(self, *args):
        form.PortraitWindow.CloseIfOpen()
        form.PortraitWindow.Open(charID=session.charid)

    def ToggleGeneral(self, *args):
        charsheetExpanded = not settings.user.ui.Get('charsheetExpanded', 1)
        settings.user.ui.Set('charsheetExpanded', charsheetExpanded)
        self.LoadGeneralInfo()

    def ShowSecurityStatus(self):
        data = self.crimewatchSvc.GetSecurityStatusTransactions()
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if not wnd:
            return
        else:
            wnd.sr.scroll.sr.id = 'charsheet_securitystatus'
            wnd.sr.scroll.Clear()
            scrolllist = []
            for transaction in data:
                if transaction.eventTypeID == logConst.eventSecStatusGmModification:
                    subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectSetBySlashCmd')
                    body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageResetBySlashCmd')
                elif transaction.eventTypeID == logConst.eventSecStatusGmRollback:
                    subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectSetBySlashCmd')
                    body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageResetBySlashCmd')
                elif transaction.eventTypeID == logConst.eventSecStatusIllegalAggression:
                    cfg.eveowners.Prime([transaction.otherOwnerID])
                    cfg.evelocations.Prime([transaction.locationID])
                    subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectCombatAgression')
                    body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageCombatAgression', locationID=transaction.locationID, ownerName=cfg.eveowners.Get(transaction.otherOwnerID).name, typeID=transaction.otherTypeID)
                elif transaction.eventTypeID == logConst.eventSecStatusKillPirateNpc:
                    subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectLawEnforcmentGain')
                    body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageLawEnforcmentGain', name=cfg.eveowners.Get(transaction.otherOwnerID).name)
                elif transaction.eventTypeID == logConst.eventSecStatusHandInTags:
                    subject = localization.GetByLabel('UI/Generic/FormatStandingTransactions/subjectHandInTags')
                    body = localization.GetByLabel('UI/Generic/FormatStandingTransactions/messageHandInTags')
                if transaction.modification is not None:
                    modification = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatusScroll/Persentage', value=transaction.modification * 100.0, decimalPlaces=4)
                else:
                    modification = ''
                text = '%s<t>%s<t><right>%s</right><t>%s' % (util.FmtDate(transaction.eventDate, 'ls'),
                 modification,
                 localization.formatters.FormatNumeric(transaction.newValue, decimalPlaces=2),
                 subject)
                hint = '%s<br>%s' % (localization.formatters.FormatNumeric(transaction.newValue, decimalPlaces=4), subject)
                scrolllist.append(listentry.Get('StandingTransaction', {'sort_%s' % localization.GetByLabel('UI/Common/Date'): transaction.eventDate,
                 'sort_%s' % localization.GetByLabel('UI/Common/Change'): transaction.modification,
                 'line': 1,
                 'text': text,
                 'hint': hint,
                 'details': body,
                 'isNPC': True}))

            if not wnd:
                return
            headers = [localization.GetByLabel('UI/Common/Date'),
             localization.GetByLabel('UI/Common/Change'),
             localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatus'),
             localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatusScroll/Subject')]
            noChangesHint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SecurityStatusScroll/NoSecurityStatusChanges')
            wnd.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=noChangesHint)
            return

    def ShowMyDecorations(self, key=None):
        wnd = self.GetWnd()
        if wnd is None:
            return
        else:
            wnd.sr.buttonParDeco.state = uiconst.UI_HIDDEN
            if key == 'mydecorations_ranks':
                self.ShowMyRanks()
            elif key == 'mydecorations_medals':
                self.ShowMyMedals()
            elif key == 'mydecorations_permissions':
                wnd.sr.buttonParDeco.state = uiconst.UI_NORMAL
                self.ShowMyDecorationPermissions()
            return

    def ShowMyMedals(self, charID=None):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if charID is None:
            charID = session.charid
        if wnd.sr.decoMedalList is None:
            wnd.sr.decoMedalList = self.GetMedalScroll(charID)
        wnd.sr.scroll.sr.id = 'charsheet_mymedals'
        wnd.sr.scroll.Load(contentList=wnd.sr.decoMedalList, noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/NoMedals'))
        return

    def GetMedalScroll(self, charID, noHeaders=False, publicOnly=False):
        scrolllist = []
        inDecoList = []
        publicDeco = (sm.StartService('medals').GetMedalsReceivedWithFlag(charID, [3]), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'))
        privateDeco = (sm.StartService('medals').GetMedalsReceivedWithFlag(charID, [2]), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'))
        _, characterMedalInfo = sm.StartService('medals').GetMedalsReceived(charID)
        if publicOnly:
            t = (publicDeco,)
        else:
            t = (publicDeco, privateDeco)
        for deco, hint in t:
            if deco and not noHeaders:
                scrolllist.append(listentry.Get('Header', {'label': hint}))
            for medalID, medalData in deco.iteritems():
                if medalID in inDecoList:
                    continue
                inDecoList.append(medalID)
                details = characterMedalInfo.Filter('medalID')
                if details and details.has_key(medalID):
                    details = details.get(medalID)
                entry = sm.StartService('info').GetMedalEntry(medalData, details, 0)
                if entry:
                    scrolllist.append(entry)

        return scrolllist

    def ShowMyRanks(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if wnd.sr.decoRankList is None:
            scrolllist = []
            characterRanks = sm.StartService('facwar').GetCharacterRankOverview(session.charid)
            for characterRank in characterRanks:
                entry = sm.StartService('info').GetRankEntry(characterRank)
                if entry:
                    scrolllist.append(entry)

            wnd.sr.decoRankList = scrolllist[:]
        wnd.sr.scroll.sr.id = 'charsheet_myranks'
        wnd.sr.scroll.Load(contentList=wnd.sr.decoRankList, noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/NoRanks'))
        return

    def ShowEmploymentHistory(self):
        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        if wnd.sr.employmentList is None:
            wnd.sr.employmentList = sm.GetService('info').GetEmploymentHistorySubContent(eve.session.charid)
        wnd.sr.scroll.sr.id = 'charsheet_employmenthistory'
        wnd.sr.scroll.Load(contentList=wnd.sr.employmentList)
        return

    def ShowKillRights(self):
        scrolllist = []
        killRights = sm.GetService('bountySvc').GetMyKillRights()
        currentTime = blue.os.GetWallclockTime()
        myKillRights = filter(lambda x: x.fromID == session.charid and currentTime < x.expiryTime, killRights)
        otherKillRights = filter(lambda x: x.toID == session.charid and currentTime < x.expiryTime, killRights)
        charIDsToPrime = set()
        for eachKR in myKillRights:
            charIDsToPrime.add(eachKR.toID)

        for eachKR in otherKillRights:
            charIDsToPrime.add(eachKR.fromID)

        cfg.eveowners.Prime(charIDsToPrime)
        if myKillRights:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/InfoWindow/CanKill'),
             'hideLines': True}))
            for killRight in myKillRights:
                scrolllist.append(listentry.Get('KillRightsEntry', {'charID': killRight.toID,
                 'expiryTime': killRight.expiryTime,
                 'killRight': killRight,
                 'isMine': True}))

        if otherKillRights:
            scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/InfoWindow/CanBeKilledBy'),
             'hideLines': True}))
            for killRight in otherKillRights:
                scrolllist.append(listentry.Get('KillRightsEntry', {'charID': killRight.fromID,
                 'expiryTime': killRight.expiryTime,
                 'killRight': killRight,
                 'isMine': False}))

        wnd = self.GetWnd()
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        wnd.sr.scroll.sr.id = 'charsheet_killrights'
        wnd.sr.scroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/NoKillRightsFound'))

    def ShowJumpClones(self):
        jumpCloneSvc = sm.GetService('clonejump')
        jumpClones = jumpCloneSvc.GetClones()
        scrolllist = []
        lastJump = jumpCloneSvc.LastCloneJumpTime()
        hoursLimit = sm.GetService('godma').GetItem(session.charid).cloneJumpCoolDown
        if lastJump:
            jumpTime = lastJump + hoursLimit * const.HOUR
            nextJump = jumpTime > blue.os.GetWallclockTime()
        else:
            nextJump = False
        nextAvailableLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/NextCloneJump')
        availableNow = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Now')
        if nextJump:
            scrolllist.append(listentry.Get('TextTimer', {'line': 1,
             'label': nextAvailableLabel,
             'text': util.FmtDate(lastJump),
             'iconID': const.iconDuration,
             'countdownTime': int(jumpTime),
             'finalText': availableNow}))
        else:
            scrolllist.append(listentry.Get('TextTimer', {'line': 1,
             'label': nextAvailableLabel,
             'text': availableNow,
             'iconID': const.iconDuration,
             'countdownTime': 0}))
        if jumpClones:
            d = OrderedDict([('station', {}), ('shipOrStructure', {})])
            primeLocs = []
            for jc in jumpClones:
                jumpCloneID = jc.jumpCloneID
                locationID = jc.locationID
                cloneName = jc.cloneName
                primeLocs.append(locationID)
                destinationType = 'station' if util.IsStation(locationID) else 'shipOrStructure'
                d[destinationType][locationID] = (jumpCloneID, locationID, cloneName)

            cfg.evelocations.Prime(primeLocs)
            for locInfo in d.itervalues():
                locIDs = locInfo.keys()
                locNames = self.GetLocNames(locIDs)
                locNames = localization.util.Sort(locNames, key=lambda x: x[0])
                for _, locationString, locationID in locNames:
                    infoForLocation = locInfo[locationID]
                    cloneName = infoForLocation[2]
                    label = '%s - %s' % (cloneName, locationString) if cloneName else locationString
                    groupID = infoForLocation
                    data = {'GetSubContent': self.GetCloneImplants,
                     'label': label,
                     'id': groupID,
                     'jumpCloneID': infoForLocation[0],
                     'locationID': infoForLocation[1],
                     'cloneName': cloneName,
                     'state': 'locked',
                     'iconMargin': 18,
                     'showicon': 'res:/ui/Texture/WindowIcons/jumpclones.png',
                     'sublevel': 0,
                     'MenuFunction': self.JumpCloneMenu,
                     'showlen': 0}
                    scrolllist.append(listentry.Get('Group', data))

        wnd = self.GetWnd()
        if wnd:
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            wnd.sr.scroll.sr.id = 'charsheet_jumpclones'
            noClonesFoundHint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/NoJumpClonesFound')
            wnd.sr.scroll.Load(contentList=scrolllist, noContentHint=noClonesFoundHint)

    def GetLocNames(self, locIDs):
        locNames = []
        destroyedLocString = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/CloneLocationDestroyed')
        destroyedLocName = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/DestroyedLocation')
        for locID in locIDs:
            if locID in cfg.evelocations:
                locName = cfg.evelocations.Get(locID).name
                locString = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/CloneLocation', cloneLocation=locID)
            else:
                locName = destroyedLocName
                locString = destroyedLocString
            locNames.append((locName, locString, locID))

        return locNames

    def GetCloneImplants(self, nodedata, *args):
        scrolllist = []
        godma = sm.GetService('godma')
        implants = uiutil.SortListOfTuples([ (getattr(godma.GetType(implant.typeID), 'implantness', None), implant) for implant in sm.GetService('clonejump').GetImplantsForClone(nodedata.jumpCloneID) ])
        if implants:
            for cloneImplantRow in implants:
                scrolllist.append(listentry.Get('ImplantEntry', {'implant_booster': cloneImplantRow,
                 'label': evetypes.GetName(cloneImplantRow.typeID),
                 'sublevel': 1}))

        else:
            noImplantsString = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/NoImplantsInstalled')
            scrolllist.append(listentry.Get('Text', {'label': noImplantsString,
             'text': noImplantsString}))
        scrolllist.append(listentry.Get('CloneButtons', {'locationID': nodedata.locationID,
         'jumpCloneID': nodedata.jumpCloneID}))
        return scrolllist

    def JumpCloneMenu(self, node):
        m = []
        validLocation = node.locationID in cfg.evelocations
        if eve.session.stationid and validLocation:
            m += [None]
            m += [(uiutil.MenuLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Jump'), sm.GetService('clonejump').CloneJump, (node.locationID,))]
        if validLocation:
            m.append((uiutil.MenuLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Destroy'), sm.GetService('clonejump').DestroyInstalledClone, (node.jumpCloneID,)))
            if util.IsStation(node.locationID):
                stationInfo = sm.StartService('ui').GetStation(node.locationID)
                m += sm.StartService('menu').CelestialMenu(node.locationID, typeID=stationInfo.stationTypeID, parentID=stationInfo.solarSystemID)
            m += [(uiutil.MenuLabel('UI/Commands/SetName'), self.SetJumpCloneName, (node.jumpCloneID, node.cloneName))]
        return m

    def SetJumpCloneName(self, cloneID, oldName):
        nameRet = uiutil.NamePopup(localization.GetByLabel('UI/Menusvc/SetName'), localization.GetByLabel('UI/Menusvc/TypeInNewName'), setvalue=oldName, maxLength=100)
        if nameRet:
            sm.GetService('clonejump').SetJumpCloneName(cloneID, nameRet)

    def ShowMyBio(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return
        else:
            wnd.sr.bioparent.state = uiconst.UI_PICKCHILDREN
            if not getattr(self, 'bioinited', 0):
                blue.pyos.synchro.Yield()
                wnd.sr.bio = uicls.EditPlainText(parent=wnd.sr.bioparent, maxLength=MAXBIOLENGTH, showattributepanel=1)
                wnd.sr.bio.sr.window = self
                wnd.sr.bioparent.OnTabDeselect = self.AutoSaveBio
                wnd.oldbio = ''
                if not self.bio:
                    bio = sm.RemoteSvc('charMgr').GetCharacterDescription(eve.session.charid)
                    if bio is not None:
                        self.bio = bio
                    else:
                        self.bio = ''
                if not wnd or wnd.destroyed:
                    return
                if self.bio:
                    wnd.oldbio = self.bio
                self.bioinited = 1
            if wnd and not wnd.destroyed:
                wnd.sr.bio.SetValue(wnd.oldbio or localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/BioEdit/HereYouCanTypeBio'))
            return

    def AutoSaveBio(self, edit=None, *args):
        wnd = self.GetWnd()
        if not wnd:
            return
        edit = edit or wnd.sr.bio
        if not edit:
            return
        newbio = edit.GetValue()
        defaultBioString = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/BioEdit/HereYouCanTypeBio')
        newbio = newbio.replace(defaultBioString, '')
        if not len(uiutil.StripTags(newbio)):
            newbio = ''
        self.bio = newbio
        if wnd and newbio.strip() != wnd.oldbio:
            uthread.pool('CharaacterSheet::AutoSaveBio', self._AutoSaveBio, newbio)
            if wnd:
                wnd.oldbio = newbio

    def _AutoSaveBio(self, newbio):
        sm.RemoteSvc('charMgr').SetCharacterDescription(newbio)

    def QuickFilterReload(self):
        self._ReloadSkillTabs()

    def _ReloadSkillTabs(self):
        if self.showing == 'myskills_skills':
            self.skillTimer = base.AutoTimer(100, self.ShowMySkills)
        elif self.showing == 'myskills_certificates':
            self.certificateTimer = base.AutoTimer(100, self.ShowCertificates)
        elif self.showing == 'myskills_skillhistory':
            uthread.new(self.ShowMySkillHistory)

    def ReloadMyStandings(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            selection = [ each for each in wnd.sr.nav.GetSelected() if each.key == 'mystandings' ]
            if selection:
                self.showing = None
                self.Load('mystandings')
        return

    def ReloadMyRanks(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.sr.decoRankList = None
            selection = [ each for each in wnd.sr.nav.GetSelected() if each.key == 'mydecorations' ]
            if selection:
                self.showing = None
                self.Load('mydecorations')
        return

    def ShowMySkillHistory(self):
        wnd = self.GetWnd()
        if not wnd:
            return

        def GetPts(lvl):
            return charskills.GetSPForLevelRaw(stc, lvl)

        wnd.sr.nav.DeselectAll()
        wnd.sr.scroll.sr.id = 'charsheet_skillhistory'
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        rs = sm.GetService('skills').GetSkillHistory()
        scrolllist = []
        actions = {const.skillEventClonePenalty: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillClonePenalty'),
         const.skillEventTrainingStarted: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingStarted'),
         const.skillEventTrainingComplete: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingComplete'),
         const.skillEventTrainingCancelled: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingCanceled'),
         const.skillEventGMGive: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/GMGiveSkill'),
         const.skillEventQueueTrainingCompleted: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillTrainingComplete'),
         const.skillEventFreeSkillPointsUsed: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillPointsApplied'),
         const.skillEventSkillExtracted: localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillLevelExtracted')}
        for r in rs:
            skill = sm.GetService('skills').GetSkill(r.skillTypeID)
            if skill:
                stc = skill.skillRank
                levels = [0,
                 GetPts(1),
                 GetPts(2),
                 GetPts(3),
                 GetPts(4),
                 GetPts(5)]
                level = 5
                for i in range(len(levels)):
                    if levels[i] > r.absolutePoints:
                        level = i - 1
                        break

                data = util.KeyVal()
                data.label = util.FmtDate(r.logDate, 'ls') + '<t>'
                data.label += evetypes.GetName(r.skillTypeID) + '<t>'
                data.label += actions.get(r.eventTypeID, localization.GetByLabel('UI/Generic/Unknown')) + '<t>'
                data.label += localization.formatters.FormatNumeric(level)
                data.Set('sort_%s' % localization.GetByLabel('UI/Common/Date'), r.logDate)
                data.id = r.skillTypeID
                data.level = level
                data.GetMenu = self.GetItemMenu
                data.MenuFunction = self.GetItemMenu
                data.OnDblClick = (self.DblClickShowInfo, data)
                addItem = listentry.Get('Generic', data=data)
                scrolllist.append(addItem)

        wnd.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Common/Date'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Skill'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Action'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/Level')], noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/NoRecordsFound'), reversesort=True)

    def GetItemMenu(self, entry, *args):
        return [(localization.GetByLabel('UI/Common/ShowInfo'), self.ShowInfo, (entry.sr.node.id, 1))]

    def DblClickShowInfo(self, otherSelf, nodeData):
        skillTypeID = getattr(nodeData, 'id', None)
        if skillTypeID is not None:
            self.ShowInfo(skillTypeID)
        return

    def ShowInfo(self, *args):
        skillID = args[0]
        sm.StartService('info').ShowInfo(skillID, None)
        return

    def GetCombatEntries(self, recent, filterText=''):
        showAsCondensed = settings.user.ui.Get('charsheet_condensedcombatlog', 0)
        if showAsCondensed:
            headers = [localization.GetByLabel('UI/Common/Date'),
             localization.GetByLabel('UI/Common/Type'),
             localization.GetByLabel('UI/Common/Name'),
             localization.GetByLabel('UI/Common/Corporation'),
             localization.GetByLabel('UI/Common/Alliance'),
             localization.GetByLabel('UI/Common/Faction')]
        else:
            headers = []
        primeEveOwners = set()
        primeEveLocations = set()
        primeCorps = set()
        primeAlliances = set()
        ret = []
        unknownShipLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownShip')
        unknownNameLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownName')
        unknownCorporationLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownCorporation')
        unknownAllianceLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownAlliance')
        unknownFactionLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/UnknownFaction')
        for kill in recent:
            primeEveLocations.add(kill.solarSystemID)
            primeEveLocations.add(kill.moonID)
            primeEveOwners.add(kill.victimCharacterID)
            primeEveOwners.add(kill.victimCorporationID)
            primeCorps.add(kill.victimCorporationID)
            primeEveOwners.add(kill.victimAllianceID)
            primeAlliances.add(kill.victimAllianceID)
            primeEveOwners.add(kill.victimFactionID)
            primeEveOwners.add(kill.finalCharacterID)
            primeEveOwners.add(kill.finalCorporationID)
            primeCorps.add(kill.finalCorporationID)
            primeEveOwners.add(kill.finalAllianceID)
            primeAlliances.add(kill.finalAllianceID)
            primeEveOwners.add(kill.finalFactionID)

        cfg.eveowners.Prime(filter(None, primeEveOwners))
        cfg.evelocations.Prime(filter(None, primeEveLocations))
        cfg.corptickernames.Prime(filter(None, primeCorps))
        cfg.allianceshortnames.Prime(filter(None, primeAlliances))

        def GetOwnerName(ownerID):
            owner = cfg.eveowners.GetIfExists(ownerID)
            return getattr(owner, 'name', '')

        def GetTypeName(typeID):
            try:
                return evetypes.GetName(typeID)
            except evetypes.TypeNotFoundException:
                return ''

        def FilterOut(kill):
            if not filterText:
                return False
            if GetTypeName(kill.victimShipTypeID).lower().find(filterText) >= 0:
                return False
            for ownerID in [kill.victimCharacterID, kill.victimCorporationID, kill.victimAllianceID]:
                ownerName = GetOwnerName(ownerID)
                if ownerName.lower().find(filterText) >= 0:
                    return False

            return True

        for kill in recent:
            if FilterOut(kill):
                continue
            if showAsCondensed:
                data = util.KeyVal()
                timeOfKill = util.FmtDate(kill.killTime)
                shipOfCharacterKilled = GetTypeName(kill.victimShipTypeID) or unknownShipLabel
                characterKilled = GetOwnerName(kill.victimCharacterID) or unknownNameLabel
                corporationOfCharacterKilled = GetOwnerName(kill.victimCorporationID) or unknownCorporationLabel
                allianceOfCharacterKilled = GetOwnerName(kill.victimAllianceID) or unknownAllianceLabel
                factionOfCharacterKilled = GetOwnerName(kill.victimFactionID) or unknownFactionLabel
                labelList = [timeOfKill,
                 shipOfCharacterKilled,
                 characterKilled,
                 corporationOfCharacterKilled,
                 allianceOfCharacterKilled,
                 factionOfCharacterKilled]
                data.label = '<t>'.join(labelList)
                data.GetMenu = self.GetCombatMenu
                data.OnDblClick = (self.GetCombatDblClick, data)
                data.kill = kill
                data.mail = kill
                ret.append(listentry.Get('KillMailCondensed', data=data))
            else:
                ret.append(listentry.Get('KillMail', {'mail': kill}))

        return (ret, headers)

    def GetCombatDblClick(self, entry, *args):
        kill = entry.sr.node.kill
        if kill is not None:
            OpenKillReport(kill)
        return

    def GetCombatMenu(self, entry, *args):
        m = [(uiutil.MenuLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/CopyKillInfo'), self.GetCombatText, (entry.sr.node.kill, 1)), (uiutil.MenuLabel('UI/Control/Entries/CopyExternalKillLink'), self.GetCrestUrl, (entry.sr.node.kill,))]
        return m

    def ReloadKillReports(self):
        combatSetting = settings.user.ui.Get('CombatLogCombo', 0)
        offset = None
        if combatSetting == 0:
            if self.prevKillIDs and self.combatPageNum:
                offset = self.prevKillIDs[self.combatPageNum]
            self.ShowCombatKills(offset)
        else:
            if self.prevLossIDs and self.combatPageNum:
                offset = self.prevLossIDs[self.combatPageNum]
            self.ShowCombatLosses(offset)
        return

    def ShowKillsEx(self, recent, func, combatType, pageNum):
        if combatType == 'kills':
            prevType = self.prevKillIDs
        else:
            prevType = self.prevLossIDs
        wnd = self.GetWnd()
        if not wnd:
            return
        filterText = wnd.killReportQuickFilter.GetValue().lower()
        scrolllist, headers = self.GetCombatEntries(recent, filterText=filterText)
        for c in wnd.sr.btnContainer.children:
            c.state = uiconst.UI_HIDDEN

        wnd.sr.btnContainer.state = uiconst.UI_HIDDEN
        killIDs = [ k.killID for k in recent ]
        prevbtn = wnd.sr.btnContainer.children[1]
        nextbtn = wnd.sr.btnContainer.children[0]
        if pageNum > 0:
            wnd.sr.btnContainer.state = uiconst.UI_NORMAL
            prevbtn.state = uiconst.UI_NORMAL
            if combatType == 'kills':
                pageIndex = min(pageNum, len(self.prevKillIDs) - 1)
                prevType = self.prevKillIDs[pageIndex - 1]
            else:
                pageIndex = min(pageNum, len(self.prevLossIDs) - 1)
                prevType = self.prevLossIDs[pageIndex - 1]
            prevbtn.OnClick = (func, prevType, -1)
        maxKillIDs = max(killIDs) + 1 if killIDs else 0
        if combatType == 'kills' and pageNum + 1 > len(self.prevKillIDs):
            self.prevKillIDs.append(maxKillIDs)
        elif pageNum + 1 > len(self.prevLossIDs):
            self.prevLossIDs.append(maxKillIDs)
        if len(recent) >= self.killentries:
            wnd.sr.btnContainer.state = uiconst.UI_NORMAL
            nextbtn.state = uiconst.UI_NORMAL
            nextbtn.OnClick = (func, min(killIDs), 1)
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        isCondensed = settings.user.ui.Get('charsheet_condensedcombatlog', 0)
        if isCondensed:
            wnd.sr.scroll.sr.id = 'charsheet_kills'
        else:
            wnd.sr.scroll.sr.id = 'charsheet_kills2'
        noContentHintText = ''
        if combatType == 'kills':
            noContentHintText = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/NoKillsFound')
        elif combatType == 'losses':
            noContentHintText = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/NoLossesFound')
        pos = wnd.sr.scroll.GetScrollProportion()
        wnd.sr.scroll.Load(contentList=scrolllist, headers=headers, scrollTo=pos, noContentHint=noContentHintText)

    def GetCombatText(self, kill, isCopy=0):
        ret = util.CombatLog_CopyText(kill)
        if isCopy:
            blue.pyos.SetClipboardData(util.CleanKillMail(ret))
        else:
            return ret

    def GetCrestUrl(self, killmail):
        crest_url = util.GetPublicCrestUrl('killmails', killmail.killID, util.GetKillReportHashValue(killmail))
        blue.pyos.SetClipboardData(crest_url)

    def OnCombatChange(self, *args):
        wnd = self.GetWnd()
        selected = wnd.sr.combatCombo.GetValue()
        settings.user.ui.Set('CombatLogCombo', selected)
        self.combatPageNum = 0
        if selected == 0:
            self.ShowCombatKills()
        else:
            self.ShowCombatLosses()

    def ShowCombatKills(self, startFrom=None, pageChange=0, *args):
        recent = sm.GetService('info').GetKillsRecentKills(self.killentries, startFrom)
        self.combatPageNum = max(0, self.combatPageNum + pageChange)
        self.ShowKillsEx(recent, self.ShowCombatKills, 'kills', pageNum=self.combatPageNum)

    def ShowCombatLosses(self, startFrom=None, pageChange=0, *args):
        recent = sm.GetService('info').GetKillsRecentLosses(self.killentries, startFrom)
        self.combatPageNum = max(0, self.combatPageNum + pageChange)
        self.ShowKillsEx(recent, self.ShowCombatLosses, 'losses', pageNum=self.combatPageNum)

    def ShowKills(self):
        self.prevKillIDs = []
        self.prevLossIDs = []
        self.combatPageNum = 0
        selectedCombatType = settings.user.ui.Get('CombatLogCombo', 0)
        if selectedCombatType == 0:
            self.ShowCombatKills()
        else:
            self.ShowCombatLosses()

    @telemetry.ZONE_METHOD
    def ShowSkills(self, key):
        if key == 'myskills_skills':
            self.ShowMySkills(force=True)
            LogOpenCharacterSkills()
        elif key == 'myskills_certificates':
            self.ShowCertificates()
        elif key == 'myskills_skillhistory':
            self.ShowMySkillHistory()

    def ShowCertificates(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        else:
            self.certificateTimer = None
            showOnlyMine = settings.user.ui.Get('charsheet_showOnlyMyCerts', False)
            if getattr(wnd.sr, 'skillpanel', None):
                wnd.sr.skillpanel.state = uiconst.UI_NORMAL
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            self.SetHint()
            scrolllist = []
            myCategories = sm.GetService('certificates').GetMyCertificatesByCategoryID()
            allCategories = sm.GetService('certificates').GetAllCertificatesByCategoryID()
            if showOnlyMine:
                visibleCategories = myCategories
            else:
                visibleCategories = allCategories
            myFilter = wnd.quickFilter.GetValue()
            for groupID, certificates in visibleCategories.iteritems():
                if len(myFilter):
                    certificates = uiutil.NiceFilter(self.FilterCertificates, certificates[:])
                if len(certificates) == 0:
                    continue
                label = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/CertificateGroupWithCount', groupName=evetypes.GetGroupNameByGroup(groupID), certificatesCompleted=len(myCategories[groupID]), certificatesTotal=len(allCategories[groupID]))
                data = {'GetSubContent': self.GetCertSubContent,
                 'label': label,
                 'groupItems': certificates,
                 'id': ('charsheetGroups_cat', groupID),
                 'sublevel': 0,
                 'showlen': 0,
                 'showicon': 'hide',
                 'state': 'locked',
                 'forceOpen': bool(myFilter)}
                scrolllist.append(listentry.Get('Group', data))

            scrolllist = localization.util.Sort(scrolllist, key=lambda x: x.label)
            wnd.sr.scroll.sr.id = 'charsheet_mycerts'
            contentHint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/NoCertificatesFound')
            wnd.sr.scroll.Load(contentList=scrolllist, noContentHint=contentHint)
            return

    def FilterCertificates(self, certificate):
        wnd = self.GetWnd()
        if not wnd:
            return
        filterVal = wnd.quickFilter.GetValue().lower()
        return certificate.GetName().lower().find(filterVal) + 1

    def GetCertSubContent(self, dataX, *args):
        wnd = self.GetWnd()
        toggleGroups = settings.user.ui.Get('charsheet_toggleOneCertGroupAtATime', 1)
        if toggleGroups and not dataX.forceOpen:
            dataWnd = uicontrols.Window.GetIfOpen(windowID=unicode(dataX.id))
            if not dataWnd:
                for entry in wnd.sr.scroll.GetNodes():
                    if entry.__guid__ != 'listentry.Group' or entry.id == dataX.id:
                        continue
                    if entry.open:
                        if entry.panel:
                            entry.panel.Toggle()
                        else:
                            uicore.registry.SetListGroupOpenState(entry.id, 0)
                            entry.scroll.PrepareSubContent(entry)

        entries = self.GetCertificateEntries(dataX)
        return entries

    def GetCertificateEntries(self, data, *args):
        scrolllist = [ self.CreateCertificateEntry(d) for d in data.groupItems ]
        return localization.util.Sort(scrolllist, key=lambda x: x.label)

    def CreateCertificateEntry(self, certificate, *args):
        level = certificate.GetLevel()
        certificate = util.KeyVal(label=certificate.GetName(), certID=certificate.certificateID, level=level, iconID='res:/UI/Texture/Classes/Certificates/level%sSmall.png' % level)
        return listentry.Get(data=certificate, decoClass=listentry.CertEntryBasic)

    @telemetry.ZONE_METHOD
    def ShowMySkills(self, force=False):
        if not force and self.showing != 'myskills_skills':
            return
        else:
            self.skillTimer = None
            wnd = self.GetWnd()
            if not wnd:
                return
            if getattr(wnd.sr, 'skillpanel', None):
                wnd.sr.skillpanel.state = uiconst.UI_NORMAL
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            advancedView = settings.user.ui.Get('charsheet_showSkills', 'trained') in ('mytrainable', 'alltrainable')
            groups = sm.GetService('skills').GetSkillGroups(advancedView)
            scrolllist = []
            skillCount = sm.GetService('skills').GetSkillCount()
            skillPoints = sm.StartService('skills').GetFreeSkillPoints()
            if skillPoints > 0:
                text = '<color=0xFF00FF00>' + localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/UnAllocatedSkillPoints', skillPoints=skillPoints) + '</color>'
                hint = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ApplySkillHint')
                scrolllist.append(listentry.Get('Text', {'text': text,
                 'hint': hint}))
            currentSkillPoints = 0
            for group, skills, untrained, intraining, inqueue, points in groups:
                currentSkillPoints += points

            skillText = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/YouCurrentlyHaveSkills', numSkills=skillCount, currentSkillPoints=currentSkillPoints)
            scrolllist.append(listentry.Get('Text', {'text': skillText}))

            @telemetry.ZONE_METHOD
            def Published(skill):
                return evetypes.IsPublished(skill.typeID)

            for group, skills, untrained, intraining, inqueue, points in groups:
                untrained = filter(Published, untrained)
                if not len(skills) and not advancedView:
                    continue
                tempList = []
                if advancedView and settings.user.ui.Get('charsheet_showSkills', 'trained') == 'mytrainable':
                    for utrained in untrained[:]:
                        isSkillReqMet = sm.GetService('skills').IsSkillRequirementMet(utrained.typeID)
                        isTrialRestricted = sm.GetService('skills').IsTrialRestricted(utrained.typeID)
                        if isSkillReqMet and not isTrialRestricted:
                            tempList.append(utrained)

                    combinedSkills = skills[:] + tempList[:]
                    if not len(skills) and tempList == []:
                        continue
                if settings.user.ui.Get('charsheet_showSkills', 'trained') == 'alltrainable':
                    combinedSkills = skills[:] + untrained[:]
                numInQueueLabel = ''
                label = None
                if len(inqueue):
                    if len(intraining):
                        labelPath = 'UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillsInQueueTraining'
                    else:
                        labelPath = 'UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillsInQueue'
                    numInQueueLabel = localization.GetByLabel(labelPath, skillsInQueue=len(inqueue))
                if advancedView:
                    label = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillGroupOverviewAdvanced', groupName=group.groupName, skills=len(skills), totalSkills=len(combinedSkills), points=points, skillsInQueue=numInQueueLabel)
                else:
                    label = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/SkillGroupOverviewSimple', groupName=group.groupName, skills=len(skills), points=points, skillsInQueue=numInQueueLabel)
                    combinedSkills = skills[:]
                if settings.user.ui.Get('charsheet_hideLevel5Skills', False) == True:
                    for skill in skills:
                        if skill.skillLevel == 5:
                            combinedSkills.remove(skill)

                if settings.user.ui.Get('charsheet_hideUntrainedSkills', False) == True:
                    combinedSkills = filter(lambda s: s.skillPoints > 0, combinedSkills)
                myFilter = wnd.quickFilter.GetValue()
                if len(myFilter):
                    combinedSkills = uiutil.NiceFilter(wnd.quickFilter.QuickFilter, combinedSkills)
                if len(combinedSkills) == 0:
                    continue
                data = {'GetSubContent': self.GetSubContent,
                 'DragEnterCallback': self.OnGroupDragEnter,
                 'DeleteCallback': self.OnGroupDeleted,
                 'MenuFunction': self.GetMenu,
                 'label': label,
                 'groupItems': combinedSkills,
                 'inqueue': inqueue,
                 'id': ('myskills', group.groupID),
                 'tabs': [],
                 'state': 'locked',
                 'showicon': 'hide',
                 'showlen': 0,
                 'forceOpen': bool(myFilter)}
                scrolllist.append(listentry.Get('Group', data))

            scrolllist.append(listentry.Get('Space', {'height': 64}))
            pos = wnd.sr.scroll.GetScrollProportion()
            wnd.sr.scroll.sr.id = 'charsheet_myskills'
            wnd.sr.scroll.Load(contentList=scrolllist, headers=[], scrollTo=pos)
            return

    @telemetry.ZONE_METHOD
    def GetSubContent(self, data, *args):
        scrolllist = []
        wnd = self.GetWnd()
        if not wnd:
            return
        else:
            skillQueueSvc = sm.GetService('skillqueue')
            skillqueue = skillQueueSvc.GetServerQueue()
            skillqueue = {(x.trainingTypeID, x.trainingToLevel):idx for idx, x in enumerate(skillqueue)}
            mySkills = sm.GetService('skills').GetSkills()
            skillsInQueue = data.inqueue
            skillInTraining = skillQueueSvc.SkillInTraining()
            toggleGroups = settings.user.ui.Get('charsheet_toggleOneSkillGroupAtATime', 1)
            if toggleGroups and not data.forceOpen:
                dataWnd = uicontrols.Window.GetIfOpen(unicode(data.id))
                if not dataWnd:
                    for entry in wnd.sr.scroll.GetNodes():
                        if entry.__guid__ != 'listentry.Group' or entry.id == data.id:
                            continue
                        if entry.open:
                            if entry.panel:
                                entry.panel.Toggle()
                            else:
                                uicore.registry.SetListGroupOpenState(entry.id, 0)
                                entry.scroll.PrepareSubContent(entry)

            skillsInGroup = localization.util.Sort(data.groupItems, key=lambda x: evetypes.GetName(x.typeID))
            for skill in skillsInGroup:
                inQueue = None
                if skill.typeID in skillsInQueue:
                    for i in xrange(5, skill.skillLevel, -1):
                        if (skill.typeID, i) in skillqueue:
                            inQueue = i
                            break

                inTraining = 0
                if skillInTraining and skill.typeID == skillInTraining.typeID:
                    inTraining = 1
                data = {'invtype': skill.typeID,
                 'skill': skill,
                 'trained': skill.typeID in mySkills,
                 'plannedInQueue': inQueue,
                 'skillID': skill.typeID,
                 'inTraining': inTraining}
                scrolllist.append(listentry.Get('SkillEntry', data))

            return scrolllist

    def OnGroupDeleted(self, ids):
        pass

    def OnGroupDragEnter(self, group, drag):
        pass

    def GetMenu(self, *args):
        return []

    def ShowStandings(self, positive):
        wnd = self.GetWnd()
        if not wnd:
            return
        self.SetHint()
        scrolllist = sm.GetService('standing').GetStandingEntries(positive, eve.session.charid)
        wnd.sr.scroll.sr.id = 'charsheet_standings'
        wnd.sr.scroll.Load(contentList=scrolllist)

    def UpdateMyAttributes(self, attributeID, value):
        wnd = self.GetWnd()
        if not wnd:
            return
        for entry in wnd.sr.scroll.GetNodes():
            if entry.attributeID == attributeID:
                entry.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/Points', skillPoints=int(value))
                if entry.panel:
                    entry.panel.sr.text.text = entry.text
                    entry.panel.hint = entry.text.replace('<t>', '  ')

    def ShowMyAttributes(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
        self.SetHint()
        scrollList = sm.GetService('info').GetAttributeScrollListForItem(itemID=eve.session.charid, typeID=const.typeCharacterAmarr, attrList=[const.attributePerception,
         const.attributeMemory,
         const.attributeWillpower,
         const.attributeIntelligence,
         const.attributeCharisma])
        respecInfo = sm.GetService('skills').GetRespecInfo()
        self.respecEntry = listentry.Get('AttributeRespec', data=util.KeyVal(nextTimedRespec=respecInfo['nextTimedRespec'], freeRespecs=respecInfo['freeRespecs']))
        scrollList.append(self.respecEntry)
        wnd.sr.scroll.sr.id = 'charsheet_myattributes'
        wnd.sr.scroll.Load(fixedEntryHeight=32, contentList=scrollList, noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Attributes/NoAttributesFound'))

    def CheckBoxChange(self, checkbox):
        if checkbox.name == 'charsheet_condensedcombatlog':
            settings.user.ui.Set('charsheet_condensedcombatlog', checkbox.checked)
            self.ShowKills()
        elif checkbox.data.has_key('key'):
            key = checkbox.data['key']
            if key == 'charsheet_showSkills':
                if checkbox.data['retval'] is None:
                    settings.user.ui.Set(key, checkbox.checked)
                else:
                    settings.user.ui.Set(key, checkbox.data['retval'])
            else:
                settings.user.ui.Set(key, checkbox.checked)
        return

    def ShowMyImplantsAndBoosters(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        else:
            wnd.sr.scroll.state = uiconst.UI_PICKCHILDREN
            self.SetHint()
            mygodma = self.GetMyGodmaItem(eve.session.charid)
            if not mygodma:
                return
            implants = mygodma.implants
            boosters = mygodma.boosters
            godma = sm.GetService('godma')
            implants = uiutil.SortListOfTuples([ (getattr(godma.GetType(implant.typeID), 'implantness', None), implant) for implant in implants ])
            boosters = uiutil.SortListOfTuples([ (getattr(godma.GetType(booster.boosterTypeID), 'boosterness', None), booster) for booster in boosters ])
            scrolllist = []
            if implants:
                scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/Implants', implantCount=len(implants))}))
                for each in implants:
                    scrolllist.append(listentry.Get('ImplantEntry', {'implant_booster': each,
                     'label': evetypes.GetName(each.typeID)}))

                if boosters:
                    scrolllist.append(listentry.Get('Divider'))
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
            staticMgr = dogmaLocation.dogmaStaticMgr
            if boosters:
                scrolllist.append(listentry.Get('Header', {'label': localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/Boosters', boosterCount=len(boosters))}))
                for each in boosters:
                    scrolllist.append(listentry.Get('ImplantEntry', {'implant_booster': each,
                     'label': evetypes.GetName(each.boosterTypeID)}))
                    boosterEffects = staticMgr.passiveFilteredEffectsByType.get(each.boosterTypeID, [])
                    for effectID in boosterEffects:
                        eff = cfg.dgmeffects.Get(effectID)
                        chanceAttributeID = staticMgr.effects[effectID].fittingUsageChanceAttributeID
                        if chanceAttributeID and effectID in each.sideEffectIDs:
                            scrolllist.append(listentry.Get('IconEntry', {'line': 1,
                             'hint': eff.displayName,
                             'text': None,
                             'label': eff.displayName,
                             'icon': util.IconFile(eff.iconID),
                             'selectable': 0,
                             'iconoffset': 32,
                             'iconsize': 22,
                             'linecolor': (1.0, 1.0, 1.0, 0.125)}))

                    scrolllist.append(listentry.Get('Divider'))

            wnd.sr.scroll.sr.id = 'charsheet_implantandboosters'
            wnd.sr.scroll.Load(fixedEntryHeight=32, contentList=scrolllist, noContentHint=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Augmentations/NoImplantOrBoosterInEffect'))
            return

    def GetMyGodmaItem(self, itemID):
        ret = sm.GetService('godma').GetItem(itemID)
        while ret is None and not getattr(getattr(self, 'wnd', None), 'destroyed', 1):
            self.LogWarn('godma item not ready yet. sleeping for it...')
            blue.pyos.synchro.SleepWallclock(500)
            ret = sm.GetService('godma').GetItem(itemID)

        return ret

    def GetBoosterSubContent(self, nodedata):
        scrolllist = []
        for each in nodedata.groupItems:
            entry = listentry.Get('LabelTextTop', {'line': 1,
             'label': each[0],
             'text': each[1],
             'iconID': each[2]})
            scrolllist.append(entry)

        return localization.util.Sort(scrolllist, key=lambda x: x.label)

    def GoTo(self, URL, data=None, args={}, scrollTo=None):
        URL = URL.encode('cp1252', 'replace')
        if URL.startswith('showinfo:') or URL.startswith('evemail:') or URL.startswith('evemailto:'):
            self.output.GoTo(self, URL, data, args)
        else:
            uicore.cmd.OpenBrowser(URL, data=data, args=args)

    def ShowMyDecorationPermissions(self):
        scrollHeaders = [localization.GetByLabel('UI/CharacterCreation/FirstName'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'),
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'),
         localization.GetByLabel('UI/PI/Common/Remove')]
        wnd = self.GetWnd()
        if not wnd:
            return
        wnd.sr.scroll.sr.fixedColumns = {localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'): 60,
         localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'): 60}
        wnd.sr.scroll.sr.id = 'charsheet_decopermissions'
        wnd.sr.scroll.Load(contentList=[], headers=scrollHeaders)
        wnd.sr.scroll.OnColumnChanged = self.OnDecorationPermissionsColumnChanged
        publicDeco = sm.StartService('medals').GetMedalsReceivedWithFlag(session.charid, [3])
        privateDeco = sm.StartService('medals').GetMedalsReceivedWithFlag(session.charid, [2])
        ppKeys = [ each for each in publicDeco.keys() + privateDeco.keys() ]
        scrolllist = []
        inMedalList = []
        characterMedals, characterMedalInfo = sm.StartService('medals').GetMedalsReceived(session.charid)
        for characterMedal in characterMedals:
            medalID = characterMedal.medalID
            if medalID not in ppKeys:
                continue
            if medalID in inMedalList:
                continue
            inMedalList.append(medalID)
            details = characterMedalInfo.Filter('medalID')
            if details and details.has_key(medalID):
                details = details.get(medalID)
            entry = self.CreateDecorationPermissionsEntry(characterMedal)
            if entry:
                scrolllist.append(entry)

        wnd.sr.scroll.Load(contentList=scrolllist, headers=scrollHeaders, noContentHint=localization.GetByLabel('UI/Common/NothingFound'))
        self.OnDecorationPermissionsColumnChanged()

    def CreateDecorationPermissionsEntry(self, data):
        entry = {'line': 1,
         'label': data.title + '<t><t><t>',
         'itemID': data.medalID,
         'visibilityFlags': data.status,
         'indent': 3,
         'selectable': 0}
        return listentry.Get('DecorationPermissions', entry)

    def OnDecorationPermissionsColumnChanged(self, *args, **kwargs):
        wnd = self.GetWnd()
        if not wnd:
            return
        else:
            for entry in wnd.sr.scroll.GetNodes():
                if entry.panel and getattr(entry.panel, 'OnColumnChanged', None):
                    entry.panel.OnColumnChanged()

            return

    def SaveDecorationPermissionsChanges(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        else:
            promptForDelete = False
            changes = {}
            for entry in wnd.sr.scroll.GetNodes():
                if entry.panel and hasattr(entry.panel, 'flag'):
                    if entry.panel.HasChanged():
                        if entry.panel.flag == 1:
                            promptForDelete = True
                        changes[entry.panel.sr.node.itemID] = entry.panel.flag

            if promptForDelete == False or eve.Message('DeleteMedalConfirmation', {}, uiconst.YESNO) == uiconst.ID_YES:
                if len(changes) > 0:
                    sm.StartService('medals').SetMedalStatus(changes)
            wnd.sr.decoMedalList = None
            return

    def SetAllDecorationPermissions(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        else:
            permissionList = [(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Private'), 2), (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/Public'), 3)]
            pickedPermission = uix.ListWnd(permissionList, 'generic', localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/SetAllDecorationPermissions'), localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/SaveAllChangesImmediately'), windowName='permissionPickerWnd')
            if not pickedPermission:
                return
            permissionID = pickedPermission[1]
            m, _ = sm.StartService('medals').GetMedalsReceived(session.charid)
            myDecos = []
            for each in m:
                if each.status != 1:
                    myDecos.append(each.medalID)

            myDecos = list(set(myDecos))
            updateDict = {}
            for decoID in myDecos:
                updateDict[decoID] = permissionID

            if len(updateDict) > 0:
                sm.StartService('medals').SetMedalStatus(updateDict)
                wnd.sr.decoMedalList = None
                self.ShowMyDecorations('mydecorations_permissions')
            return

    def ShowPilotLicense(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            return
        if not getattr(wnd.sr, 'plexBackground'):
            scrollContainer = uicls.ScrollContainer(name='plexScroll', parent=wnd.sr.plexContainer, align=uiconst.TOALL, padding=(10, 10, 10, 10))
            uicontrols.EveLabelLargeBold(parent=scrollContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/PlexTitle'), padding=(10, 10, 0, 0))
            uicontrols.EveLabelMedium(parent=scrollContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/PlexDescription'), padding=(10, 2, 0, 10), color=util.Color.GRAY5)
            subscription = ContainerAutoSize(parent=scrollContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
            wnd.sr.plexSubscriptionLabel = uicontrols.EveLabelMedium(parent=subscription, align=uiconst.TOTOP, text='', padding=(75, 15, 0, 15))
            InfoIcon(parent=subscription, typeID=const.typePilotLicence, pos=(10, 2, 55, 55), texturePath='res:/UI/Texture/Icons/plex.png', iconOpacity=1.0)
            InfoIcon(parent=subscription, align=uiconst.TOPRIGHT, typeID=const.typePilotLicence, top=10, left=10)
            uicontrols.EveLabelLargeBold(parent=scrollContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/BuyingPlexTitle'), padding=(10, 10, 0, 0))
            uicontrols.EveLabelMedium(parent=scrollContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/BuyingPlexDescription'), padding=(10, 2, 0, 10), color=util.Color.GRAY5)
            buyButtons = FlowContainer(parent=scrollContainer, align=uiconst.TOTOP, contentAlignment=CONTENT_ALIGN_CENTER, contentSpacing=(8, 0))
            BuyButtonIsk(parent=buyButtons, align=uiconst.NOALIGN, typeID=const.typePilotLicence)
            BuyButtonPlex(parent=buyButtons, align=uiconst.NOALIGN, logContext='CharacterSheet')
            uicontrols.EveLabelLargeBold(parent=scrollContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/MultipleCharacterTitle'), padding=(10, 25, 0, 0))
            uicontrols.EveLabelMedium(parent=scrollContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/MultipleCharacterDescription'), padding=(10, 2, 0, 10), color=util.Color.GRAY5)
            multipleQueue1 = ContainerAutoSize(parent=scrollContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
            wnd.sr.multipleQueueLabel1 = uicontrols.EveLabelMediumBold(parent=multipleQueue1, align=uiconst.TOTOP, text='', padding=(35, 8, 0, 8))
            wnd.sr.multipleQueueExpiryLabel1 = uicontrols.EveLabelMediumBold(parent=multipleQueue1, align=uiconst.TOPRIGHT, text='', pos=(10, 8, 0, 0), color=util.Color.GRAY5)
            wnd.sr.multipleQueueIcon1 = uicontrols.Icon(parent=multipleQueue1, align=uiconst.TOPLEFT, icon='res:/UI/Texture/Icons/additional_training_queue.png', pos=(10, 7, 17, 17))
            multipleQueue2 = ContainerAutoSize(parent=scrollContainer, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, bgColor=(0, 0, 0, 0.3))
            wnd.sr.multipleQueueLabel2 = uicontrols.EveLabelMediumBold(parent=multipleQueue2, align=uiconst.TOTOP, text='', padding=(35, 8, 0, 8))
            wnd.sr.multipleQueueExpiryLabel2 = uicontrols.EveLabelMediumBold(parent=multipleQueue2, align=uiconst.TOPRIGHT, text='', pos=(10, 8, 0, 0), color=util.Color.GRAY5)
            wnd.sr.multipleQueueIcon2 = uicontrols.Icon(parent=multipleQueue2, align=uiconst.TOPLEFT, icon='res:/UI/Texture/Icons/additional_training_queue.png', pos=(10, 7, 17, 17))
            uicontrols.EveLabelLargeBold(parent=scrollContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/ConvertAurumTitle'), padding=(10, 25, 0, 0))
            uicontrols.EveLabelMedium(parent=scrollContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/ConvertAurumDescription'), padding=(10, 2, 0, 0), color=util.Color.GRAY5)
            if boot.region != 'optic':
                uicontrols.EveLabelLargeBold(parent=scrollContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/CharacterTransferTitle'), padding=(10, 25, 0, 0))
                uicontrols.EveLabelMedium(parent=scrollContainer, align=uiconst.TOTOP, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/CharacterTransferDescription'), padding=(10, 2, 0, 0), color=util.Color.GRAY5)
            wnd.sr.plexBackground = FillThemeColored(parent=wnd.sr.plexContainer, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.1)
        wnd.sr.plexContainer.state = uiconst.UI_PICKCHILDREN
        wnd.sr.multipleQueueLabel1.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueNotActive')
        wnd.sr.multipleQueueLabel1.color = util.Color.GRAY5
        wnd.sr.multipleQueueExpiryLabel1.state = uiconst.UI_HIDDEN
        wnd.sr.multipleQueueIcon1.opacity = 0.3
        wnd.sr.multipleQueueLabel2.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueNotActive')
        wnd.sr.multipleQueueLabel2.color = util.Color.GRAY5
        wnd.sr.multipleQueueExpiryLabel2.state = uiconst.UI_HIDDEN
        wnd.sr.multipleQueueIcon2.opacity = 0.3
        for index, (trainingID, trainingExpiry) in enumerate(sorted(sm.GetService('skillqueue').GetMultipleCharacterTraining().iteritems())):
            if index == 0:
                wnd.sr.multipleQueueLabel1.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueActive')
                wnd.sr.multipleQueueLabel1.color = (0.0, 1.0, 0.0, 0.8)
                wnd.sr.multipleQueueExpiryLabel1.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueExpires', expiryDate=trainingExpiry)
                wnd.sr.multipleQueueExpiryLabel1.state = uiconst.UI_DISABLED
                wnd.sr.multipleQueueIcon1.opacity = 1.0
            elif index == 1:
                wnd.sr.multipleQueueLabel2.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueActive')
                wnd.sr.multipleQueueLabel2.color = (0.0, 1.0, 0.0, 0.8)
                wnd.sr.multipleQueueExpiryLabel2.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/AdditionalQueueExpires', expiryDate=trainingExpiry)
                wnd.sr.multipleQueueExpiryLabel2.state = uiconst.UI_DISABLED
                wnd.sr.multipleQueueIcon2.opacity = 1.0

        if self.GetSubscriptionDays():
            wnd.sr.plexSubscriptionLabel.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/DaysLeft', daysLeft=self.GetSubscriptionDays())
        else:
            wnd.sr.plexSubscriptionLabel.text = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/PilotLicense/Fine')

    def ShowSkins(self):
        wnd = self.GetWnd()
        if not wnd:
            return
        if not hasattr(wnd, 'skinsPanel'):
            return
        wnd.skinsPanel.state = uiconst.UI_PICKCHILDREN
        wnd.skinsPanel.Load()

    def OnSkinLicenseActivated(self, skinID):
        if self.showing == 'skins':
            self.ShowSkins()

    def GetSubscriptionDays(self, force=False):
        if self.daysLeft == -1 or force:
            charDetails = sm.RemoteSvc('charUnboundMgr').GetCharacterToSelect(eve.session.charid)
            self.daysLeft = getattr(charDetails[0], 'daysLeft', None) if len(charDetails) else None
        return self.daysLeft


class CharacterSheetWindow(uicontrols.Window):
    __guid__ = 'form.CharacterSheet'
    default_width = 497
    default_height = 456
    default_minSize = (497, 456)
    default_left = 0
    default_top = 32
    default_windowID = 'charactersheet'
    default_captionLabelPath = 'UI/CharacterSheet/CharacterSheetWindow/CharacterSheetCaption'
    default_descriptionLabelPath = 'Tooltips/Neocom/CharacterSheet_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/charactersheet.png'

    def OnUIRefresh(self):
        pass

    @telemetry.ZONE_METHOD
    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.characterSheetSvc = sm.GetService('charactersheet')
        self.sr.standingsinited = 0
        self.sr.skillsinited = 0
        self.sr.killsinited = 0
        self.sr.mydecorationsinited = 0
        self.sr.pilotlicenceinited = 0
        self.SetScope('station_inflight')
        self.IsBrowser = 1
        self.GoTo = self.characterSheetSvc.GoTo
        self.HideMainIcon()
        leftSide = Container(name='leftSide', parent=self.sr.main, align=uiconst.TOLEFT, left=const.defaultPadding, width=settings.user.ui.Get('charsheetleftwidth', 200), idx=0)
        self.sr.leftSide = leftSide
        self.sr.nav = uicontrols.Scroll(name='senderlist', parent=leftSide, padTop=const.defaultPadding, padBottom=const.defaultPadding)
        self.sr.nav.OnSelectionChange = self.characterSheetSvc.OnSelectEntry
        mainArea = Container(name='mainArea', parent=self.sr.main, align=uiconst.TOALL)
        self.sr.buttonParDeco = Container(name='buttonParDeco', align=uiconst.TOBOTTOM, height=25, parent=mainArea, state=uiconst.UI_HIDDEN)
        buttonDeco = Container(name='buttonDeco', align=uiconst.TOBOTTOM, height=15, parent=self.sr.buttonParDeco, padBottom=5)
        mainArea2 = Container(name='mainArea2', parent=mainArea, align=uiconst.TOALL)
        divider = Divider(name='divider', align=uiconst.TOLEFT, width=const.defaultPadding - 1, parent=mainArea2, state=uiconst.UI_NORMAL)
        divider.Startup(leftSide, 'width', 'x', 84, 220)
        self.sr.divider = divider
        Container(name='push', parent=mainArea2, state=uiconst.UI_PICKCHILDREN, width=const.defaultPadding, align=uiconst.TORIGHT)
        self.sr.skillpanel = ContainerAutoSize(parent=mainArea2, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, alignMode=uiconst.TOTOP, padTop=2)
        self.sr.combatlogpanel = Container(name='combatlogpanel', parent=mainArea2, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN, padTop=const.defaultPadding)
        self.skinsPanel = CharacterSkinsPanel(parent=mainArea2, align=uiconst.TOALL, state=uiconst.UI_HIDDEN, padTop=const.defaultPadding, padBottom=const.defaultPadding)
        combatValues = ((localization.GetByLabel('UI/Corporations/Wars/Killmails/ShowKills'), 0), (localization.GetByLabel('UI/Corporations/Wars/Killmails/ShowLosses'), 1))
        selectedCombatType = settings.user.ui.Get('CombatLogCombo', 0)
        self.sr.combatCombo = uicontrols.Combo(parent=self.sr.combatlogpanel, name='combo', select=selectedCombatType, align=uiconst.TOPLEFT, left=1, callback=self.characterSheetSvc.OnCombatChange, options=combatValues, idx=0, adjustWidth=True)
        self.sr.combatSetting = uicontrols.Checkbox(parent=self.sr.combatlogpanel, align=uiconst.TOPLEFT, pos=(0,
         self.sr.combatCombo.height + const.defaultPadding,
         300,
         14), configName='charsheet_condensedcombatlog', text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs/CondensedCombatLog'), checked=settings.user.ui.Get('charsheet_condensedcombatlog', 0), callback=self.characterSheetSvc.CheckBoxChange)
        self.killReportQuickFilter = uicls.QuickFilterEdit(parent=self.sr.combatlogpanel, left=const.defaultPadding, align=uiconst.TOPRIGHT, width=150)
        self.killReportQuickFilter.ReloadFunction = self.characterSheetSvc.ReloadKillReports
        self.sr.combatlogpanel.height = self.sr.combatCombo.height + self.sr.combatSetting.height + const.defaultPadding
        if not IsSkillInjectorBannerDismissed():
            SkillInjectorBanner(parent=self.sr.skillpanel, align=uiconst.TOTOP, padding=(4, 4, 4, 4))
        skillFilterCont = Container(parent=self.sr.skillpanel, align=uiconst.TOTOP, height=24)
        uicls.UtilMenu(parent=skillFilterCont, align=uiconst.CENTERLEFT, menuAlign=uiconst.BOTTOMLEFT, GetUtilMenu=self.GetSkillSettingsMenu, texturePath='res:/UI/Texture/SettingsCogwheel.png', width=16, height=16, iconSize=18)
        self.quickFilter = uicls.QuickFilterEdit(parent=skillFilterCont, align=uiconst.CENTERLEFT, width=80, left=18)
        self.quickFilter.ReloadFunction = self.characterSheetSvc.QuickFilterReload
        btn = uicontrols.Button(parent=skillFilterCont, align=uiconst.CENTERRIGHT, label=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/OpenTrainingQueue'), func=self.characterSheetSvc.OpenSkillQueueWindow, name='characterSheetOpenTrainingQueue')
        btns = [(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/SaveDecorationPermissionChanges'),
          self.characterSheetSvc.SaveDecorationPermissionsChanges,
          (),
          64), (localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/DecoTabs/SetAllDecorationPermissions'),
          self.characterSheetSvc.SetAllDecorationPermissions,
          (),
          64)]
        uicontrols.ButtonGroup(btns=btns, parent=buttonDeco, line=False)
        self.sr.scroll = uicontrols.Scroll(parent=mainArea2, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.sr.scroll.sr.id = 'charactersheetscroll'
        self.sr.hint = None
        self.sr.employmentList = None
        self.sr.decoRankList = None
        self.sr.decoMedalList = None
        self.sr.mainArea = mainArea
        self.sr.bioparent = Container(name='bio', parent=mainArea2, state=uiconst.UI_HIDDEN, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.sr.plexContainer = Container(name='plex', parent=mainArea2, state=uiconst.UI_HIDDEN, padding=(0,
         const.defaultPadding,
         0,
         const.defaultPadding))
        self.characterSheetSvc.LoadGeneralInfo()
        navEntries = self.characterSheetSvc.GetNavEntries(self)
        scrolllist = []
        for label, _, icon, key, _, UIName, descriptionLabelPath in navEntries:
            data = util.KeyVal()
            data.text = label
            data.label = label
            data.icon = icon
            data.key = key
            data.hint = label
            data.name = UIName
            data.line = False
            data.labeloffset = 4
            data.tooltipPanelClassInfo = TooltipHeaderDescriptionWrapper(header=label, description=localization.GetByLabel(descriptionLabelPath), tooltipPointer=uiconst.POINT_RIGHT_2)
            scrolllist.append(listentry.Get('IconEntry', data=data))

        self._CheckShowT3ShipLossMessage()
        self.sr.nav.Load(contentList=scrolllist)
        self.sr.nav.SetSelected(min(len(navEntries) - 1, settings.char.ui.Get('charactersheetselection', 0)))
        return

    @telemetry.ZONE_METHOD
    def _CheckShowT3ShipLossMessage(self):
        lossMessages = sm.StartService('skills').GetRecentLossMessages()
        for messageTuple in lossMessages:
            messageType, messageDict = messageTuple
            eve.Message(messageType, messageDict)

        if len(lossMessages):
            sm.GetService('skills').ResetSkillHistory()

    def Close(self, *args, **kwds):
        sm.GetService('charactersheet').OnCloseWnd(self)
        uicontrols.Window.Close(self, *args, **kwds)

    def GetSkillSettingsMenu(self, menuParent):
        if sm.GetService('charactersheet').showing == 'myskills_skills':
            return self.GetSkillSkillSettingsMenu(menuParent)
        else:
            return self.GetSkillCertSettingsMenu(menuParent)

    def GetSkillSkillSettingsMenu(self, menuParent):
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ShowOnlyCurrentSkills'), checked=settings.user.ui.Get('charsheet_showSkills', 'trained') == 'trained', callback=self.SetShowSkillsTrained)
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ShowOnlyTrainableSkills'), checked=settings.user.ui.Get('charsheet_showSkills', 'trained') == 'mytrainable', callback=self.SetShowSkillsMyTrainable)
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ShowAllSkills'), checked=settings.user.ui.Get('charsheet_showSkills', 'trained') == 'alltrainable', callback=self.SetShowSkillsAll)
        menuParent.AddDivider()
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/HighlightPartiallyTrainedSkills'), checked=settings.user.ui.Get('charsheet_hilitePartiallyTrainedSkills', False), callback=self.ToggleHighlightPartiallyTrainedSkills)
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ToggleOneSkillGroupAtATime'), checked=settings.user.ui.Get('charsheet_toggleOneSkillGroupAtATime', False), callback=self.ToggleOneSkillGroup)
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/HideLvl5'), checked=settings.user.ui.Get('charsheet_hideLevel5Skills', False), callback=self.ToggleHideLevel5Skills)
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/HideUntrained'), checked=settings.user.ui.Get('charsheet_hideUntrainedSkills', False), callback=self.ToggleHideUntrainedSkills)

    def SetShowSkillsTrained(self):
        settings.user.ui.Set('charsheet_showSkills', 'trained')
        sm.GetService('charactersheet').ShowMySkills()

    def SetShowSkillsMyTrainable(self):
        settings.user.ui.Set('charsheet_showSkills', 'mytrainable')
        sm.GetService('charactersheet').ShowMySkills()

    def SetShowSkillsAll(self):
        settings.user.ui.Set('charsheet_showSkills', 'alltrainable')
        sm.GetService('charactersheet').ShowMySkills()

    def ToggleHighlightPartiallyTrainedSkills(self):
        current = settings.user.ui.Get('charsheet_hilitePartiallyTrainedSkills', False)
        settings.user.ui.Set('charsheet_hilitePartiallyTrainedSkills', not current)
        sm.GetService('charactersheet').ShowMySkills()

    def ToggleOneSkillGroup(self):
        current = settings.user.ui.Get('charsheet_toggleOneSkillGroupAtATime', False)
        settings.user.ui.Set('charsheet_toggleOneSkillGroupAtATime', not current)
        sm.GetService('charactersheet').ShowMySkills()

    def ToggleHideLevel5Skills(self):
        current = settings.user.ui.Get('charsheet_hideLevel5Skills', False)
        settings.user.ui.Set('charsheet_hideLevel5Skills', not current)
        sm.GetService('charactersheet').ShowMySkills()

    def ToggleHideUntrainedSkills(self):
        current = settings.user.ui.Get('charsheet_hideUntrainedSkills', False)
        settings.user.ui.Set('charsheet_hideUntrainedSkills', not current)
        sm.GetService('charactersheet').ShowMySkills()

    def GetSkillCertSettingsMenu(self, menuParent):
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/ToggleShowOnlyMyCertificates'), checked=settings.user.ui.Get('charsheet_showOnlyMyCerts', False), callback=self.ToggleShowOnlyMyCerts)
        menuParent.AddCheckBox(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/CertTabs/ToggleOneCertificationGroupAtATime'), checked=settings.user.ui.Get('charsheet_toggleOneCertGroupAtATime', True), callback=self.ToggleOneCertGroup)

    def ToggleShowOnlyMyCerts(self):
        current = settings.user.ui.Get('charsheet_showOnlyMyCerts', False)
        settings.user.ui.Set('charsheet_showOnlyMyCerts', not current)
        sm.GetService('charactersheet').ShowCertificates()

    def ToggleOneCertGroup(self):
        current = settings.user.ui.Get('charsheet_toggleOneCertGroupAtATime', True)
        settings.user.ui.Set('charsheet_toggleOneCertGroupAtATime', not current)
        sm.GetService('charactersheet').ShowCertificates()


class CloneButtons(uicontrols.SE_BaseClassCore):
    __guid__ = 'listentry.CloneButtons'
    default_showHilite = False

    def Startup(self, args):
        jumpText = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Jump')
        self.sr.JumpBtn = uicontrols.Button(parent=self, label=jumpText, align=uiconst.CENTER, func=self.OnClickJump)
        destroyLabel = localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/JumpCloneScroll/Destroy')
        self.sr.DecomissionBtn = uicontrols.Button(parent=self, label=destroyLabel, align=uiconst.CENTER, func=self.OnClickDecomission)
        LineThemeColored(parent=self, align=uiconst.TOBOTTOM, opacity=0.4)

    def Load(self, node):
        self.sr.node = node
        self.locationID = node.locationID
        self.jumpCloneID = node.jumpCloneID
        self.sr.JumpBtn.width = self.sr.DecomissionBtn.width = max(self.sr.JumpBtn.width, self.sr.DecomissionBtn.width)
        self.sr.JumpBtn.left = -self.sr.JumpBtn.width / 2
        self.sr.DecomissionBtn.left = self.sr.DecomissionBtn.width / 2
        self.sr.JumpBtn.Disable()
        self.sr.DecomissionBtn.Disable()
        validLocation = self.locationID in cfg.evelocations
        if validLocation:
            self.sr.DecomissionBtn.Enable()
            if session.stationid or session.structureid:
                self.sr.JumpBtn.Enable()

    def GetHeight(self, *args):
        node, _ = args
        node.height = 32
        return node.height

    def OnClickJump(self, *args):
        sm.GetService('clonejump').CloneJump(self.locationID)

    def OnClickDecomission(self, *args):
        sm.GetService('clonejump').DestroyInstalledClone(self.jumpCloneID)


class CombatDetailsWnd(uicontrols.Window):
    __guid__ = 'form.CombatDetailsWnd'
    default_windowID = 'CombatDetails'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/KillsTabs'))
        self.HideMainIcon()
        self.SetTopparentHeight(0)
        ret = attributes.ret
        uicontrols.ButtonGroup(btns=[[localization.GetByLabel('UI/Common/Buttons/Close'),
          self.CloseByUser,
          None,
          81]], parent=self.sr.main)
        self.edit = uicontrols.Edit(parent=self.sr.main, align=uiconst.TOALL, readonly=True)
        self.UpdateDetails(ret)
        return

    def UpdateDetails(self, ret=''):
        self.edit.SetValue(ret)


def LogOpenCharacterSkills():
    uthread.new(LogMultiPilotTrainingBannerImpression)


def LogOpenPilotLicense():
    uthread.new(LogCharacterSheetPilotLicenseImpression)