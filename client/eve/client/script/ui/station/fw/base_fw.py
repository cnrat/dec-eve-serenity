# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\fw\base_fw.py
from math import pi
import math
from eve.client.script.ui.control.themeColored import GradientThemeColored
import uicontrols
import blue
from eve.client.script.ui.control import entries as listentry
import moniker
import uiprimitives
import uthread
import util
import uicls
import carbonui.const as uiconst
import localization
import log
import facwarCommon

class MilitiaWindow(uicontrols.Window):
    __guid__ = 'form.MilitiaWindow'
    __notifyevents__ = ['OnJoinMilitia',
     'OnRankChange',
     'OnSessionChanged',
     'OnSystemStatusChanged']
    default_width = 650
    default_height = 660
    default_minSize = (500, 520)
    default_topParentHeight = 0
    default_windowID = 'factionalWarfare'
    default_captionLabelPath = 'Tooltips/StationServices/FactionalWarfare'
    default_descriptionLabelPath = 'Tooltips/StationServices/FactionalWarfare_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/factionalwarfare.png'

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.factionalWarStatus = None
        self.topCont = uiprimitives.Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, height=140, clipChildren=True, padRight=4)
        self.tabgroup = uicontrols.TabGroup(parent=self.sr.main, align=uiconst.TOTOP)
        self.bottomCont = uiprimitives.Container(name='buttonParent', align=uiconst.TOBOTTOM, height=28, parent=self.sr.main, padding=(2, 0, 2, 2))
        GradientThemeColored(bgParent=self.bottomCont)
        self.warzonePanel = uiprimitives.Container(name='warzonePanel', parent=self.sr.main, padding=const.defaultPadding, state=uiconst.UI_HIDDEN)
        self.statisticsPanel = uiprimitives.Container(name='statisticsPanel', parent=self.sr.main, padding=const.defaultPadding, state=uiconst.UI_HIDDEN)
        self.rulesPanel = uiprimitives.Container(name='rulesPanel', parent=self.sr.main, padding=const.defaultPadding, state=uiconst.UI_HIDDEN)
        uthread.new(self.LoadTabPanels)
        return

    def LoadTabPanels(self):
        self.FetchData()
        self.ConstructWarzonePanel()
        self.ConstructBottomButtons()
        if session.warfactionid:
            self.ConstructExistingFWPlayerHeader()
        else:
            self.ConstructNewFWPlayerHeader()
        self.ConstructStatisticsPanel()
        self.ConstructRulesPanel()
        panelData = (util.KeyVal(name='frontPage', label=localization.GetByLabel('UI/FactionWarfare/WarzoneControl'), panel=self.warzonePanel), util.KeyVal(name='statistics', label=localization.GetByLabel('UI/FactionWarfare/Statistics'), panel=self.statisticsPanel), util.KeyVal(name='rules', label=localization.GetByLabel('UI/FactionWarfare/RulesOfEngagement'), panel=self.rulesPanel))
        self.tabgroup.LoadTabs(panelData, settingsID='FWWindowTabGroup')

    def OnSessionChanged(self, isRemote, session, change):
        if not self.destroyed:
            self.LoadTabPanels()

    def OnSystemStatusChanged(self):
        if not self.destroyed:
            self.LoadTabPanels()

    def OnJoinMilitia(self):
        if self and not self.destroyed:
            self.ConstructBottomButtons()

    def OnRankChange(self, oldrank, newrank):
        if not self.destroyed:
            self.LoadTabPanels()

    def FetchData(self):
        self.ShowLoad()
        fwSvc = sm.StartService('facwar')
        self.factionID = fwSvc.GetActiveFactionID()
        self.factionName = cfg.eveowners.Get(self.factionID).ownerName
        self.factionItem = cfg.eveowners.Get(self.factionID)
        self.militiaID = sm.StartService('facwar').GetFactionMilitiaCorporation(self.factionID)
        self.militiaItem = cfg.eveowners.Get(self.militiaID)
        self.militiaName = self.militiaItem.ownerName
        self.warZoneInfo = sm.GetService('facwar').GetFacWarZoneInfo(self.factionID)
        self.factionalWarStatus = sm.StartService('facwar').GetFactionalWarStatus()
        self.HideLoad()
        return True

    def OnEnlistMe(self, *args):
        sm.StartService('facwar').JoinFactionAsCharacter(self.factionID, session.warfactionid)

    def OnEnlistMyCorp(self, *args):
        sm.StartService('facwar').JoinFactionAsCorporation(self.factionID, session.warfactionid)

    def OnEnlistMyAlliance(self, *args):
        sm.StartService('facwar').JoinFactionAsAlliance(self.factionID, session.warfactionid)

    def ConstructWarzoneSignupPanel(self):
        textCont = uiprimitives.Container(name='text', parent=self.warzonePanel, align=uiconst.TOTOP, height=128, width=self.warzonePanel.width)
        enlistInfoLabel = 'UI/Generic/Unknown'
        if self.factionID == 500001:
            enlistInfoLabel = 'UI/FactionWarfare/EnlistInfoCaldari'
        elif self.factionID == 500002:
            enlistInfoLabel = 'UI/FactionWarfare/EnlistInfoMinmatar'
        elif self.factionID == 500003:
            enlistInfoLabel = 'UI/FactionWarfare/EnlistInfoAmarr'
        elif self.factionID == 500004:
            enlistInfoLabel = 'UI/FactionWarfare/EnlistInfoGallente'
        else:
            log.LogError('Unknown Faction.')
        text = uicontrols.EveLabelMedium(text=localization.GetByLabel(enlistInfoLabel), parent=textCont, left=8, top=8, width=textCont.width - 16, state=uiconst.UI_NORMAL)
        textCont.height = text.height + const.defaultPadding
        isSafe = sm.StartService('facwar').CheckForSafeSystem(eve.stationItem, self.factionID)
        warntxt = ''
        if not isSafe:
            if session.allianceid is not None:
                warntxt = localization.GetByLabel('UI/FactionWarfare/CantEnlistAllianceHereInfo')
            else:
                warntxt = localization.GetByLabel('UI/FactionWarfare/CantEnlistHereInfo')
        uiprimitives.Container(name='push', parent=self.warzonePanel, align=uiconst.TOTOP, height=8)
        uiprimitives.Container(name='push', parent=self.warzonePanel, align=uiconst.TOTOP, height=4)
        buttonCont = uiprimitives.Container(name='signupBtns', parent=self.warzonePanel, align=uiconst.TORIGHT, width=98)
        buttonCont.state = uiconst.UI_HIDDEN if not buttons else uiconst.UI_NORMAL
        textCont = uiprimitives.Container(name='text', parent=self.warzonePanel, align=uiconst.TOALL, pos=(2 * const.defaultPadding,
         const.defaultPadding,
         2 * const.defaultPadding,
         const.defaultPadding))
        warnTextCont = None
        if warntxt:
            warnTextCont = uiprimitives.Container(name='warntext', parent=textCont, align=uiconst.TOTOP, height=72)
            uiprimitives.Container(name='push', parent=textCont, align=uiconst.TOTOP, height=4)
            uicontrols.Frame(parent=warnTextCont, color=(1.0, 1.0, 1.0, 0.125))
            uiprimitives.Fill(parent=warnTextCont, color=(32 / 256.0,
             41 / 256.0,
             46 / 256.0,
             168 / 256.0))
            infoicon = uicontrols.Icon(parent=warnTextCont, icon='33_3', left=const.defaultPadding, top=const.defaultPadding, idx=0, width=64, height=64, state=uiconst.UI_DISABLED, ignoreSize=True)
            wrntext = uicontrols.EveHeaderSmall(text=warntxt, parent=warnTextCont, align=uiconst.TOALL, idx=0, top=8, left=72, width=6, state=uiconst.UI_NORMAL)
            warnTextCont.height = max(72, wrntext.textheight + 16)
        text = uicontrols.EveLabelMedium(text=infotxt, parent=textCont, align=uiconst.TOALL, state=uiconst.UI_NORMAL)
        return

    def ConstructWarzonePanel(self):
        self.warzonePanel.Flush()
        self.warzoneControl = uicls.FWWarzoneControl(parent=self.warzonePanel, align=uiconst.TOTOP, padding=(0, 10, 0, 10))
        bottomCont = uiprimitives.Container(parent=self.warzonePanel, align=uiconst.TOALL, height=0.3)
        systemStatsCont = uicontrols.DragResizeCont(name='systemStatsCont', settingsID='FWsystemStatsCont', parent=bottomCont, align=uiconst.TORIGHT_PROP, minSize=0.1, maxSize=0.5, defaultSize=0.45)
        mapCont = uiprimitives.Container(parent=bottomCont, align=uiconst.TOALL)
        uicontrols.GradientSprite(bgParent=mapCont, rotation=-pi / 2, rgbData=[(0, (0.3, 0.3, 0.3))], alphaData=[(0, 0.1), (0.9, 0.0)])
        self.bracketParent = uiprimitives.Container(name='bracketCont', parent=mapCont, clipChildren=True)
        from eve.client.script.ui.control.scenecontainer import SceneContainerBaseNavigation
        self.sceneContainerNav = SceneContainerBaseNavigation(parent=mapCont, state=uiconst.UI_NORMAL)
        from eve.client.script.ui.control.scenecontainer import SceneContainerBrackets
        self.sceneContainerNav.cursor = uiconst.UICURSOR_DRAGGABLE
        self.sceneContainer = SceneContainerBrackets(parent=mapCont, align=uiconst.TOALL)
        self.sceneContainerNav.Startup(self.sceneContainer)
        self.ConstructMap()
        self.systemsScroll = uicontrols.Scroll(name='systemsScroll', parent=systemStatsCont)
        self.systemsScroll.sr.id = 'FWSystemsScroll'
        self.UpdateSystemsScroll()

    def ConstructStatisticsPanel(self):
        self.statisticsPanel.Flush()
        scrolls = [('personal', localization.GetByLabel('UI/Generic/Personal')), ('corp', localization.GetByLabel('UI/Generic/Corporation')), ('militia', localization.GetByLabel('UI/FactionWarfare/Militia'))]
        if session.allianceid is not None:
            scrolls.append(('alliance', localization.GetByLabel('UI/Common/Alliance')))
        for key, text in scrolls:
            cont = uiprimitives.Container(parent=self.statisticsPanel, align=uiconst.TOTOP_PROP, height=1.0 / len(scrolls))
            uicontrols.Label(parent=cont, align=uiconst.TOTOP, text=text)
            self.infoScroll = uicontrols.Scroll(parent=cont, padBottom=5)
            self.LoadStatisticsScrollData(key)

        return

    def ConstructRulesPanel(self):
        self.rulesPanel.Flush()
        scrollCont = uicls.ScrollContainer(parent=self.rulesPanel)
        uicontrols.Label(parent=scrollCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/FactionWarfare/RulesOfEngagementText'), padding=4)

    def UpdateSystemsScroll(self):
        fwSvc = sm.GetService('facwar')
        foeID = facwarCommon.GetFactionMainEnemy(self.factionID)
        systemIDs = fwSvc.GetSolarSystemsOccupiedByFactions((self.factionID, foeID))
        scrolllist = []
        for systemID in systemIDs:
            data = util.KeyVal()
            numJumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(systemID)
            captureStatus = fwSvc.GetSystemCaptureStatusTxt(systemID)
            level = self.GetSystemLevelString(systemID)
            systemName = self.ColorTextBySide(cfg.evelocations.Get(systemID).name, systemID)
            data.label = '%s<t>%s<t>%s<t>%s' % (systemName,
             level,
             numJumps,
             captureStatus)
            data.itemID = systemID
            data.typeID = const.typeSolarSystem
            data.selectable = 0
            data.OnMouseEnter = self.OnSystemEntryMouseEnter
            data.OnMouseExit = self.OnSystemEntryMouseExit
            data.hint = self.GetSolarSystemHint(systemID, fwSvc.GetSystemCaptureStatus(systemID))
            scrolllist.append(listentry.Get('Generic', data=data))

        headers = (localization.GetByLabel('UI/FactionWarfare/System'),
         localization.GetByLabel('UI/FactionWarfare/Level'),
         localization.GetByLabel('UI/FactionWarfare/Jumps'),
         localization.GetByLabel('UI/FactionWarfare/Capture status'))
        self.systemsScroll.Load(contentList=scrolllist, headers=headers)
        return scrolllist

    def ShowRulesOfEngagementTab(self):
        self.tabgroup.ShowPanel(self.rulesPanel)

    def GetSystemUpgradeNumbers(self):
        ret = [0,
         0,
         0,
         0,
         0]
        for systemID in sm.GetService('facwar').GetSolarSystemsOccupiedByFactions([self.factionID]):
            level = self.GetSystemLevel(systemID)
            if level:
                ret[level - 1] += 1

        return ret

    def GetSystemLevel(self, systemID):
        return self.warZoneInfo.systemUpgradeLevel[systemID]

    def GetSystemLevelString(self, systemID):
        systemLevel = self.GetSystemLevel(systemID)
        if self.IsFriendSystem(systemID):
            if systemLevel:
                return util.IntToRoman(systemLevel)
            else:
                return ''
        else:
            return '-'

    def ColorTextBySide(self, text, systemID):
        if self.IsFriendSystem(systemID):
            color = util.Color.RGBtoHex(*facwarCommon.COLOR_FRIEND_BAR)
        else:
            color = util.Color.RGBtoHex(*facwarCommon.COLOR_FOE_BAR)
        return '<color=%s>%s</color>' % (color, text)

    def IsFriendSystem(self, systemID):
        friendSystems = sm.GetService('facwar').GetSolarSystemsOccupiedByFactions([self.factionID])
        return systemID in friendSystems

    def OnSystemEntryMouseEnter(self, entry):
        bracket = self.bracketsByID.get(entry.sr.node.itemID, None)
        if not bracket:
            return
        else:
            bracket.OnMouseEnter()
            return

    def OnSystemEntryMouseExit(self, entry):
        bracket = self.bracketsByID.get(entry.sr.node.itemID, None)
        if not bracket:
            return
        else:
            bracket.OnMouseExit()
            return

    def GetSystemScrollEntry(self, systemID):
        for node in self.systemsScroll.GetNodes():
            if node.itemID == systemID:
                return node

    def GetSolarSystemHint(self, systemID, captureStatus):
        hint = cfg.evelocations.Get(systemID).name
        level = self.GetSystemLevelString(systemID)
        if level and self.IsFriendSystem(systemID):
            hint = localization.GetByLabel('UI/FactionWarfare/SystemNameAndLevel', systemName=hint, level=level)
        hint += '<br>'
        if session.solarsystemid2 == systemID:
            hint += '<color=gray>' + localization.GetByLabel('UI/FactionWarfare/CurrentSolarSystem') + '</color>'
        else:
            jumps = sm.GetService('clientPathfinderService').GetJumpCountFromCurrent(systemID)
            hint += '<color=gray>' + localization.GetByLabel('UI/FactionWarfare/NumpJumpsAway', jumps=jumps) + '</color>'
        if captureStatus == facwarCommon.STATE_CONTESTED:
            percentage = '%2.1f' % sm.GetService('facwar').GetSystemContestedPercentage(systemID)
            hint += '<br>' + localization.GetByLabel('UI/FactionWarfare/StatusContestedHint', percentage=percentage)
        elif captureStatus == facwarCommon.STATE_VULNERABLE:
            hint += '<br>' + localization.GetByLabel('UI/FactionWarfare/StatusVulnerableHint')
        elif captureStatus == facwarCommon.STATE_CAPTURED:
            hint += '<br>' + localization.GetByLabel('UI/Neocom/SystemLost')
        return hint

    def ConstructMap(self):
        fwSvc = sm.StartService('facwar')
        foeID = facwarCommon.GetFactionMainEnemy(self.factionID)
        systems = fwSvc.GetSolarSystemsOccupiedByFactions((self.factionID, foeID))
        solarSystemIDs = systems.keys()
        translations = self.sceneContainer.GetTranslationsForSolarsystemIDs(solarSystemIDs)
        self.bracketsByID = {}
        for i, translation in enumerate(translations):
            systemID = solarSystemIDs[i]
            captureStatus = fwSvc.GetSystemCaptureStatus(systemID)
            bracket = uicls.FWMapBracket(parent=self.bracketParent, controller=self, width=8, height=8, curveSet=self.sceneContainer.bracketCurveSet, systemID=systemID, captureStatus=captureStatus, occupierID=systems[systemID], friendID=self.factionID, foeID=foeID)
            bracket.trackTransform = self.sceneContainer.CreateBracketTransform(translation)
            self.bracketsByID[systemID] = bracket

        if self.factionID in (const.factionAmarrEmpire, const.factionMinmatarRepublic):
            self.sceneContainer.SetOrbit(2.23, math.pi / 2 + 0.16)
            self.sceneContainerNav.SetMinMaxZoom(0.5, 12.0)
            self.sceneContainer.zoom = 0.82
        else:
            self.sceneContainer.SetOrbit(2.47, math.pi / 2 + 0.16)
            self.sceneContainerNav.SetMinMaxZoom(0.5, 15.0)
            self.sceneContainer.zoom = 0.93
        self.sceneContainer.AnimRotateFrom(yaw=-40.0, pitch=-40.0, zoom=10.0, duration=1.5)

    def OnMapBracketClicked(self, bracket):
        pass

    def OnMapBracketMouseEnter(self, bracket):
        node = self.GetSystemScrollEntry(bracket.systemID)
        if node.panel:
            node.panel.Select()

    def OnMapBracketMouseExit(self, bracket):
        node = self.GetSystemScrollEntry(bracket.systemID)
        if node.panel:
            node.panel.Deselect()

    def RetireAlliance(self, factionID, *args):
        ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/FactionWarfare/ConfirmRetireHeader'),
         'question': localization.GetByLabel('UI/FactionWarfare/ConfirmRetire', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            sm.StartService('facwar').LeaveFactionAsAlliance(factionID)
            self.ConstructBottomButtons()

    def RetireCorp(self, factionID, *args):
        ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/FactionWarfare/ConfirmRetireHeader'),
         'question': localization.GetByLabel('UI/FactionWarfare/ConfirmRetire', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            sm.StartService('facwar').LeaveFactionAsCorporation(factionID)
            self.ConstructBottomButtons()

    def Retire(self, *args):
        factionID = session.warfactionid
        ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/FactionWarfare/ConfirmRetireHeader'),
         'question': localization.GetByLabel('UI/FactionWarfare/ConfirmRetire', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            corp = sm.StartService('corp')
            corp.KickOut(session.charid, confirm=False)
            sm.StartService('objectCaching').InvalidateCachedMethodCall('corporationSvc', 'GetEmploymentRecord', session.charid)

    def CopyTable(self, *args):
        menu = [(localization.GetByLabel('UI/FactionWarfare/CopyTable'), self.CopyScroll, (self.infoScroll,))]
        return menu

    def CopyScroll(self, scroll, *args):
        t = ''
        if hasattr(scroll, 'sr') and hasattr(scroll.sr, 'headers'):
            for header in getattr(scroll.sr, 'headers', None):
                if header == '':
                    header = '-'
                t = t + '%s, ' % header

        for each in scroll.GetNodes():
            t = t + '\r\n%s' % each.label.replace('<t>', ',  ').replace('<b>', '').replace('</b>', '')

        blue.pyos.SetClipboardData(t)
        return

    def CancelApplication(self, factionID):
        ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/FactionWarfare/ConfirmCancelApplicationHeader'),
         'question': localization.GetByLabel('UI/FactionWarfare/ConfirmCancelApplicationAlliance', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            if session.allianceid:
                sm.StartService('facwar').WithdrawJoinFactionAsAlliance(factionID)
            else:
                sm.StartService('facwar').WithdrawJoinFactionAsCorporation(factionID)
            self.ConstructBottomButtons()

    def CancelRetirement(self, factionID):
        ret = eve.Message('CustomQuestion', {'header': localization.GetByLabel('UI/FactionWarfare/ConfirmCancelRetirementHeader'),
         'question': localization.GetByLabel('UI/FactionWarfare/ConfirmCancelRetirementHeader', factionName=cfg.eveowners.Get(factionID).name)}, uiconst.YESNO)
        if ret == uiconst.ID_YES:
            if session.allianceid:
                sm.StartService('facwar').WithdrawLeaveFactionAsAlliance(factionID)
            else:
                sm.StartService('facwar').WithdrawLeaveFactionAsCorporation(factionID)
            self.ConstructBottomButtons()

    def ConstructBottomButtons(self):
        fwSvc = sm.GetService('facwar')
        self.bottomCont.Flush()
        buttons = []
        self.factionalWarStatus = fwSvc.GetFactionalWarStatus()
        fwStatus = self.factionalWarStatus.status
        pendingFactionID = self.factionalWarStatus.factionID
        hasReqCorporationRole = session.corprole & const.corpRoleDirector == const.corpRoleDirector
        hasReqAllianceRole = hasReqCorporationRole and session.allianceid and sm.GetService('alliance').GetAlliance().executorCorpID == session.corpid
        notEnlisted = not session.warfactionid
        if notEnlisted:
            if fwStatus == const.facwarCorporationJoining and hasReqCorporationRole:
                buttons.append(('UI/FactionWarfare/WithdrawApplication',
                 self.CancelApplication,
                 pendingFactionID,
                 None))
            else:
                isInFWStation = fwSvc.CheckStationElegibleForMilitia()
                if isInFWStation:
                    disabledTxt = None
                else:
                    disabledTxt = 'UI/FactionWarfare/EnlistDisabledHint'
                buttons.append(('UI/FactionWarfare/EnlistMe',
                 self.OnEnlistMe,
                 (),
                 disabledTxt))
                if isInFWStation and hasReqCorporationRole:
                    disabledTxt = None
                else:
                    disabledTxt = 'UI/FactionWarfare/EnlistCorpDisabledHint'
                buttons.append(('UI/FactionWarfare/EnlistCorporation',
                 self.OnEnlistMyCorp,
                 (),
                 disabledTxt))
                if isInFWStation and hasReqAllianceRole:
                    disabledTxt = None
                else:
                    disabledTxt = 'UI/FactionWarfare/EnlistAllianceDisabledHint'
                buttons.append(('UI/FactionWarfare/EnlistAlliance',
                 self.OnEnlistMyAlliance,
                 (),
                 disabledTxt))
        elif util.IsNPC(session.corpid):
            if session.warfactionid:
                buttons.append(('UI/FactionWarfare/Retire',
                 self.Retire,
                 (),
                 None))
        elif hasReqCorporationRole:
            if fwStatus == const.facwarCorporationActive:
                if session.allianceid:
                    buttons.append(('UI/FactionWarfare/RetireAlliance',
                     self.RetireAlliance,
                     pendingFactionID,
                     None))
                else:
                    buttons.append(('UI/FactionWarfare/RetireCorporation',
                     self.RetireCorp,
                     pendingFactionID,
                     None))
            elif fwStatus == const.facwarCorporationLeaving:
                buttons.append(('UI/FactionWarfare/CancelRetirement',
                 self.CancelRetirement,
                 pendingFactionID,
                 None))
        if buttons:
            height = 54 if notEnlisted else 36
            buttonCont = uicontrols.ContainerAutoSize(parent=self.bottomCont, align=uiconst.CENTER, height=height, padding=8)
            self.bottomCont.height = height
            for label, func, args, disabledTxt in buttons:
                btn = uicontrols.Button(parent=buttonCont, align=uiconst.TOLEFT, func=func, args=args, label=localization.GetByLabel(label), padLeft=8)
                if disabledTxt:
                    btn.hint = localization.GetByLabel(disabledTxt)
                    btn.Disable()

        return

    def ConstructNewFWPlayerHeader(self):
        self.topCont.Flush()
        iconSize = 50
        firstLine = uiprimitives.Container(parent=self.topCont, align=uiconst.TOTOP_PROP, height=0.4, padLeft=20)
        uiprimitives.Sprite(parent=firstLine, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize), texturePath='res:/UI/Texture/Icons/FactionalWarfare_64.png')
        enemyID = facwarCommon.GetFactionMainEnemy(self.factionID)
        enemyAllyID = facwarCommon.GetFactionSecondaryEnemy(self.factionID)
        text = localization.GetByLabel('UI/FactionWarfare/NonFWPlayerHeader1', typeID=const.typeFaction, factionID=self.factionID, factionName=self.factionName, enemyID=enemyID, enemyName=cfg.eveowners.Get(enemyID).name, enemyAllyID=enemyAllyID, enemyAllyName=cfg.eveowners.Get(enemyAllyID).name)
        uicontrols.EveLabelLarge(parent=firstLine, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, left=iconSize + 20, text=text)
        secondLine = uiprimitives.Container(parent=self.topCont, align=uiconst.TOTOP_PROP, height=0.6, padLeft=20)
        uiprimitives.Sprite(parent=secondLine, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize), texturePath='res:/UI/Texture/WindowIcons/dogtags.png')
        enemyID = facwarCommon.GetFactionMainEnemy(self.factionID)
        labelCont = uicontrols.ContainerAutoSize(parent=secondLine, align=uiconst.CENTERLEFT, left=iconSize + 20)
        uicontrols.EveCaptionSmall(parent=labelCont, text=localization.GetByLabel('UI/FactionWarfare/FightForFaction', factionName=cfg.eveowners.Get(self.factionID).name))
        uicontrols.EveLabelMedium(state=uiconst.UI_NORMAL, parent=labelCont, top=25, text=localization.GetByLabel('UI/FactionWarfare/FightForFactionText', url='localsvc:service=facwar&method=ShowRulesOfEngagementTab'))

    def ConstructExistingFWPlayerHeader(self):
        self.topCont.Flush()
        iconSize = 50
        rightCont = uiprimitives.Container(name='rightCont', parent=self.topCont, align=uiconst.TORIGHT, width=200, padLeft=2)
        leftCont = uiprimitives.Container(name='leftCont', parent=self.topCont, clipChildren=True)
        firstLine = uiprimitives.Container(parent=leftCont, align=uiconst.TOTOP_PROP, height=0.4, padLeft=20)
        uiprimitives.Sprite(parent=firstLine, align=uiconst.CENTERLEFT, pos=(0,
         0,
         iconSize,
         iconSize), texturePath='res:/UI/Texture/Icons/FactionalWarfare_64.png')
        enemyID = facwarCommon.GetFactionMainEnemy(self.factionID)
        enemyAllyID = facwarCommon.GetFactionSecondaryEnemy(self.factionID)
        text = localization.GetByLabel('UI/FactionWarfare/FWPlayerHeader1', typeID=const.typeFaction, factionID=self.factionID, factionName=self.factionName, enemyID=enemyID, enemyName=cfg.eveowners.Get(enemyID).name, enemyAllyID=enemyAllyID, enemyAllyName=cfg.eveowners.Get(enemyAllyID).name)
        uicontrols.EveLabelLarge(parent=firstLine, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, left=iconSize + 20, text=text)
        secondLine = uiprimitives.Container(parent=leftCont, align=uiconst.TOTOP_PROP, height=0.6, padLeft=20)
        logo = uicls.LogoIcon(itemID=self.factionID, parent=secondLine, align=uiconst.CENTERLEFT, size=iconSize, ignoreSize=True)
        enemyID = facwarCommon.GetFactionMainEnemy(self.factionID)
        labelCont = uicontrols.ContainerAutoSize(parent=secondLine, align=uiconst.CENTERLEFT, left=iconSize + 20)
        rank, rankDesc = self.GetCurrentRank()
        timeServed = self.GetTimeServed()
        text = localization.GetByLabel('UI/FactionWarfare/FWPlayerHeader2', rank=rank, corp=cfg.eveowners.Get(session.corpid).name, faction=self.factionName, time=timeServed)
        uicontrols.EveLabelMedium(parent=labelCont, text=text, tabs=[100])
        firstLine = uiprimitives.Container(name='firstLine', parent=rightCont, align=uiconst.TOTOP, height=80)
        secondLine = uiprimitives.Container(name='secondLine', parent=rightCont, align=uiconst.TOTOP, height=40, top=3)
        totalPointsCont = uiprimitives.Container(parent=firstLine, pos=(0, 30, 55, 30), align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/FactionWarfare/WarzoneProgress', points=self.warZoneInfo.factionPoints, pointsTotal=int(self.warZoneInfo.maxWarZonePoints)))
        uicontrols.EveLabelSmall(parent=totalPointsCont, text=localization.GetByLabel('UI/FactionWarfare/Points'), align=uiconst.CENTERTOP, top=-15)
        uicontrols.Frame(bgParent=totalPointsCont, color=(0.392, 0.635, 0.212, 0.2))
        uicontrols.GradientSprite(bgParent=totalPointsCont, rotation=-pi / 2, rgbData=[(0, (0.239, 0.42, 0.235)), (1, (0.075, 0.157, 0.086))], alphaData=[(0, 1.0), (1, 0.9)])
        self.totalPointsLabel = uicontrols.EveCaptionMedium(parent=totalPointsCont, align=uiconst.CENTER, text=self.warZoneInfo.factionPoints)
        systemsCont = uiprimitives.Container(parent=firstLine, align=uiconst.TOPLEFT, pos=(65, 5, 50, 100), state=uiconst.UI_NORMAL, hint=localization.GetByLabel('UI/FactionWarfare/NumConqueredSystems'))
        uiprimitives.Sprite(parent=systemsCont, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/WindowIcons/systems.png')
        numSystems = len(sm.GetService('facwar').GetSolarSystemsOccupiedByFactions([self.factionID]))
        self.numSystemsLabel = uicontrols.EveHeaderLarge(parent=systemsCont, align=uiconst.CENTERTOP, top=30, text=numSystems)
        numUpgrades = self.GetSystemUpgradeNumbers()
        for i, num in enumerate(numUpgrades):
            if num:
                bgColor = util.Color.GetGrayRGBA(0.5, 0.5)
            else:
                bgColor = util.Color.GetGrayRGBA(0.2, 0.5)
            cont = uiprimitives.Container(parent=secondLine, bgColor=bgColor, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL, width=35, padTop=15, padRight=4, hint=localization.GetByLabel('UI/FactionWarfare/UpgradeLevelHint', level=util.IntToRoman(i + 1)))
            uicontrols.EveLabelMedium(parent=cont, align=uiconst.CENTERTOP, text=util.IntToRoman(i + 1), top=-20)
            uicontrols.EveHeaderLarge(parent=cont, align=uiconst.CENTER, text=num)

    def GetCurrentRank(self):
        currentRank = 1
        currRank = sm.StartService('facwar').GetCharacterRankInfo(session.charid)
        if currRank:
            currentRank = currRank.currentRank
        rankName, rankDescription = sm.GetService('facwar').GetRankLabel(self.factionID, currentRank)
        return (rankName, rankDescription)

    def GetTimeServed(self):
        try:
            timeInFW = blue.os.GetWallclockTime() - max(self.factionalWarStatus.startDate, sm.RemoteSvc('corporationSvc').GetEmploymentRecord(session.charid)[0].startDate)
            return util.FmtTimeInterval(timeInFW, 'day')
        except:
            return localization.GetByLabel('UI/Generic/Unknown')

    def LoadStatisticsScrollData(self, key):
        stats = self.GetStatisticsScrollData(key)
        scrolllist, header = self.GetStatisticsScrolllist(stats)
        self.infoScroll.Load(contentList=scrolllist, headers=header)

    def GetStatisticsScrolllist(self, stats, *args):
        caption = stats.get('label', '')
        header = stats.get('header', [])
        list = stats.get('data', [])
        scrolllist = []
        for each in list:
            data = util.KeyVal()
            data.label = each
            data.vspace = 0
            data.GetMenu = self.CopyTable
            data.selectable = 0
            scrolllist.append(listentry.Get('Generic', data=data))

        return (scrolllist, header)

    def GetStatisticsScrollData(self, key):
        stats = self.GetStatsData(key)
        if not stats:
            return
        statsHeader = stats.get('header')
        statsData = stats.get('data')
        data = [self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/KillsYesterday'), statsHeader, statsData.get('killsY')),
         self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/KillsLastWeek'), statsHeader, statsData.get('killsLW')),
         self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/KillsTotal'), statsHeader, statsData.get('killsTotal')),
         self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/VictoryPointsYesterday'), statsHeader, statsData.get('vpY')),
         self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/VictoryPointsLastWeek'), statsHeader, statsData.get('vpLW')),
         self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/VictoryPointsTotal'), statsHeader, statsData.get('vpTotal'))]
        factionInfo = sm.StartService('facwar').GetStats_FactionInfo()
        if key == 'militia':
            memberCount = self.ChangeFormat(factionInfo, 'totalMembersCount')
            sysControlled = self.ChangeFormat(factionInfo, 'systemsCount')
            data.insert(0, self.GetLine(localization.GetByLabel('UI/FactionWarfare/Pilots'), statsHeader, memberCount))
            data.append(self.GetLine(localization.GetByLabel('UI/FactionWarfare/Stats/SystemsControlled'), statsHeader, sysControlled))
        if key == 'corp':
            corpPilots = self.GetCorpPilots(factionInfo)
            data.insert(0, self.GetLine(localization.GetByLabel('UI/FactionWarfare/Pilots'), statsHeader, corpPilots))
        return {'label': self.GetStatsLabel(key),
         'configname': key,
         'header': self.GetStatsHeader(key, statsHeader),
         'data': data}

    def GetCorpPilots(self, factionInfo):
        pilots = {}
        if util.IsNPC(session.corpid):
            yourFactionInfo = factionInfo.get(session.warfactionid, None)
            pilots['your'] = getattr(yourFactionInfo, 'militiaMembersCount', 0)
        else:
            reg = moniker.GetCorpRegistry()
            pilots['your'] = reg.GetCorporation().memberCount
        topFWCorp = 0
        topCorps = self.ChangeFormat(factionInfo, 'topMemberCount')
        for each in topCorps.itervalues():
            if topFWCorp < each:
                topFWCorp = each

        pilots['top'] = topFWCorp
        allMembers = 0
        members = self.ChangeFormat(factionInfo, 'totalMembersCount')
        for each in members.itervalues():
            allMembers += each

        pilots['all'] = allMembers
        return pilots

    def ChangeFormat(self, data, attributeName):
        temp = {}
        for key, value in data.iteritems():
            temp[key] = getattr(value, attributeName, 0)

        return temp

    def GetStatsData(self, what):
        if what == 'militia':
            return sm.StartService('facwar').GetStats_Militia()
        elif what == 'personal':
            return sm.StartService('facwar').GetStats_Personal()
        elif what == 'corp':
            return sm.StartService('facwar').GetStats_Corp(session.corpid)
        elif what == 'alliance':
            return sm.StartService('facwar').GetStats_Alliance(session.allianceid)
        else:
            return None

    def GetStatsLabel(self, what):
        if what == 'militia':
            return localization.GetByLabel('UI/FactionWarfare/Militia')
        if what == 'personal':
            return localization.GetByLabel('UI/Generic/Personal')
        if what == 'corp':
            return localization.GetByLabel('UI/Generic/Corporation')
        if what == 'alliance':
            return localization.GetByLabel('UI/Common/Alliance')

    def GetStatsHeader(self, what, header):
        if what in ('personal', 'corp', 'alliance'):
            return self.GetPersonalCorpHeader(header)
        if what == 'militia':
            return self.GetMilitiaHeader(header, short=1)
        return []

    def GetLine(self, text, header, data):
        temp = '%s<t>' % text
        for each in header:
            temp = '%s%s<t>' % (temp, util.FmtAmt(data.get(each, 0), fmt='sn'))

        temp = temp[:-3]
        return temp

    def GetMilitiaHeader(self, header, short=0):
        temp = [localization.GetByLabel('UI/Generic/Statistics')]
        for each in header:
            if short:
                try:
                    raceID = {const.factionAmarrEmpire: const.raceAmarr,
                     const.factionCaldariState: const.raceCaldari,
                     const.factionGallenteFederation: const.raceGallente,
                     const.factionMinmatarRepublic: const.raceMinmatar}[each]
                    name = cfg.races.Get(raceID).raceName
                except KeyError:
                    name = cfg.eveowners.Get(each).name

            else:
                name = cfg.eveowners.Get(each).name
            temp.append(name)

        return temp

    def GetPersonalCorpHeader(self, header):
        translation = {'you': localization.GetByLabel('UI/FactionWarfare/You'),
         'your': localization.GetByLabel('UI/FactionWarfare/Your'),
         'top': localization.GetByLabel('UI/FactionWarfare/Top'),
         'all': localization.GetByLabel('UI/FactionWarfare/All')}
        temp = [localization.GetByLabel('UI/Generic/Statistics')]
        for each in header:
            name = translation.get(each, '')
            temp.append(name)

        return temp


class FWMapBracket(uiprimitives.Bracket):
    __guid__ = 'uicls.FWMapBracket'
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        uiprimitives.Bracket.ApplyAttributes(self, attributes)
        self.captureStatus = attributes.get('captureStatus', facwarCommon.STATE_STABLE)
        self.isCurrLocation = attributes.get('isCurrLocation', False)
        self.controller = attributes.controller
        self.systemID = attributes.systemID
        self.occupierID = attributes.occupierID
        self.friendID = attributes.friendID
        self.foeID = attributes.foeID
        if self.occupierID == self.friendID:
            self.color = facwarCommon.COLOR_FRIEND_BAR
            self.hoverColor = facwarCommon.COLOR_FRIEND_LIGHT
        else:
            self.color = facwarCommon.COLOR_FOE_BAR
            self.hoverColor = facwarCommon.COLOR_FOE_LIGHT
        self.dotSprite = uiprimitives.Sprite(parent=self, texturePath='res:/Texture/Particle/MapSprite.dds', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.color)
        self.bgSprite = uiprimitives.Sprite(parent=self, texturePath='res:/Texture/Particle/MapSprite.dds', align=uiconst.TOALL, state=uiconst.UI_DISABLED, color=self.hoverColor, padding=-10, opacity=0.0)
        if self.systemID == session.solarsystemid2:
            frame = uiprimitives.Sprite(parent=self, name='frame', pos=(0, 0, 20, 20), align=uiconst.CENTER, state=uiconst.UI_DISABLED, opacity=0.3, texturePath='res:/UI/Texture/classes/StarMapSvc/currentLocation.png')
            uicontrols.Label(parent=self, align=uiconst.CENTERLEFT, left=18, fontsize=10, text=localization.GetByLabel('UI/FactionWarfare/YouAreHere'), opacity=0.5)
        self.animCont = uiprimitives.Container(parent=self, state=uiconst.UI_DISABLED)
        uthread.new(self.SetSystemCaptureStatus, self.captureStatus)

    def SetSystemCaptureStatus(self, captureStatus):
        fwSvc = sm.GetService('facwar')
        self.captureStatus = captureStatus
        self.animCont.Flush()
        size = 32
        if captureStatus == facwarCommon.STATE_STABLE:
            pass
        elif captureStatus == facwarCommon.STATE_CONTESTED:
            ripple = uiprimitives.Sprite(parent=self.animCont, align=uiconst.CENTER, pos=(0, 0, 32, 32), texturePath='res:/UI/Texture/classes/FWWindow/ripple1.png', color=util.Color.WHITE)
            uicore.animations.FadeTo(ripple, 0.1, 0.5, duration=3.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
        elif captureStatus == facwarCommon.STATE_VULNERABLE:
            for texturePath in ('res:/UI/Texture/classes/FWWindow/ripple1.png', 'res:/UI/Texture/classes/FWWindow/ripple2.png', 'res:/UI/Texture/classes/FWWindow/ripple3.png'):
                ripple = uiprimitives.Sprite(parent=self.animCont, align=uiconst.CENTER, pos=(0,
                 0,
                 size,
                 size), texturePath=texturePath, color=self.color)
                uicore.animations.FadeTo(ripple, 0.1, 0.8, duration=3.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)
                blue.synchro.SleepWallclock(1000)

        elif captureStatus == facwarCommon.STATE_CAPTURED:
            wasMine = self.systemID in fwSvc.GetSolarSystemsOccupiedByFactions([fwSvc.GetActiveFactionID()])
            if wasMine:
                fromColor = facwarCommon.COLOR_FRIEND_BAR
                toColor = facwarCommon.COLOR_FOE_BAR
            else:
                fromColor = facwarCommon.COLOR_FOE_BAR
                toColor = facwarCommon.COLOR_FRIEND_BAR
            uicore.animations.SpColorMorphTo(self.dotSprite, fromColor, toColor, duration=2.0, curveType=uiconst.ANIM_SMOOTH, loops=uiconst.ANIM_REPEAT)

    def GetHint(self):
        return self.controller.GetSolarSystemHint(self.systemID, self.captureStatus)

    def OnMouseEnter(self, *args):
        uicore.animations.FadeIn(self.bgSprite, endVal=0.3, duration=0.3)
        self.controller.OnMapBracketMouseEnter(self)

    def OnMouseExit(self, *args):
        self.controller.OnMapBracketMouseExit(self)
        uicore.animations.FadeOut(self.bgSprite, duration=0.3)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFormItemIDTypeID(self.systemID, const.typeSolarSystem)

    def OnClick(self, *args):
        self.controller.OnMapBracketClicked(self)