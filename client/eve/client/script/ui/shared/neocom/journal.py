# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\neocom\journal.py
import service
import uiprimitives
import uicontrols
import uix
import uiutil
import form
import util
import blue
import uthread
import listentry
import base
import carbonui.const as uiconst
import geo2
import log
import logConst
from contractutils import GetColoredContractStatusText, ConFmtDate, GetContractTitle
from incursion import IncursionTab
from operator import attrgetter
import localization
import telemetry
import evetypes
from inventorycommon.const import ownerAmarrNavy
from eve.common.lib.appConst import factionDrifters
from eve.common.script.sys.rowset import IndexRowset
from eve.client.script.ui.control.divider import Divider
from evePathfinder.core import IsUnreachableJumpCount
MAX_COL_LENGTH = 60

class ReportSortBy():
    Constellation, LP, Jumps, Influence, StagingSolarSystem, Security = range(6)


REPORT_SORT_PARAMETERS = (('constellationName', False),
 ('loyaltyPoints', True),
 ('jumps', False),
 ('influence', True),
 ('stagingSolarSystemName', False),
 ('security', True))
REWARD_SCOUT = 8
REWARD_VANGUARD = 1
REWARD_ASSAULT = 2
REWARD_HQ = 3
REWARD_BOSS = 10
REWARD_THRONE_WORLDS_LIGHT = 15
REWARD_THRONE_WORLDS_MEDIUM = 16
REWARD_THRONE_WORLDS_HEAVY = 17
INCURSION_DUNGEONS = {'scout': (util.KeyVal(severity='scout', index=1, rewardID=REWARD_SCOUT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/OneText'),
           util.KeyVal(severity='scout', index=2, rewardID=REWARD_SCOUT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/TwoText'),
           util.KeyVal(severity='scout', index=3, rewardID=REWARD_SCOUT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/ThreeText'),
           util.KeyVal(severity='scout', index=4, rewardID=REWARD_SCOUT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/Four', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Scout/FourText')),
 'vanguard': (util.KeyVal(severity='vanguard', index=1, rewardID=REWARD_VANGUARD, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/OneText'), util.KeyVal(severity='vanguard', index=2, rewardID=REWARD_VANGUARD, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/TwoText'), util.KeyVal(severity='vanguard', index=3, rewardID=REWARD_VANGUARD, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Vanguard/ThreeText')),
 'assault': (util.KeyVal(severity='assault', index=1, rewardID=REWARD_ASSAULT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/OneText'), util.KeyVal(severity='assault', index=2, rewardID=REWARD_ASSAULT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/TwoText'), util.KeyVal(severity='assault', index=3, rewardID=REWARD_ASSAULT, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/Assault/ThreeText')),
 'hq': (util.KeyVal(severity='hq', index=1, rewardID=REWARD_HQ, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/One', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/OneText'),
        util.KeyVal(severity='hq', index=2, rewardID=REWARD_HQ, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Two', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/TwoText'),
        util.KeyVal(severity='hq', index=3, rewardID=REWARD_HQ, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Three', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/ThreeText'),
        util.KeyVal(severity='hq', index=4, rewardID=REWARD_BOSS, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Four', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/FourText'),
        util.KeyVal(severity='hq', index=5, rewardID=REWARD_BOSS, name='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/Five', text='UI/Incursion/Distributions/SanshaIncursion/Encounters/HQ/FiveText')),
 'amarr': (util.KeyVal(severity='defensiveOutpost', index=1, rewardID=REWARD_THRONE_WORLDS_LIGHT, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrDefensiveOutpost', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrDefensiveOutpostText'), util.KeyVal(severity='encampment', index=2, rewardID=REWARD_THRONE_WORLDS_MEDIUM, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrEncampment', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrEncampmentText'), util.KeyVal(severity='battalion', index=3, rewardID=REWARD_THRONE_WORLDS_HEAVY, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrBattalion', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Amarr/AmarrBattalionText')),
 'drifters': (util.KeyVal(severity='moderateInflux', index=1, rewardID=REWARD_THRONE_WORLDS_LIGHT, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/ModerateDrifterInflux', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/ModerateDrifterInfluxText'), util.KeyVal(severity='severeInflux', index=2, rewardID=REWARD_THRONE_WORLDS_MEDIUM, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/SevereDrifterInflux', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/SevereDrifterInfluxText'), util.KeyVal(severity='criticalInflux', index=3, rewardID=REWARD_THRONE_WORLDS_HEAVY, name='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/CriticalDrifterInflux', text='UI/Incursion/Distributions/DefenseOfTheThroneWorlds/Encounters/Drifters/CriticalDrifterInfluxText'))}
ENGLISH_MISSIONS_SETTING = 'AgentMissionsInEnglish'

class LPTypeFilter():
    LPLost = -1
    LPPayedOut = -2


class JournalSvc(service.Service):
    __exportedcalls__ = {'Refresh': [],
     'GetMyAgentJournalDetails': [],
     'ShowContracts': [],
     'ShowIncursionTab': [service.ROLE_IGB]}
    __update_on_reload__ = 0
    __guid__ = 'svc.journal'
    __notifyevents__ = ['ProcessSessionChange',
     'OnAgentMissionChange',
     'OnEscalatingPathMessage',
     'OnFleetEscalatingPathMessage',
     'OnLPStoreAcceptOffer',
     'OnLPChange',
     'OnPILaunchesChange',
     'OnEpicJournalChange',
     'ProcessUIRefresh']
    __servicename__ = 'journal'
    __displayname__ = 'Journal Client Service'
    __dependencies__ = ['window', 'settings']

    def Run(self, memStream=None):
        log.LogInfo('Starting Journal')
        self.Reset()
        self.outdatedAgentJournals = []
        self.outdatedCorpLP = True
        self.lpMapping = []
        self.pathPlexPositionByInstanceID = {}

    def Stop(self, memStream=None):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.Close()
        return

    def ProcessSessionChange(self, isremote, session, change):
        if eve.session.charid is None:
            self.Stop()
            self.Reset()
        if 'locationid' in change:
            self.pathPlexPositionByInstanceID = {}
        return

    def ProcessUIRefresh(self):
        self.Reset()

    @telemetry.ZONE_METHOD
    def OnAgentMissionChange(self, what, agentID, tutorialID=None):
        if agentID is None:
            self.agentjournal = None
        elif agentID not in self.outdatedAgentJournals:
            self.outdatedAgentJournals.append(agentID)
        sm.GetService('addressbook').RefreshWindow()
        wnd = self.GetWnd()
        if (not wnd or wnd.destroyed) and what not in (const.agentMissionDeclined,
         const.agentMissionCompleted,
         const.agentMissionQuit,
         const.agentMissionOfferAccepted,
         const.agentMissionOfferDeclined,
         const.agentMissionDungeonMoved):
            sm.GetService('neocom').Blink(form.Journal.default_windowID)
        sm.ScatterEvent('OnAgentMissionChanged', what, agentID, tutorialID=tutorialID)
        return

    def OnLPChange(self, what):
        self.outdatedCorpLP = True
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            sm.GetService('neocom').Blink(form.Journal.default_windowID)

    def OnEscalatingPathMessage(self, instanceID):
        exp1 = self.GetExpeditions()
        exp2 = IndexRowset(exp1.header, exp1.lines, 'instanceID')
        if instanceID not in exp2:
            exp1 = self.GetExpeditions(1)
            exp2 = IndexRowset(exp1.header, exp1.lines, 'instanceID')
        if instanceID in exp2:
            data = util.KeyVal()
            data.rec = exp2[instanceID]
            self.PopupDungeonDescription(data)
        else:
            log.LogInfo("Someone tried loading a message that isn't there")

    def OnFleetEscalatingPathMessage(self, charID, pathStep):
        if charID != eve.session.charid:
            if cfg.eveowners.GetIfExists(charID) is not None:
                dungeonName = localization.GetByLabel('UI/Journal/JournalWindow/Dungeons/DungeonName', character=charID)
            else:
                dungeonName = localization.GetByLabel('UI/Journal/JournalWindow/Dungeons/DungeonNameUnknown')
            journalEntry = localization.GetByMessageID(pathStep.journalEntryTemplateID)
            data = util.KeyVal()
            data.instanceID = 0
            data.dungeonName = dungeonName
            data.pathEntry = localization.GetByLabel('UI/Journal/JournalWindow/Dungeons/UpdatedJournalEntry', character=charID, journalEntry=journalEntry)
            data.fakerec = True
            data.rec = data
            self.PopupDungeonDescription(data)
        return

    def OnLPStoreAcceptOffer(self):
        self.outdatedCorpLP = True
        wnd = self.GetWnd()
        if wnd:
            wnd.sr.maintabs.ReloadVisible()

    def OnEpicJournalChange(self):
        wnd = self.GetWnd()
        if not wnd or wnd.destroyed:
            sm.GetService('neocom').Blink(form.Journal.default_windowID)

    def Reset(self):
        self.agentjournal = None
        self.semaphore = uthread.Semaphore()
        self.notext = None
        self.expeditionRowset = None
        self.launchsRowSet = None
        self.lpMapping = []
        self.outdatedCorpLP = True
        return

    def Refresh(self):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.sr.maintabs.ReloadVisible()
        return

    def GetWnd(self, new=0, skipAutoSelect=False):
        if new:
            wnd = form.Journal.Open(skipAutoSelect=skipAutoSelect)
        else:
            wnd = form.Journal.GetIfOpen()
        return wnd

    def ShowContracts(self, *args):
        wnd = self.GetWnd()
        if wnd is not None and not wnd.destroyed:
            wnd.ShowContracts(*args)
        return

    def ShowIncursionTab(self, flag=None, constellationID=None, taleID=None, open=False):
        wnd = self.GetWnd(new=open, skipAutoSelect=True)
        if wnd is not None and not wnd.destroyed:
            blue.pyos.synchro.Yield()
            wnd.ShowIncursionTab(flag, constellationID, taleID)
        return

    def GetLaunches(self, force=0):
        if self.launchsRowSet is None or force:
            self.launchsRowSet = sm.RemoteSvc('planetMgr').GetMyLaunchesDetails()
        return self.launchsRowSet

    def OnPILaunchesChange(self, *args):
        self.launchsRowSet = None
        sm.GetService('neocom').Blink(form.Journal.default_windowID)
        return

    def GetExpeditions(self, force=0):
        if self.expeditionRowset and not force:
            return self.expeditionRowset
        if not self.expeditionRowset or force:
            self.expeditionRowset = sm.RemoteSvc('dungeonExplorationMgr').GetMyEscalatingPathDetails()
        return self.expeditionRowset

    def PopupDungeonDescription(self, node):
        if node.get('fakerec', None):
            did = node.instanceID
            dname = node.dungeonName
            djentry = node.pathEntry
        else:
            if node.rec:
                dungeonDstData = node.rec.destDungeon
                dungeonSrcData = node.rec.srcDungeon
                dungeonInstanceID = node.rec.dungeon.instanceID
                dungeonPath = node.rec.pathStep
            else:
                dungeonDstData = node.destDungeon
                dungeonSrcData = node.srcDungeon
                dungeonInstanceID = node.dungeon.instanceID
                dungeonPath = node.pathStep
            did = dungeonInstanceID
            if dungeonDstData is not None:
                dname = localization.GetByMessageID(dungeonDstData.dungeonNameID)
            elif dungeonSrcData is not None:
                dname = localization.GetByMessageID(dungeonSrcData.dungeonNameID)
            else:
                log.LogError('No dungeon data to get dungeon name from. id:', did)
                return
            djentry = localization.GetByMessageID(dungeonPath.journalEntryTemplateID)
        data = util.KeyVal()
        data.rec = node
        data.header = dname
        data.icon = '40_14'
        data.text = djentry
        data.caption = localization.GetByLabel('UI/Common/Expeditions')
        data.hasDungeonWarp = True
        data.instanceID = did
        wnd = sm.GetService('transmission').OnIncomingTransmission(data)
        return

    def GetMyAgentJournalDetails(self):
        s = getattr(self, 'semaphore', None)
        if s is not None:
            s.acquire()
        try:
            if getattr(self, 'agentjournal', None) is None:
                self.agentjournal = sm.RemoteSvc('agentMgr').GetMyJournalDetails()
                for mission in self.agentjournal[0]:
                    for b in mission[6]:
                        if getattr(b, 'originalHint', None) is None:
                            b.originalHint = b.hint
                        b.hint = localization.GetByLabel(b.originalHint, location=b.locationID, index=b.locationNumber + 1)

            elif self.outdatedAgentJournals:
                parallelCalls = []
                tmp = self.outdatedAgentJournals
                for agentID in self.outdatedAgentJournals:
                    parallelCalls.append((sm.GetService('agents').GetAgentMoniker(agentID).GetMyJournalDetails, ()))

                self.outdatedAgentJournals = []
                parallelResults = uthread.parallel(parallelCalls)
                self.i = parallelResults
                if self.agentjournal is None:
                    self.agentjournal = sm.RemoteSvc('agentMgr').GetMyJournalDetails()
                else:
                    for agentID in tmp:
                        for mission in self.agentjournal[0]:
                            if mission[4] == agentID:
                                self.agentjournal[0].remove(mission)
                                break

                        for research in self.agentjournal[1]:
                            if research[0] == agentID:
                                self.agentjournal[1].remove(research)
                                break

                    for i in range(len(parallelResults)):
                        for mission in parallelResults[i][0]:
                            for b in mission[6]:
                                if getattr(b, 'originalHint', None) is None:
                                    b.originalHint = b.hint
                                b.hint = localization.GetByLabel(b.originalHint, location=b.locationID, index=b.locationNumber + 1)

                        agentID = tmp[i]
                        for n in range(2):
                            self.agentjournal[n].extend(parallelResults[i][n])

        finally:
            if s is not None:
                s.release()

        return self.agentjournal

    def GetMyAgentJournalBookmarks(self):
        ret = []
        missions = self.GetMyAgentJournalDetails()[0]
        if len(missions):
            i = 0
            for i in range(len(missions)):
                missionState, importantMission, missionType, missionName, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable, contentID = missions[i]
                ret.append((missionName, bookmarks, agentID))

        return ret

    def GetMyLoyaltyPoints(self):
        if self.outdatedCorpLP == True:
            loyaltyPoints = sm.RemoteSvc('LPSvc').GetLPsForCharacter()
            self.lpMapping = []
            for row in loyaltyPoints:
                self.lpMapping.append((row[0], row[1]))

            self.outdatedCorpLP = False
        return self.lpMapping

    def CheckUndock(self, stationID):
        missions = self.GetMyAgentJournalDetails()[0]
        if len(missions):
            for i in range(len(missions)):
                missionState, importantMission, missionType, missionNameID, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable, contentID = missions[i]
                if missionState == const.agentMissionStateAccepted:
                    for b in bookmarks:
                        if b.itemID == stationID and b.locationType == 'objective.source':
                            if not sm.GetService('agents').CheckCourierCargo(agentID, b.itemID, contentID):
                                missionName = sm.GetService('agents').ProcessMessage((missionNameID, contentID), agentID)
                                return uicore.Message('CourierUndockMissingCargo', {'missionName': missionName}, uiconst.YESNO) == uiconst.ID_YES

        return True


class EscalatingPathLocationEntry(listentry.Generic):
    __guid__ = 'listentry.EscalatingPathLocationEntry'
    OnSelectCallback = None

    def Load(self, node):
        self.sr.node = node
        self.sr.label.text = node.label
        self.OnSelectCallback = node.Get('callback', None)
        if node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.state = uiconst.UI_NORMAL
        self.sr.label.Update()
        return

    def OpenDetails(self):
        sm.GetService('journal').PopupDungeonDescription(self.sr.node)

    def OnDblClick(self, *args):
        self.OpenDetails()

    def GetMenu(self):
        node = self.sr.node
        m = []
        expired = node.rec.expiryTime < blue.os.GetWallclockTime()
        if not expired:
            if node.rec.dungeon.solarSystemID is not None:
                m += sm.GetService('menu').CelestialMenu(node.rec.dungeon.solarSystemID)
                m.append(None)
                m.append((uiutil.MenuLabel('UI/Commands/OpenDescription'), self.OpenDetails))
            if node.rec.dungeon.solarSystemID == eve.session.solarsystemid:
                journal = sm.GetService('journal')
                if node.rec.instanceID in journal.pathPlexPositionByInstanceID:
                    log.LogInfo('Using cached path instance position')
                    resp = journal.pathPlexPositionByInstanceID[node.rec.instanceID]
                else:
                    resp = sm.RemoteSvc('keeper').CanWarpToPathPlex(node.rec.instanceID)
                if resp:
                    if resp is True:
                        m.append((uiutil.MenuLabel('UI/Inflight/WarpToBookmark'), self.WarpToHiddenDungeon, (node.id, node)))
                    else:
                        mickey = sm.StartService('michelle')
                        me = mickey.GetBall(eve.session.shipid)
                        dist = geo2.Vec3DistanceD(resp, (me.x, me.y, me.z))
                        if dist < const.minWarpDistance:
                            journal.pathPlexPositionByInstanceID[node.rec.instanceID] = resp
                            m.append((uiutil.MenuLabel('UI/Inflight/ApproachLocation'), self.Approach, list(resp)))
                        else:
                            m.append((uiutil.MenuLabel('UI/Inflight/WarpToBookmark'), self.WarpToHiddenDungeon, (node.id, node)))
        else:
            m.append(None)
            m.append((uiutil.MenuLabel('UI/Commands/Remove'), self.DeleteExpeditionEntry, (node.id, node)))
        return m

    def Approach(self, x, y, z):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.CmdGotoDirection(x, y, z)
            sm.GetService('menu').ClearAlignTargets()
        return

    def DeleteExpeditionEntry(self, instanceID, *args):
        rm = []
        for entry in self.sr.node.scroll.GetNodes():
            if entry.id == instanceID:
                rm.append(entry)

        if rm:
            self.sr.node.scroll.RemoveEntries(rm)
        uthread.new(sm.RemoteSvc('dungeonExplorationMgr').DeleteExpiredPathStep, instanceID)
        uthread.new(sm.GetService('journal').GetExpeditions, force=1)

    def WarpToHiddenDungeon(self, instanceID, node, *args):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.CmdWarpToStuff('epinstance', instanceID)
        return


class PlanetaryInteractionLaunchEntry(listentry.Generic):
    __guid__ = 'listentry.PlanetaryInteractionLaunchEntry'
    OnSelectCallback = None

    def Load(self, node):
        listentry.Generic.Load(self, node)
        self.sr.node = node
        self.sr.label.text = node.label
        self.OnSelectCallback = node.Get('callback', None)
        if node.Get('selected', 0):
            self.Select()
        else:
            self.Deselect()
        self.state = uiconst.UI_NORMAL
        self.sr.label.Update()
        return

    def GetMenu(self):
        node = self.sr.node
        m = []
        if not node.expired:
            if node.rec.solarSystemID is not None:
                m += sm.GetService('menu').CelestialMenu(node.rec.solarSystemID, filterFunc=[uiutil.MenuLabel('UI/Inflight/BookmarkLocation')])
                m.append(None)
            if node.rec.solarSystemID == eve.session.solarsystemid:
                mickey = sm.StartService('michelle')
                me = mickey.GetBall(eve.session.shipid)
                dist = geo2.Vec3DistanceD((node.rec.x, node.rec.y, node.rec.z), (me.x, me.y, me.z))
                if dist < const.minWarpDistance:
                    m.append((uiutil.MenuLabel('UI/Inflight/ApproachLocation'), self.Approach, list((node.rec.itemID, node))))
                else:
                    m.append((uiutil.MenuLabel('UI/Inflight/WarpToBookmark'), self.WarpToLaunchPickup, (node.rec.launchID, node)))
        else:
            m.append(None)
            m.append((uiutil.MenuLabel('UI/Commands/Remove'), self.DeleteLaunchEntry, (node.rec.launchID, node)))
        return m

    def Approach(self, launchID, node):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.CmdFollowBall(launchID, 50)
        return

    def WarpToLaunchPickup(self, launchID, node, *args):
        bp = sm.StartService('michelle').GetRemotePark()
        if bp is not None:
            bp.CmdWarpToStuff('launch', launchID)
        return

    def DeleteLaunchEntry(self, launchID, *args):
        rm = []
        for entry in self.sr.node.scroll.GetNodes():
            if entry.id == launchID:
                rm.append(entry)

        if rm:
            self.sr.node.scroll.RemoveEntries(rm)
        uthread.new(sm.RemoteSvc('planetMgr').DeleteLaunch, launchID)
        uthread.new(sm.GetService('journal').GetLaunches, force=1)


class JournalWindow(uicontrols.Window):
    __guid__ = 'form.Journal'
    __notifyevents__ = ['OnEpicJournalChange',
     'OnEscalatingPathChange',
     'OnEscalatingPathMessage',
     'OnPILaunchesChange',
     'ProcessSessionChange',
     'OnAgentMissionChange',
     'OnLPChange',
     'OnDeleteContract']
    default_width = 525
    default_height = 300
    default_minSize = (465, 300)
    default_windowID = 'journal'
    default_captionLabelPath = 'UI/Journal/JournalWindow/Caption'
    default_descriptionLabelPath = 'Tooltips/Neocom/Journal_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/journal.png'
    default_topParentHeight = 0
    default_scrollPanelPadding = 10

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        self.entry = None
        self.selectedArc = None
        self.curEpicArcId = None
        self.epicJournalData = None
        self.showingIncursionTab = False
        self.incursionLPLogData = None
        self.contractFilters = {}
        skipAutoSelect = attributes.Get('skipAutoSelect', False)
        self.SetScope('station_inflight')
        self.clientPathfinderService = sm.GetService('clientPathfinderService')
        self.sr.agenttabs = uicontrols.TabGroup(name='agenttabs', parent=self.sr.main)
        self.sr.incursiontabs = uicontrols.TabGroup(name='incursiontabs', parent=self.sr.main)
        width = settings.char.ui.Get('journalIncursionEncounterScrollWidth', 100)
        self.sr.incursionEncounterScroll = uicontrols.Scroll(parent=self.sr.main, name='encounterScroll', align=uiconst.TOLEFT, width=width, state=uiconst.UI_HIDDEN)
        self.LoadIncursionDistributions()
        divider = Divider(name='incursionEncountersDivider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.main, state=uiconst.UI_HIDDEN)
        dividerMin = 100
        dividerMax = self.sr.incursionEncounterScroll.GetMaxTextWidth(200) + self.default_scrollPanelPadding
        divider.Startup(self.sr.incursionEncounterScroll, 'width', 'x', dividerMin, dividerMax)
        divider.OnSizeChanged = self.OnIncursionEncounterResize
        self.sr.incursionEncounterDivider = divider
        self.sr.incursionReportFilter = uiprimitives.Container(name='incursionGlobalReportFilter', parent=self.sr.main, align=uiconst.TOTOP, height=36, state=uiconst.UI_HIDDEN)
        options = ((localization.GetByLabel('UI/Common/Constellation'), ReportSortBy.Constellation),
         (localization.GetByLabel('UI/Incursion/Journal/StagingSystem'), ReportSortBy.StagingSolarSystem),
         (localization.GetByLabel('UI/Common/Jumps'), ReportSortBy.Jumps),
         (localization.GetByLabel('UI/Common/Security'), ReportSortBy.Security),
         (localization.GetByLabel('UI/LPStore/LP'), ReportSortBy.LP),
         (localization.GetByLabel('UI/Incursion/Common/HUDInfluenceTitle'), ReportSortBy.Influence))
        self.sr.incursionReportSortCombo = uicontrols.Combo(label=localization.GetByLabel('UI/Common/SortBy'), parent=self.sr.incursionReportFilter, options=options, name='reportSortByCombo', callback=self.OnReportSortByComboChange, align=uiconst.TOLEFT, width=200, select=settings.char.ui.Get('journalIncursionReportSort', ReportSortBy.Constellation), padding=(const.defaultPadding,
         18,
         0,
         0))
        refreshBtn = uix.GetBigButton(24, self.sr.incursionReportFilter, top=12, left=4)
        refreshBtn.hint = localization.GetByLabel('UI/Incursion/Journal/RefreshGlobalReport')
        refreshBtn.sr.icon.LoadIcon('ui_105_32_22', ignoreSize=True)
        refreshBtn.SetAlign(uiconst.TOPRIGHT)
        refreshBtn.OnClick = lambda : self.ShowIncursionTab(IncursionTab.GlobalReport)
        self.sr.incursionLPLogFilters = uiprimitives.Container(name='incursionLPLogFilters', parent=self.sr.main, height=36, align=uiconst.TOTOP, state=uiconst.UI_HIDDEN)
        self.sr.incursionLPLoadbutton = uicontrols.Button(parent=self.sr.incursionLPLogFilters, label=localization.GetByLabel('UI/Generic/Load'), align=uiconst.BOTTOMRIGHT, func=self.LoadIncursionLPLog, left=4)
        now = util.FmtDate(blue.os.GetWallclockTime(), 'sn')
        self.sr.incursionLPDate = uicontrols.SinglelineEdit(name='incursionFromdate', parent=self.sr.incursionLPLogFilters, setvalue=now, align=uiconst.TOLEFT, maxLength=16, label=localization.GetByLabel('UI/Common/Date'), padding=(4, 16, 0, 0))
        options = [(localization.GetByLabel('UI/Incursion/Journal/AllIncursionsFilter'), None)]
        self.sr.incursionLPTaleIDFilter = uicontrols.Combo(label=localization.GetByLabel('UI/Incursion/Journal/Incursion'), parent=self.sr.incursionLPLogFilters, options=options, name='incursionTaleIDFilter', width=110, align=uiconst.TOLEFT, padding=(4, 16, 0, 0))
        options = [(localization.GetByLabel('UI/Incursion/Journal/AllTypesFilter'), None)]
        self.sr.incursionLPTypeFilter = uicontrols.Combo(label=localization.GetByLabel('UI/Incursion/Journal/Types'), parent=self.sr.incursionLPLogFilters, options=options, name='incursionTypeFilter', width=110, align=uiconst.TOLEFT, padding=(4, 16, 0, 0))
        self.sr.incursionEncounterEdit = uicontrols.Edit(parent=self.sr.main, name='incursionEncounterEdit', state=uiconst.UI_HIDDEN, readonly=True, align=uiconst.TOALL)
        self.sr.main = uiutil.GetChild(self, 'main')
        self.sr.agentEnglishMissionsCnt = uiprimitives.Container(name='agentEnglishMissionCnt', parent=self.sr.main, padding=(const.defaultPadding,) * 4, height=20, align=uiconst.TOBOTTOM, state=uiconst.UI_HIDDEN)
        self.sr.agentEnglishMissions = uicontrols.Checkbox(parent=self.sr.agentEnglishMissionsCnt, name='agentMissionEnglish', text=localization.GetByLabel('UI/Journal/JournalWindow/Agents/ShowEnglishMissionNames'), checked=settings.user.localization.Get(ENGLISH_MISSIONS_SETTING, False), callback=self.OnAgentEnglishCheckBoxChange)
        self.sr.scroll = uicontrols.Scroll(parent=self.sr.main, padding=(const.defaultPadding,) * 4)
        self.sr.scroll.multiSelect = 0
        self.sr.contractsWnd = uiprimitives.Container(name='contracts', parent=self.sr.main, padding=(const.defaultPadding,) * 4, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.contractFiltersContainer = uiprimitives.Container(name='filters', parent=self.sr.contractsWnd, height=36, align=uiconst.TOTOP)
        top = 13
        statusOptions = [(localization.GetByLabel('UI/Journal/JournalWindow/Contracts/RequiresAttentionFilter'), 0),
         (localization.GetByLabel('UI/Journal/JournalWindow/Contracts/InProgressIssuedByFilter'), 1),
         (localization.GetByLabel('UI/Journal/JournalWindow/Contracts/InProgressAcceptedByFilter'), 2),
         (localization.GetByLabel('UI/Journal/JournalWindow/Contracts/BidOnByFilter'), 3)]
        c = self.statusCombo = uicontrols.Combo(label=localization.GetByLabel('UI/Generic/Status'), parent=self.contractFiltersContainer, options=statusOptions, name='status', callback=self.OnComboChange, pos=(1,
         top,
         0,
         0), width=130)
        ownersOptions = [(localization.GetByLabel('UI/Contracts/ContractsWindow/Me'), False), (localization.GetByLabel('UI/Contracts/ContractsWindow/MyCorporation'), True)]
        c = self.ownerCombo = uicontrols.Combo(label=localization.GetByLabel('UI/Contracts/ContractsWindow/Owner'), parent=self.contractFiltersContainer, options=ownersOptions, name='owner', callback=self.OnComboChange, pos=(c.width + c.left + 5,
         top,
         0,
         0))
        uicontrols.Button(parent=self.contractFiltersContainer, label=localization.GetByLabel('UI/Contracts/ContractsWindow/FetchContracts'), func=self.FetchContracts, pos=(c.left + c.width + 5,
         top,
         0,
         0))
        self.contractsNotifyWnd = uiprimitives.Container(name='contractsnotify', parent=self.sr.contractsWnd, left=const.defaultPadding, top=const.defaultPadding, width=const.defaultPadding, height=30, align=uiconst.TOBOTTOM)
        self.contractsNotifyWnd.state = uiconst.UI_HIDDEN
        self.sr.contractsListWnd = uicontrols.Scroll(parent=self.sr.contractsWnd)
        self.sr.contractsListWnd.multiSelect = 0
        self.CreateEpicJournal()
        self.sr.agenttabs.Startup([[localization.GetByLabel('UI/Journal/JournalWindow/Agents/Missions'),
          self.sr.scroll,
          self,
          ('agent_missions', 0)], [localization.GetByLabel('UI/Journal/JournalWindow/Agents/Research'),
          self.sr.scroll,
          self,
          ('agent_research', 1)], [localization.GetByLabel('UI/Journal/JournalWindow/Agents/LoyaltyPoints'),
          self.sr.scroll,
          self,
          ('agent_lp', 2)]], 'journalagenttabs', autoselecttab=0)
        self.sr.incursiontabs.Startup([[localization.GetByLabel('UI/Incursion/Journal/GlobalReport'),
          self.sr.scroll,
          self,
          ('incursions_globalreport', IncursionTab.GlobalReport)], [localization.GetByLabel('UI/Incursion/Journal/Encounters'),
          self.sr.scroll,
          self,
          ('incursions_encounters', IncursionTab.Encounters)], [localization.GetByLabel('UI/Incursion/Journal/LoyaltyPointLog'),
          self.sr.scroll,
          self,
          ('incursions_lplog', IncursionTab.LPLog)]], 'journalincursiontabs', autoselecttab=0)
        self.sr.maintabs = uicontrols.TabGroup(name='maintabs', parent=self.sr.main, idx=0)
        self.sr.maintabs.Startup([[localization.GetByLabel('UI/Journal/JournalWindow/AgentsTab'),
          self.sr.scroll,
          self,
          ('agents', None)],
         [localization.GetByLabel('UI/Journal/JournalWindow/ExpeditionsTab'),
          self.sr.scroll,
          self,
          ('expeditions', None)],
         [localization.GetByLabel('UI/Journal/JournalWindow/ContractsTab'),
          self.sr.scroll,
          self,
          ('contracts', None)],
         [localization.GetByLabel('UI/Journal/JournalWindow/PlanetaryLaunchesTab'),
          self.sr.scroll,
          self,
          ('launches', None)],
         [localization.GetByLabel('UI/Journal/JournalWindow/EpicJournalTab'),
          self.sr.scroll,
          self,
          ('epicJournal', None)],
         [localization.GetByLabel('UI/Journal/JournalWindow/IncursionsTab'),
          self.sr.scroll,
          self,
          ('incursions', None)]], 'journalmaintabs', autoselecttab=0, UIIDPrefix='journalTab')
        if not skipAutoSelect:
            self.sr.maintabs.AutoSelect()
        sm.RegisterNotify(self)
        return

    def MouseDown(self, *args):
        sm.GetService('neocom').BlinkOff(self.default_windowID)

    def LoadIncursionDistributions(self):
        self._ConstructIncursionDistributionData()
        scrolllist = []
        for distributionId, distributionData in self.incursionDistributions.iteritems():
            data = {'GetSubContent': self.LoadIncursionEncounters,
             'label': distributionData['distributionName'],
             'sublevel': 0,
             'selected': False,
             'id': ('distribution', distributionId),
             'showlen': False,
             'state': 'locked',
             'BlockOpenWindow': True,
             'showicon': 'hide'}
            scrolllist.append(listentry.Get('Group', data))

        scrolllist.sort(key=lambda encounter: encounter['label'])
        self.sr.incursionEncounterScroll.LoadContent(contentList=scrolllist)

    def LoadIncursionEncounters(self, distributionNodeData, *args):
        scrolllist = []
        distributionId = distributionNodeData['id'][1]
        infestationTypes = self.incursionDistributions[distributionId]['infestationTypes']
        for encounterId, encounterLabel in infestationTypes.iteritems():
            encounterNodeData = {'GetSubContent': self.GetIncursionDungeons,
             'label': encounterLabel,
             'encounterId': encounterId,
             'sublevel': 1,
             'selected': False,
             'id': ('encounter', encounterId),
             'showlen': False,
             'state': 'locked',
             'BlockOpenWindow': True,
             'showicon': 'hide'}
            scrolllist.append(listentry.Get('Group', encounterNodeData))

        scrolllist.sort(key=lambda encounter: encounter['label'])
        return scrolllist

    def GetIncursionDungeons(self, encounterDataNode, *args):
        scrolllist = []
        incursionSvc = sm.GetService('incursion')
        for dungeon in INCURSION_DUNGEONS[encounterDataNode['encounterId']]:
            dungeonDataNode = {'label': localization.GetImportantByLabel(dungeon.name),
             'OnClick': self.ShowEncounter,
             'dungeon': dungeon,
             'sublevel': 2,
             'id': ('dungeon', localization.GetImportantByLabel(dungeon.name)),
             'lpAmount': incursionSvc.GetMaxRewardValueByID(dungeon.rewardID, const.rewardTypeLP),
             'iskAmount': incursionSvc.GetMaxRewardValueByID(dungeon.rewardID, const.rewardTypeISK)}
            scrolllist.append(listentry.Get('Generic', dungeonDataNode))

        return scrolllist

    def _ConstructIncursionDistributionData(self):
        self.incursionDistributions = {'sansha': {'distributionName': localization.GetImportantByLabel('UI/Incursion/Distributions/SanshaIncursion/SanshaIncursion'),
                    'infestationTypes': {'scout': localization.GetImportantByLabel('UI/Incursion/Common/Scout'),
                                         'vanguard': localization.GetImportantByLabel('UI/Incursion/Common/Vanguard'),
                                         'assault': localization.GetImportantByLabel('UI/Incursion/Common/Assault'),
                                         'hq': localization.GetImportantByLabel('UI/Incursion/Common/HQ')}},
         'drifters': {'distributionName': localization.GetByLabel('UI/Incursion/Distributions/DefenseOfTheThroneWorlds/DefenseOfTheThroneWorldsIncursion'),
                      'infestationTypes': {'amarr': localization.GetByMessageID(cfg.eveowners.Get(ownerAmarrNavy).ownerNameID),
                                           'drifters': localization.GetByMessageID(cfg.eveowners.Get(factionDrifters).ownerNameID)}}}

    def ShowEncounter(self, node):
        data = node.sr.node
        imgLink = '<img size=250 style=margin-left:8;margin-top:8 src=reward:{rewardID} align=right>'
        html = localization.GetByLabel(data.dungeon.text, lpAmount=data.lpAmount, iskAmount=data.iskAmount, imgLink=imgLink.format(rewardID=data.dungeon.rewardID))
        self.sr.incursionEncounterEdit.LoadHTML(html)

    def OnIncursionEncounterResize(self):
        settings.char.ui.Set('journalIncursionEncounterScrollWidth', self.sr.incursionEncounterScroll.width)

    def OnReportSortByComboChange(self, combo, key, value):
        self.SortIncursionGlobalReport(value)

    def Load(self, args):
        key, flag = args
        self.sr.scroll.ShowHint(None)
        self.sr.contractsWnd.Hide()
        self.sr.epicJournalWnd.Hide()
        self.sr.incursiontabs.Hide()
        self.sr.incursionReportFilter.Hide()
        self.sr.incursionEncounterScroll.Hide()
        self.sr.incursionEncounterEdit.Hide()
        self.sr.agenttabs.Hide()
        self.sr.scroll.Hide()
        self.sr.incursionLPLogFilters.Hide()
        self.sr.agentEnglishMissionsCnt.Hide()
        if key == 'agents':
            self.sr.scroll.Show()
            self.sr.agenttabs.Show()
            self.sr.agenttabs.AutoSelect(silently=1)
        elif key[:6] == 'agent_':
            self.sr.scroll.Show()
            self.sr.agenttabs.Show()
            self.ShowAgentTab(flag)
        elif key == 'expeditions':
            self.sr.scroll.Show()
            self.ShowExpeditions()
        elif key == 'contracts':
            self.sr.contractsWnd.Show()
            self.DoShowContracts()
        elif key == 'epicJournal':
            self.ShowEpicJournal()
        elif key == 'launches':
            self.sr.scroll.Show()
            self.ShowPILaunches()
        elif key.startswith('incursions'):
            self.sr.incursiontabs.Show()
            self.ShowIncursionTab(flag)
        return

    def OnAgentEnglishCheckBoxChange(self, checkbox):
        if checkbox.checked:
            settings.user.localization.Set(ENGLISH_MISSIONS_SETTING, True)
        else:
            settings.user.localization.Delete(ENGLISH_MISSIONS_SETTING)
        if getattr(self.sr, 'maintabs', None):
            self.sr.maintabs.ReloadVisible()
        return

    def ShowAgentTab(self, statusflag=-1):
        self._SelectTab(self.sr.maintabs.sr.Get(localization.GetByLabel('UI/Journal/JournalWindow/AgentsTab') + '_tab'))
        self.sr.agenttabs.Show()
        self.ShowLoad()
        showEnglishTitles = localization.util.GetLanguageID() != localization.const.LOCALE_SHORT_ENGLISH and settings.user.localization.Get(ENGLISH_MISSIONS_SETTING, False)
        if statusflag == 0:
            missions = sm.GetService('journal').GetMyAgentJournalDetails()[0]
            scrolllist = []
            if len(missions):
                missionIconData = []
                maxOptionalIcons = 0
                for i in xrange(len(missions)):
                    missionIconData.append(self.GetMissionIconDataForAgentTab(missions[i]))
                    maxOptionalIcons = max(maxOptionalIcons, len(missionIconData[i]))

                for i in xrange(len(missions)):
                    state = ''
                    missionState, importantMission, missionTypeLabel, missionNameID, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable, contentID = missions[i]
                    missionType = localization.GetByLabel(missionTypeLabel)
                    if isinstance(missionNameID, (int, long)):
                        missionName = localization.GetByMessageID(missionNameID)
                        if showEnglishTitles:
                            enMissionName = localization.GetByMessageID(missionNameID, languageID=localization.const.LOCALE_SHORT_ENGLISH)
                    else:
                        enMissionName = missionName = missionNameID
                    sm.GetService('agents').PrimeMessageArguments(agentID, contentID)
                    blankIconID = 'ui_38_16_39'
                    for j in xrange(maxOptionalIcons - len(missionIconData[i])):
                        missionIconData[i].insert(0, (blankIconID, ''))

                    missionStateLabel = {const.agentMissionStateAllocated: localization.GetByLabel('UI/Journal/JournalWindow/Agents/StateOffered'),
                     const.agentMissionStateOffered: localization.GetByLabel('UI/Journal/JournalWindow/Agents/StateOffered'),
                     const.agentMissionStateAccepted: localization.GetByLabel('UI/Journal/JournalWindow/Agents/StateAccepted'),
                     const.agentMissionStateFailed: localization.GetByLabel('UI/Journal/JournalWindow/Agents/StateFailed')}
                    missionLogInfo = '%s mission %d (%s) %s' % (missionStateLabel[missionState],
                     i,
                     missionName,
                     'expires in ' + util.FmtTimeInterval(expirationTime - blue.os.GetWallclockTime()) if expirationTime else 'does not expire')
                    log.LogInfo('Journal::ShowAgentTab:', missionLogInfo)
                    if importantMission:
                        missionType = '<color=0xFFFFFF00>' + localization.GetByLabel('UI/Journal/JournalWindow/Agents/ImportantMission', missionType=missionType) + '<color=0xffffffff>'
                    if missionState in (const.agentMissionStateAllocated, const.agentMissionStateOffered):
                        state = '<color=0xFFFFFF00>' + missionStateLabel[missionState] + '<color=0xffffffff>'
                        if expirationTime > blue.os.GetWallclockTime() + const.WEEK + const.MIN:
                            expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/OfferExpiresAt', expirationTime=expirationTime)
                            log.LogInfo('* Showing date only (expiration time is longer than ' + util.FmtTimeInterval(const.WEEK + const.MIN) + ')')
                        elif expirationTime > blue.os.GetWallclockTime() + const.DAY:
                            expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/OfferExpiresAtExact', expirationTime=expirationTime)
                            log.LogInfo('* Showing hours/minutes (expiration time is between ' + util.FmtTimeInterval(const.DAY) + ' and ' + util.FmtTimeInterval(const.WEEK + const.MIN) + ')')
                        else:
                            log.LogInfo('* Showing other expiration message')
                            if expirationTime:
                                expirationTime -= blue.os.GetWallclockTime()
                                expirationTime = int(expirationTime / const.MIN) * const.MIN
                            if expirationTime == 0:
                                expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/OfferDoesNotExpire')
                            elif not expirationTime:
                                expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/OfferUndefinedExpiration')
                            elif expirationTime > 0:
                                expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/OfferExpiresIn', expirationTime=expirationTime)
                            else:
                                expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/OfferExpired')
                                state = '<color=0xffeb3700>' + localization.GetByLabel('UI/Journal/JournalWindow/Agents/StateOfferExpired') + '<color=0xffffffff>'
                    if missionState in (const.agentMissionStateAccepted, const.agentMissionStateFailed):
                        if missionState == const.agentMissionStateAccepted:
                            state = '<color=0xff00FF00>' + missionStateLabel[missionState] + '<color=0xffffffff>'
                        else:
                            state = '<color=0xffeb3700>' + missionStateLabel[missionState] + '<color=0xffffffff>'
                        if expirationTime > blue.os.GetWallclockTime() + const.WEEK + const.MIN:
                            expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/MissionExpiresAt', expirationTime=expirationTime)
                            log.LogInfo('* Showing date only (expiration time is longer than ' + util.FmtTimeInterval(const.WEEK + const.MIN) + ')')
                        elif expirationTime > blue.os.GetWallclockTime() + const.DAY:
                            expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/MissionExpiresAtExact', expirationTime=expirationTime)
                            log.LogInfo('* Showing hours/minutes (expiration time is between ' + util.FmtTimeInterval(const.DAY) + ' and ' + util.FmtTimeInterval(const.WEEK + const.MIN) + ')')
                        else:
                            log.LogInfo('* Showing other expiration message')
                            if expirationTime:
                                expirationTime -= blue.os.GetWallclockTime()
                                expirationTime = int(expirationTime / const.MIN) * const.MIN
                            if expirationTime == 0:
                                expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/MissionDoesNotExpire')
                            elif not expirationTime:
                                expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/MissionUndefinedExpiration')
                            elif expirationTime > 0:
                                expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/MissionExpiresIn', expirationTime=expirationTime)
                            else:
                                expirationText = localization.GetByLabel('UI/Journal/JournalWindow/Agents/MissionExpired')
                                state = '<color=0xffeb3700>' + localization.GetByLabel('UI/Journal/JournalWindow/Agents/StateMissionExpired') + '<color=0xffffffff>'
                    if showEnglishTitles:
                        text = '<t>'.join([state,
                         cfg.eveowners.Get(agentID).name,
                         missionName,
                         enMissionName,
                         missionType,
                         expirationText])
                    else:
                        text = '<t>'.join([state,
                         cfg.eveowners.Get(agentID).name,
                         missionName,
                         missionType,
                         expirationText])
                    scrolllist.append(listentry.Get('VirtualAgentMissionEntry', {'missionState': missionState,
                     'agentID': agentID,
                     'label': text,
                     'missionIconData': missionIconData[i]}))

            if showEnglishTitles:
                headers = [localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderStatus'),
                 localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderAgent'),
                 localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderMission'),
                 localization.GetByLabel('UI/Journal/JournalWindow/Agents/EnglishName'),
                 localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderType'),
                 localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderExpiration')]
            else:
                headers = [localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderStatus'),
                 localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderAgent'),
                 localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderMission'),
                 localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderType'),
                 localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderExpiration')]
            self._SelectTab(self.sr.agenttabs.sr.tabs[0])
            self.sr.scroll.sr.id = 'agentjournalscroll%s' % statusflag
            self.sr.scroll.Load(contentList=scrolllist, headers=headers, noContentHint=localization.GetByLabel('UI/Journal/JournalWindow/Agents/NoMissionsOfferedOrAccepted'))
            if localization.util.GetLanguageID() != localization.const.LOCALE_SHORT_ENGLISH:
                self.sr.agentEnglishMissionsCnt.Show()
        elif statusflag == 1:
            research = sm.GetService('journal').GetMyAgentJournalDetails()[1]
            scrolllist = []
            if len(research):
                for i in xrange(len(research)):
                    agentID, typeID, ppd, points, level, quality, stationID = research[i]
                    solarSystemID = sm.StartService('ui').GetStation(stationID).solarSystemID
                    text = '<t>'.join([cfg.eveowners.Get(agentID).name,
                     evetypes.GetName(typeID),
                     localization.formatters.FormatNumeric(points, decimalPlaces=2, useGrouping=True),
                     localization.formatters.FormatNumeric(ppd, decimalPlaces=2, useGrouping=True),
                     localization.formatters.FormatNumeric(level, decimalPlaces=0),
                     cfg.evelocations.Get(stationID).name])
                    scrolllist.append(listentry.Get('VirtualResearchEntry', {'agentID': agentID,
                     'text': text,
                     'label': text,
                     'solarSystemID': solarSystemID}))

            self._SelectTab(self.sr.agenttabs.sr.tabs[1])
            self.sr.scroll.sr.id = 'agentjournalscroll%s' % statusflag
            self.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderAgent'),
             localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderResearchField'),
             localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderResearchPoints'),
             localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderResearchPerDay'),
             localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderAgentLevel'),
             localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderAgentLocation')], noContentHint=localization.GetByLabel('UI/Journal/JournalWindow/Agents/NoResearchBeingPerformed'))
        elif statusflag == 2:
            lps = sm.GetService('journal').GetMyLoyaltyPoints()
            scrolllist = []
            if len(lps):
                for i in xrange(len(lps)):
                    corporationID, loyaltyPoints = lps[i]
                    label = '<t>'.join([cfg.eveowners.Get(corporationID).name, localization.formatters.FormatNumeric(loyaltyPoints)])
                    data = util.KeyVal()
                    data.GetMenu = self.ShowCorpMenu
                    data.label = label
                    data.hilite = None
                    data.hint = ''
                    data.selection = None
                    data.corporationID = corporationID
                    scrolllist.append(listentry.Get('Generic', data=data))

            self.sr.scroll.sr.id = 'agentjournalscroll%s' % statusflag
            self.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Journal/JournalWindow/Agents/HeaderIssuingCorporation'), localization.GetByLabel('UI/Journal/JournalWindow/Agents/LoyaltyPoints')], noContentHint=localization.GetByLabel('UI/Journal/JournalWindow/Agents/NoLP'))
            self._SelectTab(self.sr.agenttabs.sr.tabs[2])
        self.HideLoad()
        return

    def _SelectTab(self, tab):
        if tab is None:
            return
        else:
            if not tab.IsSelected():
                tab.Select(True)
            return

    def ShowCorpMenu(self, entry):
        self.entry = entry
        m = [(localization.GetByLabel('UI/Commands/ShowInfo'), self.ShowCorpInfo)]
        lpSvc = sm.GetService('lpstore')
        xChangeRate = lpSvc.GetConcordLPExchangeRate(entry.sr.node.corporationID)
        concordLPs = lpSvc.GetMyConcordLPs()
        if eve.session.stationid is not None and xChangeRate is not None and xChangeRate > 0.0 and concordLPs > 0:
            m.append((uiutil.MenuLabel('UI/Journal/JournalWindow/Agents/ConvertConcordLoyaltyPoints'), self.ShowConcordExchangeDialog))
        return m

    def ShowCorpInfo(self):
        sm.GetService('info').ShowInfo(cfg.eveowners.Get(self.entry.sr.node.corporationID).typeID, self.entry.sr.node.corporationID)

    def ShowConcordExchangeDialog(self):
        sm.GetService('lpstore').OpenConcordExchange(self.entry.sr.node.corporationID)

    def GetMissionIconDataForAgentTab(self, missionJournalDetails):
        missionState, importantMission, missionType, missionName, agentID, expirationTime, bookmarks, remoteOfferable, remoteCompletable, contentID = missionJournalDetails
        missionIconData = []
        chatBubbleIconID = 'ui_38_16_38'
        remoteMissionHints = []
        if remoteOfferable:
            remoteMissionHints.append(localization.GetByLabel('UI/Agents/Dialogue/StandardMission/AcceptRemotelyHint'))
        if remoteCompletable:
            remoteMissionHints.append(localization.GetByLabel('UI/Agents/Dialogue/StandardMission/CompleteRemotelyHint'))
        if remoteOfferable or remoteCompletable:
            remoteMissionHintText = '<br>'.join(remoteMissionHints)
            missionIconData.append((chatBubbleIconID, remoteMissionHintText))
        return missionIconData

    def ShowEpicJournal(self):
        self.sr.epicJournalWnd.Show()
        self.LoadEpicJournal(self.selectedArc)
        self._SelectTab(self.sr.maintabs.sr.Get(localization.GetByLabel('UI/Journal/JournalWindow/EpicJournalTab') + '_tab'))

    def LoadEpicJournal(self, selectedArcName=None):
        scrolllist = []
        arcs = self.GetEpicArcs()
        selectIndex = 0
        for i, (completed, arcName) in enumerate(arcs):
            if selectedArcName == arcName:
                selectIndex = i
            if completed:
                arcName = localization.GetByLabel('UI/Journal/JournalWindow/EpicArcs/EmphasisedArcName', arcName=arcName)
                hint = localization.GetByLabel('UI/Journal/JournalWindow/EpicArcs/CompletedHint', arcName=arcName)
            else:
                hint = localization.GetByLabel('UI/Journal/JournalWindow/EpicArcs/InProgressHint', arcName=arcName)
            scrolllist.append(listentry.Get('Generic', {'label': arcName,
             'value': i,
             'hint': hint}))

        self.epicArcScroll.Load(contentList=scrolllist, noContentHint=localization.GetByLabel('UI/Journal/JournalWindow/EpicArcs/NoArc'))
        self.epicArcScroll.SetSelected(selectIndex)

    def GetEpicArcs(self):
        return [ (x.completed, localization.GetByMessageID(x.titleID)) for x in self.GetMyEpicJournalData() ]

    def CreateEpicJournal(self):
        self.sr.epicJournalWnd = uiprimitives.Container(name='epicJournal', parent=self.sr.main, padding=const.defaultPadding, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        epicArcWidth = settings.user.ui.Get('journalEpicArcWidth', 100)
        self.epicArcContainer = uiprimitives.Container(name='epicArcContainer', parent=self.sr.epicJournalWnd, align=uiconst.TOLEFT, clipChildren=1, width=epicArcWidth)
        uicontrols.EveLabelMedium(text='<center>' + localization.GetByLabel('UI/Journal/JournalWindow/EpicArcs/LabelArcs') + '</center>', parent=self.epicArcContainer, height=20, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.epicArcScroll = uicontrols.Scroll(parent=self.epicArcContainer, name='epicArcScroll')
        self.epicArcScroll.OnSelectionChange = self.SelectEpicArc
        self.epicArcScroll.multiSelect = 0
        divider = Divider(name='epicArcDivider', align=uiconst.TOLEFT, width=const.defaultPadding, parent=self.sr.epicJournalWnd, state=uiconst.UI_NORMAL)
        dividerMin = 100
        dividerMax = self.epicArcScroll.GetMaxTextWidth(150) + self.default_scrollPanelPadding
        divider.Startup(self.epicArcContainer, 'width', 'x', dividerMin, dividerMax)
        divider.OnSizeChanged = self.OnEpicArcSizeChanged
        epicMissionContainerWidth = settings.user.ui.Get('journalEpicMissionWidth', 150)
        self.epicMissionContainer = uiprimitives.Container(name='epicMissionContainer', parent=self.sr.epicJournalWnd, align=uiconst.TORIGHT, clipChildren=1, width=epicMissionContainerWidth)
        uicontrols.EveLabelMedium(text='<center>' + localization.GetByLabel('UI/Journal/JournalWindow/EpicArcs/LabelMissions') + '</center>', parent=self.epicMissionContainer, height=20, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.epicMissionScroll = uicontrols.Scroll(parent=self.epicMissionContainer, name='epicMissionScroll')
        self.epicMissionScroll.OnSelectionChange = self.SelectEpicMission
        self.epicMissionScroll.multiSelect = 0
        divider = Divider(name='epicMissionDivider', align=uiconst.TORIGHT, width=const.defaultPadding, parent=self.sr.epicJournalWnd, state=uiconst.UI_NORMAL)
        dividerMin = 100
        dividerMax = self.epicMissionScroll.GetMaxTextWidth(200) + self.default_scrollPanelPadding
        divider.Startup(self.epicMissionContainer, 'width', 'x', dividerMin, dividerMax)
        divider.OnSizeChanged = self.OnEpicMissionSizeChanged
        epicMainContainer = uiprimitives.Container(name='epicMainContainer', parent=self.sr.epicJournalWnd, align=uiconst.TOALL, clipChildren=1)
        self.epicArcTitleImage = uiprimitives.Sprite(name='epicArcTitleImage', parent=epicMainContainer, align=uiconst.TOTOP)
        self.epicArcTitleImage._OnSizeChange_NoBlock = self.OnEpicArcTitleImageResize
        self.epicJournalText = uicontrols.Edit(parent=epicMainContainer, readonly=1)

    def OnEpicArcSizeChanged(self):
        settings.user.ui.Set('journalEpicArcWidth', self.epicArcContainer.width)

    def OnEpicMissionSizeChanged(self):
        settings.user.ui.Set('journalEpicMissionWidth', self.epicMissionContainer.width)

    def OnEpicArcTitleImageResize(self, width, height):
        if width:
            self.epicArcTitleImage.height = int(width / 2.5)

    def SelectEpicMission(self, selected):
        if len(selected) and hasattr(selected[0], 'value'):
            self.LoadEpicArcText(selected[0].value)
        else:
            self.LoadEpicArcText()

    def SelectEpicArc(self, selected):
        if len(selected):
            self.LoadEpicArc(selected[0].value)
            self.selectedArc = selected[0].label
        else:
            self.epicMissionScroll.Clear()
            self.epicArcTitleImage.Hide()
            self.epicJournalText.SetText('')

    def OnEpicJournalChange(self):
        self.epicJournalData = None
        self.LoadEpicJournal(self.selectedArc)
        return

    def LoadEpicArc(self, epicArcId):
        self.curEpicArcId = epicArcId
        texture = self.epicArcTitleImage.texture
        texture.resPath = self.GetEpicArcGraphic(epicArcId)
        while texture.atlasTexture.isLoading:
            blue.synchro.Yield()

        self.epicArcTitleImage.Show()
        scrolllist = []
        for i, (chapterTitle, missionName, missionText, branches) in enumerate(self.GetEpicArcMissions(epicArcId)):
            if chapterTitle:
                scrolllist.append(listentry.Get('Subheader', {'label': chapterTitle}))
            if branches:
                branchList = [localization.GetByLabel('UI/Journal/JournalWindow/EpicArcs/BranchPoint')]
                for branch in branches:
                    branchList.append(branch)

                scrolllist.append(listentry.Get('IconEntry', {'label': missionName,
                 'hint': '<br>'.join(branchList),
                 'icon': 'ui_38_16_87',
                 'iconsize': 16,
                 'value': i}))
            else:
                scrolllist.append(listentry.Get('Generic', {'label': missionName,
                 'value': i}))

        self.epicMissionScroll.Load(contentList=scrolllist)
        self.LoadEpicArcText()

    def GetEpicArcGraphic(self, epicArcIndex):
        return self.GetMyEpicJournalData()[epicArcIndex].graphic

    def LoadEpicArcText(self, selectedMissionId=None):
        if self.curEpicArcId is None:
            return
        else:
            missionTextList = []
            for i, (chapterTitle, missionName, missionText, branches) in enumerate(self.GetEpicArcMissions(self.curEpicArcId)):
                if chapterTitle:
                    if i != 0:
                        missionTextList.append('<br>')
                    missionTextList.append('<font size=16>' + chapterTitle + '</font>')
                if missionText:
                    if selectedMissionId == i:
                        text = localization.GetByLabel('UI/Journal/JournalWindow/EpicArcs/EmphasisedMissionText', imageHTML='<img src=icon:38_254 size=16>', missionText=missionText)
                        missionTextList.append('<font size=14>' + text + '</font>')
                    else:
                        missionTextList.append('<img src=icon:38_254 size=12>' + missionText)

            self.epicJournalText.SetText('<br>'.join(missionTextList))
            return

    def GetEpicArcMissions(self, epicArcIndex):
        return self.GetMyEpicJournalData()[epicArcIndex].displayMissions

    def GetMyEpicJournalData(self):
        if self.epicJournalData is None:
            self.epicJournalData = sm.RemoteSvc('agentMgr').GetMyEpicJournalDetails()
            for epicArcEntry in self.epicJournalData:
                newMissionList = []
                epicArcEntry.displayMissions = []
                for status, chapterNameID, missionNameID, inProgressTextID, completedTextID, quitInfo, branches in epicArcEntry.missions:
                    newMission = []
                    newMission.append(localization.GetByMessageID(chapterNameID))
                    newMission.append(localization.GetByMessageID(missionNameID))
                    if status == 'completed':
                        newMission.append(localization.GetByMessageID(completedTextID))
                    else:
                        jList = []
                        if inProgressTextID:
                            jList.append(localization.GetByMessageID(inProgressTextID))
                        if status == 'quit':
                            quitDate, restartDate = quitInfo
                            if restartDate > blue.os.GetWallclockTime():
                                jList.append(localization.GetByLabel('UI/Agents/EpicArcs/QuitArcRestartLater', quitTime=quitDate, restartTime=restartDate))
                            else:
                                jList.append(localization.GetByLabel('UI/Agents/EpicArcs/QuitArcRestartNow', quitTime=quitDate))
                        newMission.append('<br><br>'.join(jList))
                    branchDisplayList = []
                    for branch in branches:
                        branchName = localization.GetByMessageID(branch[0])
                        if branch[1]:
                            branchName = '<b>%s</b>' % branchName
                        branchDisplayList.append(branchName)

                    newMission.append(branchDisplayList)
                    newMissionList.append(newMission)

                epicArcEntry.displayMissions = newMissionList

            self.epicJournalData.sort()
        return self.epicJournalData

    def ShowExpeditions(self, reload=0):
        expeditionRowset = sm.GetService('journal').GetExpeditions(force=reload)
        self.ShowLoad()
        try:
            scrolllist = []
            sort_by_expirytime_key = 'sort_' + localization.GetByLabel('UI/Journal/JournalWindow/Expeditions/HeaderExpiration')
            for expeditionData in expeditionRowset:
                dungeonData = expeditionData.dungeon
                destDungeonData = expeditionData.destDungeon
                pathStep = expeditionData.pathStep
                expiryTime = expeditionData.expiryTime
                if destDungeonData is not None:
                    autopilotJumps = self.clientPathfinderService.GetAutopilotJumpCount(dungeonData.solarSystemID, session.solarsystemid2)
                    if dungeonData.solarSystemID is not None:
                        solName = cfg.evelocations.Get(dungeonData.solarSystemID).name
                    else:
                        solName = localization.GetByLabel('UI/Common/Unknown')
                    txt = localization.GetByMessageID(destDungeonData.dungeonNameID)
                    if len(txt) > MAX_COL_LENGTH:
                        txt = txt[:MAX_COL_LENGTH] + '...'
                    text = '<t>'.join(['      ',
                     util.FmtDate(dungeonData.creationTime),
                     solName,
                     str(autopilotJumps),
                     txt])
                    expired = not expiryTime - blue.os.GetWallclockTime() > 0
                    data = {'id': dungeonData.instanceID,
                     'rec': expeditionData,
                     'text': txt,
                     'label': text,
                     'hint': localization.GetByMessageID(pathStep.journalEntryTemplateID),
                     'jumps': autopilotJumps,
                     'expired': expired,
                     sort_by_expirytime_key: expiryTime}
                    scrolllist.append(listentry.Get('EscalatingPathLocationEntry', data))

            self.sr.scroll.sr.id = 'expeditionScroll'
            self.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Journal/JournalWindow/Expeditions/HeaderExpiration'),
             localization.GetByLabel('UI/Journal/JournalWindow/Expeditions/HeaderCreated'),
             localization.GetByLabel('UI/Journal/JournalWindow/Expeditions/HeaderSolarSystem'),
             localization.GetByLabel('UI/Journal/JournalWindow/Expeditions/HeaderJumps'),
             localization.GetByLabel('UI/Journal/JournalWindow/Expeditions/HeaderDescription')], noContentHint=localization.GetByLabel('UI/Journal/JournalWindow/Expeditions/NoActiveExpeditions'))
            self.AutoUpdateExpeditionTimes()
            self.sr.expeditiontimer = base.AutoTimer(1000, self.AutoUpdateExpeditionTimes)
        finally:
            self._SelectTab(self.sr.maintabs.sr.Get(localization.GetByLabel('UI/Journal/JournalWindow/ExpeditionsTab') + '_tab'))
            self.HideLoad()

        return

    def AutoUpdateExpeditionTimes(self):
        if self.destroyed or self.sr.maintabs.GetSelectedArgs()[0] != 'expeditions':
            self.sr.expeditiontimer = None
            return
        else:
            for entry in self.sr.scroll.GetNodes():
                text = entry.label
                if not entry.rec:
                    continue
                expiryLabel = ''
                expiryNumeric = entry.rec.expiryTime - blue.os.GetWallclockTime()
                if expiryNumeric > 0:
                    expiryLabel = '<color=0xFFFFFF00>' + localization.formatters.FormatTimeIntervalWritten(expiryNumeric, showFrom='day', showTo='second') + '</color>'
                else:
                    expiryLabel = '<color=0xffeb3700>' + localization.GetByLabel('UI/Journal/JournalWindow/Expeditions/Expired') + '</color>'
                entry.label = expiryLabel + text[text.find('<t>'):]
                if entry.panel:
                    entry.panel.Load(entry)

            return

    def OnEscalatingPathChange(self, *args):
        self.ShowExpeditions(True)

    def OnEscalatingPathMessage(self, instanceID):
        self.ShowExpeditions(True)

    def ShowPILaunches(self, reload=0):
        launchsRowSet = sm.GetService('journal').GetLaunches(force=reload)
        self.ShowLoad()
        try:
            scrolllist = []
            for launch in launchsRowSet:
                label = '<t>'.join(['    ',
                 cfg.evelocations.Get(launch.solarSystemID).name,
                 cfg.evelocations.Get(launch.planetID).name,
                 util.FmtDate(launch.launchTime)])
                expired = not blue.os.GetWallclockTime() - launch.launchTime < const.piLaunchOrbitDecayTime
                data = {'id': launch.launchID,
                 'label': label,
                 'callback': None,
                 'selected': 0,
                 'expired': expired,
                 'rec': launch}
                scrolllist.append(listentry.Get('PlanetaryInteractionLaunchEntry', data))

            self.sr.scroll.sr.id = 'launchesScroll'
            self.sr.scroll.Load(contentList=scrolllist, headers=[localization.GetByLabel('UI/Journal/JournalWindow/PI/HeaderReentry'),
             localization.GetByLabel('UI/Journal/JournalWindow/PI/HeaderSolarSystem'),
             localization.GetByLabel('UI/Journal/JournalWindow/PI/HeaderPlanet'),
             localization.GetByLabel('UI/Journal/JournalWindow/PI/HeaderLaunchTime')], noContentHint=localization.GetByLabel('UI/Journal/JournalWindow/PI/NoActiveLaunches'))
            self.AutoUpdateLaunchDecayTimes()
            self.sr.launchtimer = base.AutoTimer(1000, self.AutoUpdateLaunchDecayTimes)
        finally:
            self._SelectTab(self.sr.maintabs.sr.Get(localization.GetByLabel('UI/Journal/JournalWindow/PlanetaryLaunchesTab') + '_tab'))
            self.HideLoad()

        return

    def OnPILaunchesChange(self, *args):
        self.ShowPILaunches(True)

    def AutoUpdateLaunchDecayTimes(self):
        if not self or self.destroyed or self.sr.maintabs.GetSelectedArgs()[0] != 'launches':
            self.sr.launchtimer = None
            return
        else:
            for entry in self.sr.scroll.GetNodes():
                text = entry.label
                if not entry.rec:
                    continue
                expiryLabel = ''
                expiryNumeric = blue.os.GetWallclockTime() - entry.rec.launchTime
                if expiryNumeric < const.piLaunchOrbitDecayTime:
                    expiryLabel = '<color=0xFFFFFF00>' + localization.formatters.FormatTimeIntervalShortWritten(const.piLaunchOrbitDecayTime - expiryNumeric) + '</color>'
                else:
                    expiryLabel = '<color=0xffeb3700>' + localization.GetByLabel('UI/Journal/JournalWindow/PI/BurnedUp') + '</color>'
                    entry.expired = True
                entry.label = expiryLabel + text[text.find('<t>'):]
                if entry.panel:
                    entry.panel.Load(entry)

            return

    def GetJumpCount(self, toID):
        jumps = self.clientPathfinderService.GetAutopilotJumpCount(session.solarsystemid2, toID)
        if IsUnreachableJumpCount(jumps):
            return None
        else:
            return jumps

    def ShowIncursionTab(self, flag=None, constellationID=None, taleID=None):
        if self.showingIncursionTab:
            return
        else:
            self.showingIncursionTab = True
            if flag is None:
                flag = settings.char.ui.Get('journalIncursionTab', IncursionTab.GlobalReport)
            settings.char.ui.Set('journalIncursionTab', flag)
            self._SelectTab(self.sr.maintabs.sr.Get(localization.GetByLabel('UI/Journal/JournalWindow/IncursionsTab') + '_tab'))
            self._SelectTab(self.sr.incursiontabs.sr.tabs[flag])
            if flag == IncursionTab.GlobalReport:
                self.sr.scroll.Show()
                self.sr.incursionReportFilter.state = uiconst.UI_PICKCHILDREN
                starmap = sm.GetService('starmap')
                map = starmap.map
                report = sm.RemoteSvc('map').GetIncursionGlobalReport()
                rewardGroupIDs = [ r.rewardGroupID for r in report ]
                delayedRewards = sm.GetService('incursion').GetDelayedRewardsByGroupIDs(rewardGroupIDs)
                scrolllist = []
                factionsToPrime = set()
                for data in report:
                    data.jumps = self.GetJumpCount(data.stagingSolarSystemID)
                    data.influenceData = util.KeyVal(influence=data.influence, lastUpdated=data.lastUpdated, graceTime=data.graceTime, decayRate=data.decayRate)
                    ssitem = map.GetItem(data.stagingSolarSystemID)
                    data.stagingSolarSystemName = ssitem.itemName
                    data.security = map.GetSecurityStatus(data.stagingSolarSystemID)
                    data.constellationID = ssitem.locationID
                    data.constellationName = map.GetItem(ssitem.locationID).itemName
                    data.factionID = ssitem.factionID or starmap.GetAllianceSolarSystems().get(data.stagingSolarSystemID, None)
                    factionsToPrime.add(data.factionID)
                    rewards = delayedRewards.get(data.rewardGroupID, None)
                    data.loyaltyPoints = rewards[0].rewardQuantity if rewards else 0
                    scrolllist.append(listentry.Get('GlobalIncursionReportEntry', data))

                cfg.eveowners.Prime(list(factionsToPrime))
                self.sr.scroll.LoadContent(contentList=scrolllist, scrollTo=0.0)
                self.SortIncursionGlobalReport()
            elif flag == IncursionTab.LPLog:
                self.sr.incursionLPLogFilters.Show()
                self.sr.scroll.Show()
                if taleID is not None and constellationID is not None:
                    self.LoadIncursionLPLog(self.sr.scroll, taleID, constellationID)
                elif self.incursionLPLogData is None:
                    self.sr.scroll.Clear()
                    self.sr.scroll.ShowHint(localization.GetByLabel('UI/Incursion/Journal/LoadData'))
                else:
                    self.UpdateIncursionLPLog(self.incursionLPLogData)
            elif flag == IncursionTab.Encounters:
                self.sr.incursionEncounterEdit.Show()
                self.sr.incursionEncounterScroll.Show()
                self.sr.incursionEncounterDivider.Show()
            self.showingIncursionTab = False
            return

    def SortIncursionGlobalReport(self, sortBy=None):
        if sortBy is None:
            sortBy = settings.char.ui.Get('journalIncursionReportSort', ReportSortBy.Constellation)
        else:
            settings.char.ui.Set('journalIncursionReportSort', sortBy)
        attrName, reverse = REPORT_SORT_PARAMETERS[sortBy]
        scroll = self.sr.scroll
        scroll.sr.nodes = sorted(scroll.sr.nodes, key=attrgetter(attrName), reverse=reverse)
        scroll.UpdatePositionThreaded(fromWhere='SortIncursionGlobalReport')
        return

    def LoadIncursionLPLog(self, scroll, taleID=None, constellationID=None):
        rewardMgr = session.ConnectToRemoteService('rewardMgr')
        self.incursionLPLogData = rewardMgr.GetRewardLPLogs()
        self.UpdateIncursionLPLog(self.incursionLPLogData, taleID, constellationID)

    def UpdateIncursionLPLog(self, data, selectedTaleID=None, selectedConstellationID=None):
        mapsvc = sm.GetService('map')
        taleIDFilter = self.sr.incursionLPTaleIDFilter.selectedValue
        solarsystemTypeFilter = self.sr.incursionLPTypeFilter.selectedValue
        try:
            fromDate = util.ParseSmallDate(self.sr.incursionLPDate.GetValue())
        except (Exception, TypeError):
            dateString = localization.formatters.FormatDateTime(blue.os.GetWallclockTime(), dateFormat='short', timeFormat='none')
            fromDate = util.ParseDate(dateString)
            self.sr.incursionLPDate.SetValue(dateString)

        fromDate += const.DAY
        dungeonTypes = set()
        taleIDs = {}
        filteredData = []
        for d in data:
            dungeonTypes.add(d.rewardMessageKey)
            constellationID = mapsvc.GetParent(d.solarSystemID)
            if constellationID is not None:
                constellation = mapsvc.GetItem(constellationID)
                if constellation is not None:
                    taleIDs[d.taleID] = constellation.itemName
            if selectedTaleID is not None:
                if selectedTaleID != d.taleID:
                    continue
            if taleIDFilter is not None and selectedTaleID is None:
                if taleIDFilter != d.taleID:
                    continue
            if solarsystemTypeFilter is not None:
                shouldAdd = False
                if solarsystemTypeFilter == LPTypeFilter.LPPayedOut:
                    if d.eventTypeID == logConst.eventRewardLPPoolPayedOut:
                        shouldAdd = True
                elif solarsystemTypeFilter == LPTypeFilter.LPLost:
                    if d.eventTypeID == logConst.eventRewardLPPoolLost:
                        shouldAdd = True
                elif solarsystemTypeFilter == d.rewardMessageKey:
                    shouldAdd = True
                if not shouldAdd:
                    continue
            if fromDate < d.date:
                continue
            filteredData.append(d)

        if selectedTaleID is not None:
            if selectedTaleID not in taleIDs:
                constellation = mapsvc.GetItem(selectedConstellationID)
                if constellation is not None:
                    taleIDs[selectedTaleID] = constellation.itemName
        scrolllist = []
        for d in filteredData:
            solarSystemType = ''
            if d.eventTypeID == logConst.eventRewardLPPoolPayedOut:
                solarSystemType = localization.GetByLabel('UI/Incursion/Journal/CompletedAndPaidOut')
            elif d.eventTypeID == logConst.eventRewardLPPoolLost:
                solarSystemType = localization.GetByLabel('UI/Incursion/Journal/CompletedAndNotPaidOut')
            elif d.rewardMessageKey is not None and isinstance(d.rewardMessageKey, int):
                solarSystemType = localization.GetByMessageID(d.rewardMessageKey)
            elif d.rewardMessageKey is not None and d.rewardMessageKey != '':
                solarSystemType = localization.GetByLabel(d.rewardMessageKey)
            if d.lpAmountAddedToPool is None:
                d.lpAmountAddedToPool = 0
            if d.lpAmountAddedToPool == 0:
                LPAmountAddedToPool = '<color=0xFFFFFFFF>' + localization.formatters.FormatNumeric(0) + '</color>'
            else:
                LPAmountAddedToPool = '<color=0xFFFFFF00>' + localization.formatters.FormatNumeric(d.lpAmountAddedToPool) + '</color>'
            if d.lpAmountPayedOut is None:
                d.lpAmountPayedOut = 0
            if d.lpAmountPayedOut == 0:
                LPAmountPayedOut = '<color=0xFFFFFFFF>' + localization.formatters.FormatNumeric(0) + '</color>'
            elif d.eventTypeID == logConst.eventRewardLPPoolLost:
                LPAmountPayedOut = '<color=0xFFFF0000>' + localization.formatters.FormatNumeric(0) + '</color>'
            else:
                LPAmountPayedOut = '<color=0xFF00FF00>' + localization.formatters.FormatNumeric(d.lpAmountPayedOut) + '</color>'
            if d.numberOfPlayers is None:
                d.numberOfPlayers = 0
            description = ''
            if d.eventTypeID == logConst.eventRewardDisqualified:
                if d.disqualifierType == const.rewardIneligibleReasonTrialAccount:
                    description = localization.GetByLabel('UI/Incursion/Journal/DisqualifiedTrialAccount')
                elif d.disqualifierType == const.rewardIneligibleReasonInvalidGroup:
                    groupName = evetypes.GetGroupNameByGroup(d.disqualifierData)
                    description = localization.GetByLabel('UI/Incursion/Journal/DisqualifiedInvalidShipGroup2', groupName=groupName)
                elif d.disqualifierType == const.rewardIneligibleReasonShipCloaked:
                    description = localization.GetByLabel('UI/Incursion/Journal/DisqualifiedCloaked')
                elif d.disqualifierType == const.rewardIneligibleReasonNotInFleet:
                    description = localization.GetByLabel('UI/Incursion/Journal/DisqualifiedNoFleet')
                elif d.disqualifierType == const.rewardIneligibleReasonNotBestFleet:
                    description = localization.GetByLabel('UI/Incursion/Journal/DisqualifiedNotBestFleet')
                elif d.disqualifierType == const.rewardIneligibleReasonNotTop5:
                    description = localization.GetByLabel('UI/Incursion/Journal/DisqualifiedNotInTopFive')
                elif d.disqualifierType == const.rewardIneligibleReasonNotRightAmoutOfPlayers:
                    description = localization.GetByLabel('UI/Incursion/Journal/DisqualifiedNotEnoughParticipants')
                elif d.disqualifierType == const.rewardIneligibleReasonTaleAlreadyEnded:
                    description = localization.GetByLabel('UI/Incursion/Journal/DisqualifiedExpired')
            elif d.eventTypeID == logConst.eventRewardLPStoredInPool:
                description = localization.GetByLabel('UI/Incursion/Journal/LoyaltyPointPilotRewardCount', rewardedPlayers=d.numberOfPlayers)
            elif d.eventTypeID == logConst.eventRewardLPPoolPayedOut:
                description = localization.GetByLabel('UI/Incursion/Journal/LoyaltyPointPoolPaidOut')
            elif d.eventTypeID == logConst.eventRewardLPPoolLost:
                description = localization.GetByLabel('UI/Incursion/Journal/LoyaltyPointPoolLost')
            hint = description
            texts = [util.FmtSimpleDateUTC(d.date),
             solarSystemType,
             d.dungeonName,
             LPAmountAddedToPool,
             LPAmountPayedOut,
             description]
            scrolllist.append(listentry.Get('Generic', {'label': '<t>'.join(texts),
             'sort_' + localization.GetByLabel('UI/Incursion/Journal/StoredLP'): d.lpAmountAddedToPool,
             'sort_' + localization.GetByLabel('UI/Incursion/Journal/PaidLP'): d.lpAmountPayedOut,
             'hint': hint}))

        headers = [localization.GetByLabel('UI/Common/Date'),
         localization.GetByLabel('UI/Incursion/Journal/Type'),
         localization.GetByLabel('UI/Incursion/Journal/EncounterName'),
         localization.GetByLabel('UI/Incursion/Journal/StoredLP'),
         localization.GetByLabel('UI/Incursion/Journal/PaidLP'),
         localization.GetByLabel('UI/Incursion/Journal/Description')]
        options = [(localization.GetByLabel('UI/Incursion/Journal/AllIncursionsFilter'), None)]
        for taleID, constellationName in taleIDs.iteritems():
            options.append((constellationName, taleID))

        self.sr.incursionLPTaleIDFilter.LoadOptions(options)
        if selectedTaleID is None:
            self.sr.incursionLPTaleIDFilter.SelectItemByValue(taleIDFilter)
        else:
            self.sr.incursionLPTaleIDFilter.SelectItemByValue(selectedTaleID)
        options = [(localization.GetByLabel('UI/Incursion/Journal/AllTypesFilter'), None), (localization.GetByLabel('UI/Incursion/Journal/CompletedAndNotPaidOut'), LPTypeFilter.LPLost), (localization.GetByLabel('UI/Incursion/Journal/CompletedAndPaidOut'), LPTypeFilter.LPPayedOut)]
        for dungeonType in dungeonTypes:
            if dungeonType is not None and dungeonType != '':
                if isinstance(dungeonType, int):
                    options.append((localization.GetByMessageID(dungeonType), dungeonType))
                else:
                    options.append((localization.GetByLabel(dungeonType), dungeonType))

        self.sr.incursionLPTypeFilter.LoadOptions(options)
        self.sr.incursionLPTypeFilter.SelectItemByValue(solarsystemTypeFilter)
        if scrolllist:
            sortBy = self.sr.scroll.GetSortBy()
            sortDirection = self.sr.scroll.GetSortDirection()
            self.sr.scroll.LoadContent(contentList=scrolllist, reversesort=1, headers=headers, scrollTo=0.0)
            if sortBy is None:
                self.sr.scroll.Sort(by=localization.GetByLabel('UI/Common/Date'), reversesort=1)
            else:
                self.sr.scroll.Sort(by=sortBy, reversesort=sortDirection)
        else:
            self.sr.scroll.Clear()
            self.sr.scroll.ShowHint(localization.GetByLabel('UI/Incursion/Journal/NoRecordFound'))
        return

    def FetchContracts(self, *args):
        status = self.statusCombo.GetValue()
        forCorp = self.ownerCombo.GetValue() > 0
        self.contractFilters['status'] = status
        self.contractFilters['forCorp'] = forCorp
        self.DoShowContracts()

    def DoShowContracts(self):
        self.ShowLoad()
        try:
            sm.GetService('neocom').BlinkOff('contracts')
            forCorp = self.contractFilters.get('forCorp', False)
            status = int(self.contractFilters.get('status', 0))
            numRequiresAttention = numCorpRequiresAttention = 0
            l = sm.GetService('contracts').GetMyExpiredContractList()
            expiredContracts = l.mySelf
            expiredCorpContracts = l.myCorp
            numRequiresAttention = len(expiredContracts.contracts)
            if eve.session.corprole & const.corpRoleContractManager == const.corpRoleContractManager:
                numCorpRequiresAttention = len(expiredCorpContracts.contracts)
            if status == 0:
                _contracts = expiredCorpContracts if forCorp else expiredContracts
            elif status == 3:
                _contracts = sm.GetService('contracts').GetMyBids(forCorp).list
            else:
                _contracts = sm.GetService('contracts').GetMyCurrentContractList(status == 2, forCorp).list
            if not _contracts:
                self.sr.contractsListWnd.Load(contentList=[], headers=[], noContentHint=localization.GetByLabel('UI/Journal/JournalWindow/Contracts/NoContractsFound'))
            contracts = _contracts.contracts
            ownerIDs = {}
            for r in contracts:
                ownerIDs[r.issuerID] = 1
                ownerIDs[r.issuerCorpID] = 1
                ownerIDs[r.acceptorID] = 1
                ownerIDs[r.assigneeID] = 1

            cfg.eveowners.Prime(ownerIDs.keys())
            scrolllist = []
            for c in contracts:
                blue.pyos.BeNice(50)
                canGetItems = False
                canGetMoney = False
                isOutbid = False
                if status == 0:
                    st = '<color=0xff885500>unknown'
                    if c.status == const.conStatusRejected:
                        st = '<color=0xff885500>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/Rejected')
                    elif c.type == const.conTypeAuction:
                        bids = _contracts.bids.get(c.contractID, [])
                        if c.status in [const.conStatusOutstanding, const.conStatusFinishedContractor, const.conStatusFinishedIssuer] and c.dateExpired < blue.os.GetWallclockTime():
                            if len(bids) > 0:
                                highBidder = bids[0].bidderID
                                if highBidder == eve.session.charid:
                                    st = '<color=green>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/YouWon')
                                    if forCorp:
                                        isOutbid = True
                                    elif c.status in [const.conStatusOutstanding, const.conStatusFinishedIssuer]:
                                        canGetItems = True
                                        st = '<color=green>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/YouWonGetItems')
                                elif highBidder == eve.session.corpid:
                                    st = '<color=green>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CorpWon')
                                    if not forCorp:
                                        isOutbid = True
                                    elif c.status in [const.conStatusOutstanding, const.conStatusFinishedIssuer]:
                                        canGetItems = True
                                        st = '<color=green>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CorpWonGetItems')
                                elif not forCorp and c.issuerID == eve.session.charid or forCorp and c.issuerCorpID == eve.session.corpid and c.forCorp:
                                    if c.status in [const.conStatusOutstanding, const.conStatusFinishedContractor]:
                                        st = '<color=white>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/FinishedGetMoney')
                                        canGetMoney = True
                                    else:
                                        st = '<color=white>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/AuctionFinished')
                                else:
                                    st = '<color=red>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/AuctionFinished')
                                    isOutbid = True
                            else:
                                st = '<color=red>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/Expired')
                        elif c.dateExpired > blue.os.GetWallclockTime():
                            if len(bids) > 0:
                                for i in range(len(bids)):
                                    b = bids[i]
                                    if (b.bidderID == eve.session.charid or b.bidderID == eve.session.corpid) and i != 0:
                                        st = '<color=red>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/Outbid')
                                        isOutbid = True
                                        break

                    elif c.status == const.conStatusOutstanding and c.dateExpired < blue.os.GetWallclockTime():
                        st = '<color=red>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/Expired')
                    elif c.status == const.conStatusInProgress and c.dateAccepted + const.DAY * c.numDays < blue.os.GetWallclockTime():
                        st = '<color=red>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/Overdue')
                    elif c.status == const.conStatusInProgress:
                        color = 'white'
                        if c.dateAccepted + const.DAY * c.numDays < blue.os.GetWallclockTime() + 6 * const.HOUR:
                            color = '0xffdd5500'
                        timeRemaining = c.dateAccepted + const.DAY * c.numDays - blue.os.GetWallclockTime()
                        st = '<color={color}>'.format(color=color) + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/TimeRemaining', time=timeRemaining)
                    elif c.type == const.conTypeCourier:
                        st = '<color=0xffdd5500>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CourierNeedsAttention')
                    additionalColumns = '<t>%s' % st
                elif status == 3:
                    st = '<color=0xff885500>unknown'
                    bids = _contracts.bids.get(c.contractID, [])
                    if c.status in [const.conStatusOutstanding, const.conStatusFinishedContractor, const.conStatusFinishedIssuer] and c.dateExpired < blue.os.GetWallclockTime():
                        if len(bids) > 0:
                            highBidder = bids[0].bidderID
                            if highBidder == eve.session.charid:
                                st = '<color=green>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/YouWon')
                            elif highBidder == eve.session.corpid:
                                st = '<color=green>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CorpWon')
                            else:
                                st = '<color=white>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/AuctionFinished')
                        else:
                            st = '<color=red>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/Expired')
                    elif c.dateExpired > blue.os.GetWallclockTime():
                        if len(bids) > 0:
                            for i in range(len(bids)):
                                b = bids[i]
                                if (b.bidderID == eve.session.charid or b.bidderID == eve.session.corpid) and i == 0:
                                    if eve.session.charid == b.bidderID:
                                        st = '<color=green>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/HighestBidder')
                                    elif eve.session.corpid == b.bidderID:
                                        st = '<color=green>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CorpHighestBidder')
                                    break
                                elif (b.bidderID == eve.session.charid or b.bidderID == eve.session.corpid) and i != 0:
                                    st = '<color=red>' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/Outbid')
                                    break

                    additionalColumns = '<t>%s' % st
                else:
                    additionalColumns = '<t>' + '<t>'.join([GetColoredContractStatusText(c.status), util.FmtDate(c.dateAccepted, 'ss'), ConFmtDate(c.dateAccepted + const.DAY * c.numDays - blue.os.GetWallclockTime(), c.type == const.conTypeAuction)])
                text = '.'
                canDismiss = False
                if status == 0 and c.type == const.conTypeAuction and isOutbid:
                    canDismiss = True
                data = {'contract': c,
                 'contractItems': _contracts.items.get(c.contractID, []),
                 'text': text,
                 'label': text,
                 'additionalColumns': additionalColumns,
                 'status': const.conStatusInProgress,
                 'callback': self.OnSelectContract,
                 'forCorp': forCorp,
                 'canDismiss': canDismiss,
                 'canGetMoney': canGetMoney,
                 'canGetItems': canGetItems,
                 'canIgnore': False,
                 'sort_' + localization.GetByLabel('UI/Journal/JournalWindow/Contracts/HeaderContract'): GetContractTitle(c, _contracts.items.get(c.contractID, []))}
                scrolllist.append(listentry.Get('ContractEntrySmall', data))

            self.sr.contractsListWnd.sr.id = 'contractsscroll'
            headers = [localization.GetByLabel('UI/Journal/JournalWindow/Contracts/HeaderContract'),
             localization.GetByLabel('UI/Journal/JournalWindow/Contracts/HeaderType'),
             localization.GetByLabel('UI/Journal/JournalWindow/Contracts/HeaderFrom'),
             localization.GetByLabel('UI/Journal/JournalWindow/Contracts/HeaderTo'),
             localization.GetByLabel('UI/Journal/JournalWindow/Contracts/HeaderStatus')]
            if status > 0 and status < 3:
                headers.extend([localization.GetByLabel('UI/Journal/JournalWindow/Contracts/HeaderIssued'), localization.GetByLabel('UI/Journal/JournalWindow/Contracts/HeaderTimeLeft')])
            self.sr.contractsListWnd.Load(contentList=scrolllist, headers=headers, noContentHint=localization.GetByLabel('UI/Journal/JournalWindow/Contracts/NoContractsFound'))
            self.statusCombo.SetValue(self.contractFilters.get('status', 0))
            self.ownerCombo.SetValue(self.contractFilters.get('forCorp', False))
            uix.Flush(self.contractsNotifyWnd)
            if numRequiresAttention > 0 or numCorpRequiresAttention > 0:
                icon = uicontrols.Icon(icon='res:/ui/Texture/WindowIcons/warning.png', parent=self.contractsNotifyWnd, left=5, size=24, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED)
                pos = icon.left + icon.width + 2
                if numRequiresAttention > 0:
                    if numRequiresAttention == 1:
                        msg = localization.GetByLabel('UI/Journal/JournalWindow/Contracts/OneRequiresAttention')
                    elif numRequiresAttention >= 100:
                        numRequiresAttention = 100
                        msg = localization.GetByLabel('UI/Journal/JournalWindow/Contracts/MoreThan100RequireAttention', quantity=numRequiresAttention)
                    else:
                        msg = localization.GetByLabel('UI/Journal/JournalWindow/Contracts/ManyRequireAttention', quantity=numRequiresAttention)
                    title = uicontrols.EveLabelMedium(text='<color=white>' + msg + '</color>', parent=self.contractsNotifyWnd, top=6, idx=0, left=pos, state=uiconst.UI_NORMAL)
                    title.forCorp = False
                    title.OnClick = self.ShowContracts
                    title.OnMouseEnter = (self.MouseEnterHighlightOn, title)
                    title.OnMouseExit = (self.MouseExitHighlightOff, title)
                    pos += title.width + 5
                if numCorpRequiresAttention > 0:
                    if numRequiresAttention > 0:
                        if numCorpRequiresAttention == 1:
                            msg = localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CorpAndPersonalOneRequiresAttention')
                        elif numCorpRequiresAttention >= 100:
                            numCorpRequiresAttention = 100
                            msg = localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CorpAndPersonalMoreThan100RequireAttention', quantity=numCorpRequiresAttention)
                        else:
                            msg = localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CorpAndPersonalManyRequireAttention', quantity=numCorpRequiresAttention)
                    elif numCorpRequiresAttention == 1:
                        msg = localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CorpOneRequiresAttention')
                    elif numCorpRequiresAttention >= 100:
                        numCorpRequiresAttention = 100
                        msg = localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CorpMoreThan100RequireAttention', quantity=numCorpRequiresAttention)
                    else:
                        msg = localization.GetByLabel('UI/Journal/JournalWindow/Contracts/CorpManyRequireAttention', quantity=numCorpRequiresAttention)
                    title = uicontrols.EveLabelMedium(text='<color=white>' + msg + '</color>', parent=self.contractsNotifyWnd, top=6, idx=0, left=pos, state=uiconst.UI_NORMAL)
                    title.forCorp = True
                    title.OnClick = self.ShowContracts
                    title.OnMouseEnter = (self.MouseEnterHighlightOn, title)
                    title.OnMouseExit = (self.MouseExitHighlightOff, title)
        finally:
            self._SelectTab(self.sr.maintabs.sr.Get(localization.GetByLabel('UI/Journal/JournalWindow/ContractsTab') + '_tab'))
            self.HideLoad()

    def MouseExitHighlightOff(self, obj, *args):
        obj.color.SetRGB(1.0, 1.0, 1.0)

    def MouseEnterHighlightOn(self, obj, *args):
        obj.color.SetRGB(1.0, 1.0, 0.0)

    def OnComboChange(self, *args):
        pass

    def OnSelectContract(self, entry, *args):
        pass

    def ShowContracts(self, *args):
        forCorp = False
        status = 0
        if len(args) > 0:
            forCorp = args[0].forCorp
        if len(args) > 1:
            status = args[1]
        self.sr.maintabs.ShowPanelByName(localization.GetByLabel('UI/Journal/JournalWindow/ContractsTab'))
        self.contractFilters['status'] = status
        self.contractFilters['forCorp'] = forCorp
        uthread.new(self.DelayedShowContracts)

    def DelayedShowContracts(self):
        blue.pyos.synchro.SleepWallclock(300)
        self.DoShowContracts()

    def ProcessSessionChange(self, isremote, session, change):
        if getattr(self.sr, 'maintabs', None):
            self.sr.maintabs.ReloadVisible()
        return

    def OnAgentMissionChange(self, what, agentID, tutorialID=None):
        if getattr(self.sr, 'maintabs', None):
            self.sr.maintabs.ReloadVisible()
        return

    def OnLPChange(self, what):
        if getattr(self.sr, 'maintabs', None):
            self.sr.maintabs.ReloadVisible()
        return

    def OnDeleteContract(self, contractID, *args):
        listNodes = self.sr.contractsListWnd.GetNodes()
        for node in listNodes:
            if node.contract.contractID == contractID:
                self.sr.contractsListWnd.RemoveEntries([node])
                return