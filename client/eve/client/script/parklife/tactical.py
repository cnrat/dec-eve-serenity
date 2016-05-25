# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\tactical.py
import math
from math import sqrt
import dogma.effects
from dogma.const import falloffEffectivnessModuleGroups
from eve.client.script.parklife import tacticalConst
from eve.client.script.ui.camera.cameraUtil import IsNewCameraActive
import evecamera
import evetypes
import service
import uicontrols
import util
import blue
from eveDrones.droneDamageTracker import InBayDroneDamageTracker
import trinity
import geo2
import uix
import uiutil
import carbonui.const as uiconst
import uthread
import base
import states as state
import sys
import form
from collections import OrderedDict
import localization
import telemetry
import log
import tacticalOverlay
BRACKETBORDER = 17
OVERVIEW_CONFIGNAME = 0
OVERVIEW_GROUPDATA = 1
BRACKETS_CONFIGNAME = 2
BRACKETS_GROUPDATA = 3
INVISIBLE_TYPES = [const.typeUnlitModularEffectBeacon]

@util.Memoized
def GetCacheByLabel(key):
    return localization.GetByLabel(key)


class TacticalSvc(service.Service):
    __guid__ = 'svc.tactical'
    __update_on_reload__ = 0
    __notifyevents__ = ['DoBallsAdded',
     'DoBallRemove',
     'OnTacticalPresetChange',
     'OnStateChange',
     'OnStateSetupChange',
     'ProcessSessionChange',
     'OnSessionChanged',
     'OnSpecialFX',
     'ProcessOnUIAllianceRelationshipChanged',
     'ProcessRookieStateChange',
     'OnSetCorpStanding',
     'OnSetAllianceStanding',
     'OnSuspectsAndCriminalsUpdate',
     'OnSlimItemChange',
     'OnDroneStateChange2',
     'OnDroneControlLost',
     'OnItemChange',
     'OnBallparkCall',
     'OnEwarStart',
     'OnEwarEnd',
     'OnEwarOnConnect',
     'OnContactChange',
     'OnCrimewatchEngagementUpdated',
     'DoBallsRemove']
    __startupdependencies__ = ['settings']
    __dependencies__ = ['clientDogmaStaticSvc',
     'state',
     'bracket',
     'overviewPresetSvc']
    ALL_COLUMNS = OrderedDict([('ICON', 'UI/Generic/Icon'),
     ('DISTANCE', 'UI/Common/Distance'),
     ('NAME', 'UI/Common/Name'),
     ('TYPE', 'UI/Common/Type'),
     ('TAG', 'UI/Common/Tag'),
     ('CORPORATION', 'UI/Common/Corporation'),
     ('ALLIANCE', 'UI/Common/Alliance'),
     ('FACTION', 'UI/Common/Faction'),
     ('MILITIA', 'UI/Common/Militia'),
     ('SIZE', 'UI/Inventory/ItemSize'),
     ('VELOCITY', 'UI/Overview/Velocity'),
     ('RADIALVELOCITY', 'UI/Overview/RadialVelocity'),
     ('TRANSVERSALVELOCITY', 'UI/Overview/TraversalVelocity'),
     ('ANGULARVELOCITY', 'UI/Generic/AngularVelocity')])
    COLUMN_UNITS = {'VELOCITY': 'UI/Overview/MetersPerSecondUnitShort',
     'RADIALVELOCITY': 'UI/Overview/MetersPerSecondUnitShort',
     'TRANSVERSALVELOCITY': 'UI/Overview/MetersPerSecondUnitShort',
     'ANGULARVELOCITY': 'UI/Overview/RadiansPerSecondUnitShort'}

    def __init__(self):
        service.Service.__init__(self)

    def Run(self, *etc):
        service.Service.Run(self, *etc)
        self.tacticalOverlay = tacticalOverlay.TacticalOverlay(self)
        self.logme = 0
        self.jammers = {}
        self.jammersByJammingType = {}
        self.filterFuncs = None
        self.CleanUp()
        if not (eve.rookieState and eve.rookieState < 23):
            self.Setup()
        self.flagsAreDirty = False
        self.flagCheckingThread = uthread.new(self.FlagsDirtyCheckingLoop)
        self.inBayDroneDamageTracker = None
        return

    def Setup(self):
        self.CleanUp()
        self.AssureSetup()
        if util.InSpace():
            if self.IsTacticalOverlayActive():
                self.Init()
            self.Open()

    def Stop(self, *etc):
        service.Service.Stop(self, *etc)
        self.CleanUp()

    @telemetry.ZONE_METHOD
    def OnBallparkCall(self, eventName, argTuple):
        if self.sr is None:
            return
        else:
            if eventName == 'SetBallInteractive' and argTuple[1] == 1:
                bp = sm.GetService('michelle').GetBallpark()
                if not bp:
                    return
                slimItem = bp.GetInvItem(argTuple[0])
                if not slimItem:
                    return
                self.MarkFlagsAsDirty()
            return

    @telemetry.ZONE_METHOD
    def OnItemChange(self, item, change):
        if (const.ixFlag in change or const.ixLocationID in change) and item.flagID == const.flagDroneBay:
            droneview = self.GetPanel('droneview')
            if droneview:
                droneview.CheckDrones()
            else:
                self.CheckInitDrones()

    @telemetry.ZONE_METHOD
    def ProcessSessionChange(self, isRemote, session, change):
        doResetJammers = False
        if self.logme:
            self.LogInfo('Tactical::ProcessSessionChange', isRemote, session, change)
        if 'stationid' in change:
            doResetJammers = True
        if 'solarsystemid' in change:
            self.TearDownOverlay()
            doResetJammers = True
        if 'shipid' in change:
            for itemID in self.attackers:
                sm.GetService('state').SetState(itemID, state.threatAttackingMe, 0)

            self.attackers = {}
            overview = form.OverView.GetIfOpen()
            if overview:
                overview.FlushEwarStates()
            doResetJammers = True
            droneview = self.GetPanel('droneview')
            if droneview:
                if getattr(self, '_initingDrones', False):
                    self.LogInfo('Tactical: ProcessSessionChange: busy initing drones, cannot close the window')
                else:
                    droneview.Close()
        if doResetJammers:
            self.ResetJammers()

    def ResetJammers(self):
        self.jammers = {}
        self.jammersByJammingType = {}
        sm.ScatterEvent('OnEwarEndFromTactical', doAnimate=False)

    def RemoveBallFromJammers(self, ball, *args):
        ballID = ball.id
        effectsFromBall = self.jammers.get(ballID)
        if effectsFromBall is None:
            return
        else:
            doUpdate = False
            for effectName, effectSet in self.jammersByJammingType.iteritems():
                if effectName not in effectsFromBall:
                    continue
                tuplesToRemove = set()
                for effectTuple in effectSet:
                    effectBallID, moduleID = effectTuple
                    if effectBallID == ballID:
                        tuplesToRemove.add(effectTuple)

                if tuplesToRemove:
                    effectSet.difference_update(tuplesToRemove)
                    doUpdate = True

            self.jammers.pop(ballID, None)
            if doUpdate:
                sm.ScatterEvent('OnEwarEndFromTactical')
            return

    def OnSessionChanged(self, isRemote, session, change):
        if util.InSpace():
            self.AssureSetup()
            self.Open()
            if self.IsTacticalOverlayActive():
                self.Init()
            self.CheckInitDrones()
            self.MarkFlagsAsDirty()
            if 'shipid' in change:
                self.tacticalOverlay.OnShipChange()
        else:
            self.CleanUp()

    @telemetry.ZONE_METHOD
    def OnSlimItemChange(self, oldSlim, newSlim):
        if not util.InSpace():
            return
        else:
            update = 0
            if getattr(newSlim, 'allianceID', None) and newSlim.allianceID != getattr(oldSlim, 'allianceID', None):
                update = 1
            elif newSlim.corpID and newSlim.corpID != oldSlim.corpID:
                update = 2
            elif newSlim.charID != oldSlim.charID:
                update = 3
            elif newSlim.ownerID != oldSlim.ownerID:
                update = 4
            elif getattr(newSlim, 'lootRights', None) != getattr(oldSlim, 'lootRights', None):
                update = 5
            elif getattr(newSlim, 'isEmpty', None) != getattr(oldSlim, 'isEmpty', None):
                update = 6
            if update:
                self.MarkFlagsAsDirty()
            return

    def ProcessOnUIAllianceRelationshipChanged(self, *args):
        if self.InSpace():
            self.MarkFlagsAsDirty()

    def ProcessRookieStateChange(self, state):
        if util.InSpace():
            if not not (eve.rookieState and eve.rookieState < 23):
                self.CleanUp()
            elif not self.GetPanel(form.OverView.default_windowID):
                self.Setup()

    def OnContactChange(self, contactIDs, contactType=None):
        if util.InSpace():
            self.MarkFlagsAsDirty()

    def OnSetCorpStanding(self, *args):
        if util.InSpace():
            self.MarkFlagsAsDirty()

    def OnSetAllianceStanding(self, *args):
        if util.InSpace():
            self.MarkFlagsAsDirty()

    def OnCrimewatchEngagementUpdated(self, otherCharId, timeout):
        if util.InSpace():
            uthread.new(self.DelayedFlagStateUpdate)

    def OnSuspectsAndCriminalsUpdate(self, criminalizedCharIDs, decriminalizedCharIDs):
        if util.InSpace():
            uthread.new(self.DelayedFlagStateUpdate)

    def DelayedFlagStateUpdate(self):
        if getattr(self, 'delayedFlagStateUpdate', False):
            return
        setattr(self, 'delayedFlagStateUpdate', True)
        blue.pyos.synchro.SleepWallclock(1000)
        self.MarkFlagsAsDirty()
        setattr(self, 'delayedFlagStateUpdate', False)

    @telemetry.ZONE_METHOD
    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration=-1, repeat=None, startTime=None, timeFromStart=0, graphicInfo=None):
        if targetID == eve.session.shipid and isOffensive:
            attackerID = shipID
            attackTime = startTime
            attackRepeat = repeat
            shipItem = sm.StartService('michelle').GetItem(shipID)
            if shipItem and shipItem.categoryID == const.categoryStarbase:
                attackerID = moduleID
                attackTime = 0
                attackRepeat = 0
            data = self.attackers.get(attackerID, [])
            key = (moduleID,
             guid,
             attackTime,
             duration,
             attackRepeat)
            if start and shipID != session.shipid:
                if key not in data:
                    data.append(key)
                sm.GetService('state').SetState(attackerID, state.threatAttackingMe, 1)
            else:
                toRemove = None
                for signature in data:
                    if signature[0] == key[0] and signature[1] == key[1] and signature[2] == key[2] and signature[3] == key[3]:
                        toRemove = signature
                        break

                if toRemove is not None:
                    data.remove(toRemove)
                if not data:
                    sm.GetService('state').SetState(attackerID, state.threatAttackingMe, 0)
            self.attackers[attackerID] = data
        if start and guid == 'effects.WarpScramble':
            if settings.user.ui.Get('notifyMessagesEnabled', 1) or eve.session.shipid in (shipID, targetID):
                jammerName = sm.GetService('bracket').GetBracketName2(shipID)
                targetName = sm.GetService('bracket').GetBracketName2(targetID)
                if jammerName and targetName:
                    if eve.session.shipid == targetID:
                        sm.GetService('logger').AddCombatMessage('WarpScrambledBy', {'scrambler': jammerName})
                    elif eve.session.shipid == shipID:
                        sm.GetService('logger').AddCombatMessage('WarpScrambledSuccess', {'scrambled': targetName})
                    else:
                        sm.GetService('logger').AddCombatMessage('WarpScrambledOtherBy', {'scrambler': jammerName,
                         'scrambled': targetName})
        return

    def CheckInitDrones(self):
        mySlim = uix.GetBallparkRecord(eve.session.shipid)
        if not mySlim:
            return
        if mySlim.groupID == const.groupCapsule:
            return
        dronesInBay = sm.GetService('invCache').GetInventoryFromId(session.shipid).ListDroneBay()
        if dronesInBay:
            self.InitDrones()
        else:
            myDrones = sm.GetService('michelle').GetDrones()
            if myDrones:
                self.InitDrones()

    @telemetry.ZONE_METHOD
    def Open(self):
        self.InitSelectedItem()
        self.InitOverview()
        self.CheckInitDrones()

    def GetMain(self):
        if self and getattr(self.sr, 'mainParent', None):
            return self.sr.mainParent
        else:
            return

    def OnStateChange(self, itemID, flag, true, *args):
        uthread.new(self._OnStateChange, itemID, flag, true, *args)

    def _OnStateChange(self, itemID, flag, true, *args):
        if not util.InSpace():
            return
        elif not self or getattr(self, 'sr', None) is None:
            return
        else:
            if self.logme:
                self.LogInfo('Tactical::OnStateChange', itemID, flag, true, *args)
            if not getattr(self, 'inited', 0):
                return
            if flag == state.selected and true:
                self.ShowDirectionTo(itemID)
            if self.tacticalOverlay and self.tacticalOverlay.useNewOverlay:
                self.tacticalOverlay.CheckInterest(itemID, flag, true)
            return

    def OnTacticalPresetChange(self, label, set):
        if self.inited:
            uthread.new(self.InitConnectors).context = 'tactical::OnTacticalPresetChange-->InitConnectors'

    def OnStateSetupChange(self, what):
        self.MarkFlagsAsDirty()
        if self.inited:
            self.InitConnectors()

    def Toggle(self):
        pass

    def BlinkHeader(self, key):
        if not self or self.sr is None:
            return
        else:
            panel = getattr(self.sr, key.lower(), None)
            if panel:
                panel.Blink()
            return

    def IsExpanded(self, key):
        panel = getattr(self.sr, key.lower(), None)
        if panel:
            return panel.sr.main.state == uiconst.UI_PICKCHILDREN
        else:
            return

    def AssureSetup(self):
        if self.logme:
            self.LogInfo('Tactical::AssureSetup')
        if getattr(self, 'setupAssured', None):
            return
        else:
            if getattr(self, 'sr', None) is None:
                self.sr = uiutil.Bunch()
            self.setupAssured = 1
            return

    def CleanUp(self):
        if self.logme:
            self.LogInfo('Tactical::CleanUp')
        self.sr = None
        self.numberShader = None
        self.planeShader = None
        self.circleShader = None
        self.lines = None
        self.targetingRanges = None
        self.updateDirectionTimer = None
        self.genericUpdateTimer = None
        self.toggling = 0
        self.setupAssured = 0
        self.lastFactor = None
        self.groupList = None
        self.groupIDs = []
        self.direction = None
        self.direction2 = None
        self.intersections = []
        self.threats = {}
        self.attackers = {}
        self.maxConnectorDist = 150000.0
        self.TearDownOverlay()
        uicore.layer.tactical.Flush()
        self.dronesInited = 0
        self.busy = 0
        return

    def GetFilterFuncs(self):
        if self.filterFuncs is None:
            stateSvc = sm.GetService('state')
            self.filterFuncs = {'Criminal': stateSvc.CheckCriminal,
             'Suspect': stateSvc.CheckSuspect,
             'Outlaw': stateSvc.CheckOutlaw,
             'Dangerous': stateSvc.CheckDangerous,
             'StandingHigh': stateSvc.CheckStandingHigh,
             'StandingGood': stateSvc.CheckStandingGood,
             'StandingNeutral': stateSvc.CheckStandingNeutral,
             'StandingBad': stateSvc.CheckStandingBad,
             'StandingHorrible': stateSvc.CheckStandingHorrible,
             'NoStanding': stateSvc.CheckNoStanding,
             'SameFleet': stateSvc.CheckSameFleet,
             'SameCorp': stateSvc.CheckSameCorp,
             'SameAlliance': stateSvc.CheckSameAlliance,
             'SameMilitia': stateSvc.CheckSameMilitia,
             'AtWarCanFight': stateSvc.CheckAtWarCanFight,
             'AtWarMilitia': stateSvc.CheckAtWarMilitia,
             'IsWanted': stateSvc.CheckIsWanted,
             'HasKillRight': stateSvc.CheckHasKillRight,
             'WreckViewed': stateSvc.CheckWreckViewed,
             'WreckEmpty': stateSvc.CheckWreckEmpty,
             'LimitedEngagement': stateSvc.CheckLimitedEngagement,
             'AlliesAtWar': stateSvc.CheckAlliesAtWar,
             'AgentInteractable': stateSvc.CheckAgentInteractable}
        return self.filterFuncs

    def CheckFiltered(self, slimItem, filtered, alwaysShow):
        stateSvc = sm.GetService('state')
        if len(filtered) + len(alwaysShow) > 3:
            ownerID = slimItem.ownerID
            if ownerID is None or ownerID == const.ownerSystem or util.IsNPC(ownerID):
                checkArgs = (slimItem, None)
            else:
                checkArgs = (slimItem, stateSvc._GetRelationship(slimItem))
        else:
            checkArgs = (slimItem,)
        functionDict = self.GetFilterFuncs()
        for functionName in alwaysShow:
            f = functionDict.get(functionName, None)
            if f is None:
                self.LogError('CheckFiltered got bad functionName: %r' % functionName)
                continue
            if f(*checkArgs):
                return False

        for functionName in filtered:
            f = functionDict.get(functionName, None)
            if f is None:
                self.LogError('CheckFiltered got bad functionName: %r' % functionName)
                continue
            if f(*checkArgs):
                return True

        return False

    def RefreshOverview(self):
        overview = form.OverView.GetIfOpen()
        if overview:
            overview.FullReload()

    def UpdateStates(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateStates, call UpdateFlagAndBackground on the uiwindow instead'

    def UpdateBackground(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateBackground, call on the uiwindow instead'

    def UpdateIcon(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateIcon, call UpdateIconColor on the uiwindow instead'

    def UpdateFlag(self, slimItem, uiwindow):
        print 'Deprecated, TacticalSvc.UpdateFlag, call on the uiwindow instead'

    def GetFlagUI(self, parent):
        print 'Deprecated, TacticalSvc.GetFlagUI, make the icon yourself'

    def UpdateFlagPositions(self, uiwindow, icon=None):
        print 'Deprecated, TacticalSvc.UpdateFlagPositions, call on the uiwindow instead'

    def MarkFlagsAsDirty(self):
        self.flagsAreDirty = True

    @telemetry.ZONE_METHOD
    def FlagsDirtyCheckingLoop(self):
        while self.state == service.SERVICE_RUNNING:
            try:
                if self.flagsAreDirty:
                    self.flagsAreDirty = False
                    self.InvalidateFlags()
            except Exception:
                log.LogException(extraText='Error invalidating tactical flags')
                sys.exc_clear()

            blue.pyos.synchro.SleepWallclock(500)

    def InvalidateFlags(self):
        if not util.InSpace():
            return
        overview = form.OverView.GetIfOpen()
        if overview:
            overview.UpdateAllIconAndBackgroundFlags()
        sm.GetService('bracket').RenewFlags()

    def InvalidateFlagsExtraLimited(self, charID):
        if util.InSpace():
            sm.GetService('bracket').RenewSingleFlag(charID)

    def ShowDirectionTo(self, itemID):
        if self.tacticalOverlay.useNewOverlay:
            self.tacticalOverlay.ShowDirectionTo(itemID)
            return
        else:
            if self.logme:
                self.LogInfo('Tactical::ShowDirectionTo', itemID)
            if self.direction is None:
                return
            scene = sm.GetService('sceneManager').GetRegisteredScene('default')
            self.direction.display = False
            if self.directionCurveSet is not None:
                self.usedCurveSets.remove(self.directionCurveSet)
                scene.curveSets.remove(self.directionCurveSet)
                self.directionCurveSet = None
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark is None:
                return
            ball = ballpark.GetBall(itemID)
            if ball is None or getattr(ball, 'model', None) is None or ball.IsCloaked():
                return
            meball = ballpark.GetBall(eve.session.shipid)
            if not meball or not meball.model:
                return
            distVec = geo2.Vector(ball.x - meball.x, ball.y - meball.y, ball.z - meball.z)
            if geo2.Vec3Length(distVec) >= 200000.0:
                return
            set = trinity.TriCurveSet()
            vs = trinity.TriVectorSequencer()
            vc = trinity.TriVectorCurve()
            vc.value = (1.0, 1.0, 1.0)
            vs.functions.append(ball)
            vs.functions.append(vc)
            bind = trinity.TriValueBinding()
            bind.destinationObject = self.direction
            bind.destinationAttribute = 'scaling'
            bind.sourceObject = vs
            bind.sourceAttribute = 'value'
            set.curves.append(vs)
            set.curves.append(vc)
            set.bindings.append(bind)
            set.name = str(ball.id) + '_direction'
            set.Play()
            scene.curveSets.append(set)
            self.usedCurveSets.append(set)
            self.directionCurveSet = set
            self.direction.display = True
            self.UpdateDirection()
            return

    def UpdateDirection(self):
        if self.logme:
            self.LogInfo('Tactical::UpdateDirection')
        if self.direction is None or not self.direction.display:
            return
        else:
            scene = sm.GetService('sceneManager').GetRegisteredScene('default')
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark is None:
                return
            ball = ballpark.GetBall(sm.GetService('state').GetExclState(state.selected))
            if ball is None:
                return
            meball = ballpark.GetBall(eve.session.shipid)
            if not meball:
                return
            distVec = geo2.Vector(ball.x - meball.x, ball.y - meball.y, ball.z - meball.z)
            if ball.IsCloaked() or geo2.Vec3Length(distVec) > 200000.0:
                self.updateDirectionTimer = None
                self.direction.display = False
                if self.directionCurveSet is not None:
                    self.usedCurveSets.remove(self.directionCurveSet)
                    scene.curveSets.remove(self.directionCurveSet)
                    self.directionCurveSet = None
                    return
            if self.updateDirectionTimer is None:
                self.updateDirectionTimer = base.AutoTimer(111, self.UpdateDirection)
            return

    def GetAllColumns(self):
        return self.ALL_COLUMNS.keys()

    def GetColumnLabel(self, columnID, addFormatUnit=False):
        localizedID = self.ALL_COLUMNS.get(columnID, None)
        if localizedID:
            retString = localization.GetByLabel(localizedID)
            if addFormatUnit:
                unitLabelID = self.COLUMN_UNITS.get(columnID, None)
                if unitLabelID:
                    retString = '%s (%s)' % (retString, localization.GetByLabel(unitLabelID))
            return retString
        else:
            return columnID

    def GetColumns(self):
        default = self.GetDefaultVisibleColumns()
        userSet = settings.user.overview.Get('overviewColumns', None)
        if userSet is None:
            userSet = default
        userSetOrder = self.GetColumnOrder()
        return [ label for label in userSetOrder if label in userSet ]

    def GetColumnOrder(self):
        ret = settings.user.overview.Get('overviewColumnOrder', None)
        if ret is None:
            return self.GetAllColumns()
        else:
            return ret

    def GetDefaultVisibleColumns(self):
        default = ['ICON',
         'DISTANCE',
         'NAME',
         'TYPE']
        return default

    def GetNotSavedTranslations(self):
        ret = [u'Not saved', u'Nicht gespeichert', u'\u672a\u30bb\u30fc\u30d6']
        return ret

    def SetNPCGroups(self):
        sendGroupIDs = []
        userSettings = self.overviewPresetSvc.GetGroups()
        for cat, groupdict in util.GetNPCGroups().iteritems():
            for groupname, groupids in groupdict.iteritems():
                for groupid in groupids:
                    if groupid in userSettings:
                        sendGroupIDs += groupids
                        break

        if sendGroupIDs:
            changeList = [('groups', sendGroupIDs, 1)]
            self.overviewPresetSvc.ChangeSettings(changeList=changeList)

    def GetFilteredStatesFunctionNames(self, isBracket=False):
        return [ sm.GetService('state').GetStateProps(flag).label for flag in self.overviewPresetSvc.GetFilteredStates(isBracket=isBracket) ]

    def GetAlwaysShownStatesFunctionNames(self, isBracket=False):
        return [ sm.GetService('state').GetStateProps(flag).label for flag in self.overviewPresetSvc.GetAlwaysShownStates(isBracket=isBracket) ]

    def Get(self, what, default):
        if self.logme:
            self.LogInfo('Tactical::Get', what, default)
        return getattr(self, what, default)

    def OpenSettings(self, *args):
        uicore.cmd.OpenOverviewSettings()

    def ToggleOnOff(self):
        current = self.IsTacticalOverlayActive()
        if not current:
            self.ShowTacticalOverlay()
        elif self.inited:
            self.HideTacticalOverlay()

    def HideTacticalOverlay(self):
        self._SetTacticalOverlayActive(False)
        self.TearDownOverlay()
        sm.ScatterEvent('OnTacticalOverlayChange')

    def _SetTacticalOverlayActive(self, isActive):
        if IsNewCameraActive():
            cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
            if cam.cameraID == evecamera.CAM_TACTICAL:
                settings.user.overview.Set('viewTactical_camTactical', isActive)
            elif cam.cameraID == evecamera.CAM_SHIPORBIT:
                settings.user.overview.Set('viewTactical', isActive)
        else:
            settings.user.overview.Set('viewTactical', isActive)

    def ShowTacticalOverlay(self):
        if not self.IsTacticalOverlayAllowed():
            return
        self._SetTacticalOverlayActive(True)
        self.Init()
        sm.ScatterEvent('OnTacticalOverlayChange')

    def IsTacticalOverlayAllowed(self):
        cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
        if cam.cameraID == evecamera.CAM_SHIPPOV:
            return False
        return True

    def IsTacticalOverlayActive(self):
        if IsNewCameraActive():
            cam = sm.GetService('sceneManager').GetActiveSpaceCamera()
            if cam.cameraID == evecamera.CAM_TACTICAL:
                return settings.user.overview.Get('viewTactical_camTactical', True)
            elif cam.cameraID == evecamera.CAM_SHIPPOV:
                return False
            else:
                return settings.user.overview.Get('viewTactical', False)
        else:
            return settings.user.overview.Get('viewTactical', False)

    def CheckInit(self):
        if util.InSpace() and self.IsTacticalOverlayActive():
            self.Init()

    def ToggleNewTacticalOverlay(self, enable):
        inited = self.inited
        if inited:
            self.ToggleOnOff()
        self.tacticalOverlay.useNewOverlay = enable
        if inited:
            self.ToggleOnOff()

    def TearDownOverlay(self):
        if self.tacticalOverlay.useNewOverlay:
            if self.targetingRanges:
                self.targetingRanges.KillTimer()
            self.tacticalOverlay.TearDown()
            self.inited = False
            return
        else:
            connectors = getattr(self, 'connectors', None)
            if connectors:
                del connectors.children[:]
            self.connectors = None
            self.TargetingRange = None
            self.OptimalRange = None
            self.FalloffRange = None
            self.OffsetRange = None
            self.direction = None
            self.directionCurveSet = None
            self.updateDirectionTimer = None
            self.circles = None
            arena = getattr(self, 'arena', None)
            self.arena = None
            self.inited = False
            scene = sm.GetService('sceneManager').GetRegisteredScene('default')
            if scene and arena and arena in scene.objects:
                scene.objects.remove(arena)
                scene.objects.remove(self.rootTransform)
            usedCurves = getattr(self, 'usedCurveSets', None)
            if scene is not None and usedCurves is not None:
                for cs in self.usedCurveSets:
                    scene.curveSets.remove(cs)

            self.usedCurveSets = []
            return

    def AddCircleToLineSet(self, set, radius, color):
        tessSteps = int(math.sqrt(radius))
        for t in range(0, tessSteps):
            alpha0 = 2.0 * math.pi * float(t) / tessSteps
            alpha1 = 2.0 * math.pi * float(t + 1) / tessSteps
            x0 = radius * math.cos(alpha0)
            y0 = radius * math.sin(alpha0)
            x1 = radius * math.cos(alpha1)
            y1 = radius * math.sin(alpha1)
            set.AddLine((x0, 0.0, y0), color, (x1, 0.0, y1), color)

    def InitDistanceCircles(self):
        if self.circles is None:
            return
        else:
            self.circles.ClearLines()
            colorDark = (50.0 / 255.0,
             50.0 / 255.0,
             50.0 / 255.0,
             255.0 / 255.0)
            colorBright = (150.0 / 255.0,
             150.0 / 255.0,
             150.0 / 255.0,
             255.0 / 255.0)
            self.AddCircleToLineSet(self.circles, 5000.0, colorDark)
            self.AddCircleToLineSet(self.circles, 10000.0, colorDark)
            self.AddCircleToLineSet(self.circles, 20000.0, colorDark)
            self.AddCircleToLineSet(self.circles, 30000.0, colorDark)
            self.AddCircleToLineSet(self.circles, 40000.0, colorDark)
            self.AddCircleToLineSet(self.circles, 50000.0, colorBright)
            self.AddCircleToLineSet(self.circles, 75000.0, colorDark)
            self.AddCircleToLineSet(self.circles, 100000.0, colorBright)
            self.AddCircleToLineSet(self.circles, 150000.0, colorDark)
            self.AddCircleToLineSet(self.circles, 200000.0, colorDark)
            self.circles.SubmitChanges()
            return

    def InitDirectionLines(self):
        if self.direction is None:
            return
        else:
            self.direction.ClearLines()
            color = (0.2, 0.2, 0.2, 1.0)
            self.direction.AddLine((0.0, 0.0, 0.0), color, (1.0, 1.0, 1.0), color)
            self.direction.display = False
            self.direction.SubmitChanges()
            return

    def Init(self):
        if self.tacticalOverlay.useNewOverlay:
            self.tacticalOverlay.Initialize()
            self.inited = True
            return
        else:
            if self.logme:
                self.LogInfo('Tactical::Init')
            if not self.inited:
                rm = []
                scene = sm.GetService('sceneManager').GetRegisteredScene('default')
                if scene is None:
                    return
                for each in scene.objects:
                    if getattr(each, 'name', None) == 'TacticalMap':
                        rm.append(each)

                for each in rm:
                    scene.objects.remove(each)

                self.arena = trinity.Load('res:/UI/Inflight/tactical/TacticalMap.red')
                self.arena.name = 'TacticalMap'
                self.usedCurveSets = []
                self.directionCurveSet = None
                self.updateDirectionTimer = None
                ball = sm.GetService('michelle').GetBall(session.shipid)
                if not ball:
                    return
                for child in self.arena.children:
                    if child.name == 'connectors':
                        self.connectors = child
                    elif child.name == 'TargetingRange':
                        self.TargetingRange = child
                    elif child.name == 'OptimalRange':
                        self.OptimalRange = child
                    elif child.name == 'OffsetRange':
                        self.OffsetRange = child
                    elif child.name == 'FalloffRange':
                        self.FalloffRange = child
                    elif child.name == 'circleLineSet':
                        self.circles = child
                    elif child.name == 'directionLineSet':
                        self.direction = child

                self.rootTransform = trinity.EveRootTransform()
                self.rootTransform.children.append(self.OffsetRange)
                self.arena.children.remove(self.OffsetRange)
                self.InitDistanceCircles()
                self.InitDirectionLines()
                scene.objects.append(self.arena)
                scene.objects.append(self.rootTransform)
                self.inited = True
                self.InitConnectors()
                self.UpdateTargetingRanges()
            return

    def GetOverlay(self, curve=None):
        return self.tacticalOverlay

    def UpdateTargetingRanges(self, module=None, charge=None):
        if self.tacticalOverlay.useNewOverlay:
            self.tacticalOverlay.UpdateTargetingRanges(module, charge)
            return
        elif not self or not self.inited or self.TargetingRange is None:
            self.targetingRanges = None
            return
        else:
            self.targetingRanges = None
            self.intersections = []
            if not eve.session.shipid:
                self.FalloffRange.display = False
                self.OptimalRange.display = False
                self.OffsetRange.display = False
                self.rootTransform.translationCurve = self.rootTransform.rotationCurve = None
                self.TargetingRange.display = False
                self.UpdateDirection()
                return
            ship = sm.GetService('godma').GetItem(eve.session.shipid)
            maxTargetRange = ship.maxTargetRange * 2
            self.TargetingRange.display = True
            self.TargetingRange.scaling = (maxTargetRange, maxTargetRange, maxTargetRange)
            self.OffsetRange.translation = (0.0, 0.0, 0.0)
            self.OffsetRange.display = False
            self.intersections = [ship.maxTargetRange]
            if module is None:
                self.FalloffRange.display = False
                self.OptimalRange.display = False
            else:
                maxRange, falloffDist, bombRadius = self.FindMaxRange(module, charge)
                if falloffDist > 1.0:
                    falloff = (maxRange + falloffDist) * 2
                    self.FalloffRange.scaling = (falloff, falloff, falloff)
                    self.FalloffRange.display = True
                else:
                    self.FalloffRange.display = False
                optimal = 0
                if bombRadius:
                    aoeRad = bombRadius * 2
                    ball = sm.GetService('michelle').GetBall(session.shipid)
                    if ball:
                        self.rootTransform.translationCurve = self.rootTransform.rotationCurve = ball
                        self.OffsetRange.translation = (0, 0, maxRange)
                        self.OffsetRange.scaling = (aoeRad, aoeRad, aoeRad)
                        self.OffsetRange.display = True
                else:
                    optimal = maxRange * 2
                if optimal:
                    self.OptimalRange.scaling = (optimal, optimal, optimal)
                    self.OptimalRange.display = True
                self.intersections += [module.maxRange, module.maxRange + module.falloff]
            self.UpdateDirection()
            return

    def FindMaxRange(self, module, charge, dogmaLocation=None, *args):
        maxRange = 0
        falloffDist = 0
        bombRadius = 0
        if not dogmaLocation:
            dogmaLocation = sm.GetService('clientDogmaIM').GetDogmaLocation()
        try:
            effectID = self.clientDogmaStaticSvc.GetDefaultEffect(module.typeID)
        except KeyError:
            pass
        else:
            effect = self.clientDogmaStaticSvc.GetEffect(effectID)
            if effect.rangeAttributeID is not None:
                attributeName = cfg.dgmattribs.Get(effect.rangeAttributeID).attributeName
                maxRange = dogmaLocation.GetAccurateAttributeValue(module.itemID, effect.rangeAttributeID)
                if module.groupID in falloffEffectivnessModuleGroups:
                    falloffDist = dogmaLocation.GetAccurateAttributeValue(module.itemID, const.attributeFalloffEffectiveness)
                else:
                    falloffDist = dogmaLocation.GetAccurateAttributeValue(module.itemID, const.attributeFalloff)

        excludedChargeGroups = [const.groupScannerProbe, const.groupSurveyProbe]
        if not maxRange and charge and charge.groupID not in excludedChargeGroups:
            flightTime = dogmaLocation.GetAccurateAttributeValue(charge.itemID, const.attributeExplosionDelay)
            velocity = dogmaLocation.GetAccurateAttributeValue(charge.itemID, const.attributeMaxVelocity)
            bombRadius = dogmaLocation.GetAccurateAttributeValue(charge.itemID, const.attributeEmpFieldRange)
            maxRange = flightTime * velocity / 1000.0
        return (maxRange, falloffDist, bombRadius)

    def ResetTargetingRanges(self):
        self.targetingRanges = base.AutoTimer(5000, self.UpdateTargetingRanges)

    def GetPanelForUpdate(self, what):
        panel = self.GetPanel(what)
        if panel and not panel.IsCollapsed() and not panel.IsMinimized():
            return panel

    def GetPanel(self, what):
        wnd = uicontrols.Window.GetIfOpen(what)
        if wnd and not wnd.destroyed:
            return wnd

    def InitDrones(self):
        if getattr(self, '_initingDrones', False):
            return
        self._initingDrones = True
        try:
            if not form.DroneView.GetIfOpen():
                form.DroneView.Open(showActions=False, panelName=localization.GetByLabel('UI/Drones/Drones'))
        finally:
            self._initingDrones = False

    def InitOverview(self):
        if not form.OverView.GetIfOpen():
            form.OverView.Open(showActions=False, panelName=localization.GetByLabel('UI/Overview/Overview'))

    def InitSelectedItem(self):
        if not form.ActiveItem.GetIfOpen():
            form.ActiveItem.Open(panelname=localization.GetByLabel('UI/Inflight/ActiveItem/SelectedItem'))

    def InitConnectors(self):
        if self.logme:
            self.LogInfo('Tactical::InitConnectors')
        if not self.inited:
            return
        elif self.tacticalOverlay.useNewOverlay:
            self.tacticalOverlay.InitConnectors()
            return
        else:
            if self.connectors:
                del self.connectors.children[:]
            ballpark = sm.GetService('michelle').GetBallpark()
            if ballpark is None:
                return
            selected = None
            filtered = self.GetFilteredStatesFunctionNames()
            alwaysShown = self.GetAlwaysShownStatesFunctionNames()
            for itemID, ball in ballpark.balls.items():
                if itemID < 0 or itemID == eve.session.shipid:
                    continue
                if ballpark is None:
                    break
                slimItem = ballpark.GetInvItem(itemID)
                if slimItem and self.WantIt(slimItem, filtered, alwaysShown):
                    self.AddConnector(ball, 0)
                selected = sm.GetService('state').GetStates(itemID, [state.selected])
                if selected:
                    selected = itemID

            if selected:
                self.ShowDirectionTo(selected)
            if self.genericUpdateTimer is None:
                self.genericUpdateTimer = base.AutoTimer(1000, self.GenericUpdate)
            return

    def GenericUpdate(self):
        if not self or not self.connectors:
            self.genericUpdateTimer = None
            return
        else:
            for connector in self.connectors.children:
                try:
                    ballID = int(connector.name)
                except:
                    sys.exc_clear()
                    continue

                if connector.name == 'footprint':
                    connector.display = geo2.Vec3Length(connector.translation) < 200000.0

            return

    def WantIt(self, slimItem, filtered=None, alwaysShown=None, isBracket=False):
        if not slimItem:
            return False
        elif slimItem.typeID in INVISIBLE_TYPES:
            return False
        elif isBracket and self.overviewPresetSvc.GetActiveBracketPresetName() is None:
            return True
        if self.logme:
            self.LogInfo('Tactical::WantIt', slimItem)
        if slimItem.itemID == session.shipid:
            return isBracket
        filterGroups = self.overviewPresetSvc.GetValidGroups(isBracket=isBracket)
        if slimItem.groupID in filterGroups:
            if sm.GetService('state').CheckIfFilterItem(slimItem) and self.CheckFiltered(slimItem, filtered, alwaysShown):
                return False
            return True
        else:
            return False

    def CheckIfGroupIDActive(self, groupID):
        if getattr(self, 'logme', None):
            self.LogInfo('Tactical::CheckIfGroupIDActive', groupID)
        if groupID not in tacticalConst.groupIDs:
            return -1
        else:
            return groupID in self.overviewPresetSvc.GetGroups()

    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::tactical')
        try:
            return self.DoBallsAdded_(*args, **kw)
        finally:
            t.PopTimer(timer)

    def DoBallsAdded_(self, lst):
        if not self or getattr(self, 'sr', None) is None:
            return
        else:
            uthread.pool('Tactical::DoBallsAdded', self._DoBallsAdded, lst)
            return

    def _DoBallsAdded(self, lst):
        if not self or self.sr is None:
            return
        else:
            if self.logme:
                self.LogInfo('Tactical::DoBallsAdded', lst)
            self.LogInfo('Tactical - adding balls, num balls:', len(lst))
            inCapsule = 0
            mySlim = uix.GetBallparkRecord(eve.session.shipid)
            if mySlim and mySlim.groupID == const.groupCapsule:
                inCapsule = 1
            checkDrones = 0
            filtered = self.GetFilteredStatesFunctionNames()
            alwaysShown = self.GetAlwaysShownStatesFunctionNames()
            for each in lst:
                if each[1].itemID == eve.session.shipid:
                    checkDrones = 1
                if not checkDrones and not inCapsule and each[1].categoryID == const.categoryDrone:
                    drone = sm.GetService('michelle').GetDroneState(each[1].itemID)
                    if drone and (drone.ownerID == eve.session.charid or drone.controllerID == eve.session.shipid):
                        checkDrones = 1
                if not self.WantIt(each[1], filtered, alwaysShown):
                    continue
                if self.inited:
                    self.AddConnector(each[0])

            if checkDrones:
                droneview = self.GetPanel('droneview')
                if droneview:
                    droneview.CheckDrones()
                else:
                    self.CheckInitDrones()
            return

    def OnDroneStateChange2(self, droneID, oldState, newState):
        self.InitDrones()
        droneview = self.GetPanel('droneview')
        if droneview:
            droneview.CheckDrones()

    def OnDroneControlLost(self, droneID):
        droneview = self.GetPanel('droneview')
        if droneview:
            droneview.CheckDrones()

    @telemetry.ZONE_METHOD
    def DoBallsRemove(self, pythonBalls, isRelease):
        for ball, slimItem, terminal in pythonBalls:
            self.DoBallRemove(ball, slimItem, terminal)

    def DoBallRemove(self, ball, slimItem, terminal):
        if not self or getattr(self, 'sr', None) is None:
            return
        elif ball is None:
            return
        elif not util.InSpace():
            return
        else:
            if self.logme:
                self.LogInfo('Tactical::DoBallRemove', ball.id)
            uthread.pool('tactical::DoBallRemoveThread', self.DoBallRemoveThread, ball, slimItem, terminal)
            self.RemoveBallFromJammers(ball)
            return

    def DoBallRemoveThread(self, ball, slimItem, terminal):
        if self.inited:
            self.ClearConnector(ball.id)
            if util.GetAttrs(self, 'direction', 'object', 'dest') and ball == self.direction.object.dest.translationCurve or util.GetAttrs(self, 'direction', 'object', 'source') and ball == self.direction.object.source.translationCurve:
                self.direction.object.dest.translationCurve = None
                self.direction.object.source.translationCurve = None
                self.direction.display = 0
                self.direction2.display = 0
        droneview = self.GetPanel('droneview')
        if droneview and slimItem.categoryID == const.categoryDrone and slimItem.ownerID == eve.session.charid:
            droneview.CheckDrones()
        return

    def ClearConnector(self, ballID):
        if self.tacticalOverlay.useNewOverlay:
            self.tacticalOverlay.RemoveConnector(ballID)
            return
        if self.logme:
            self.LogInfo('Tactical::ClearConnector', ballID)
        for connector in self.connectors.children[:]:
            if connector.name.startswith(str(ballID)):
                self.connectors.children.remove(connector)

    def GetIntersection(self, dist, planeDist):
        if self.logme:
            self.LogInfo('Tactical::GetIntersection', dist, planeDist)
        return sqrt(abs(dist ** 2 - planeDist ** 2))

    def AddConnector(self, ball, update=1):
        if self.tacticalOverlay.useNewOverlay:
            self.tacticalOverlay.AddConnector(ball)
            return
        else:
            if self.logme:
                self.LogInfo('Tactical::AddConnector', ball, update)
            if self.connectors is None:
                return
            connector = trinity.Load('res:/UI/Inflight/tactical/footprint.red')
            connector.name = str(ball.id)
            connector.display = True
            scene = sm.GetService('sceneManager').GetRegisteredScene('default')
            verticalLine = None
            footprintPlane = None
            for child in connector.children:
                if child.name == 'verticalLine':
                    verticalLine = child
                if child.name == 'footprint':
                    footprintPlane = child

            if verticalLine is not None:
                verticalLine.ClearLines()
                verticalLine.AddLine((0.0, 0.0, 0.0), (0.2, 0.2, 0.2, 1.0), (1.0, 1.0, 1.0), (0.2, 0.2, 0.2, 1.0))
                verticalLine.SubmitChanges()
                verticalLine.translationCurve = ball
                set = trinity.TriCurveSet()
                vs = trinity.TriVectorSequencer()
                vc = trinity.TriVectorCurve()
                vc.value = (0.0, -1.0, 0.0)
                vs.functions.append(ball)
                vs.functions.append(vc)
                bind = trinity.TriValueBinding()
                bind.destinationObject = verticalLine
                bind.destinationAttribute = 'scaling'
                bind.sourceObject = vs
                bind.sourceAttribute = 'value'
                set.curves.append(vs)
                set.curves.append(vc)
                set.bindings.append(bind)
                set.name = str(ball.id) + '_vline'
                set.Play()
                scene.curveSets.append(set)
                self.usedCurveSets.append(set)
            if footprintPlane is not None:
                set = trinity.TriCurveSet()
                vs = trinity.TriVectorSequencer()
                vc = trinity.TriVectorCurve()
                vc.value = (1.0, 0.0, 1.0)
                vs.functions.append(ball)
                vs.functions.append(vc)
                bind = trinity.TriValueBinding()
                bind.destinationObject = footprintPlane
                bind.destinationAttribute = 'translation'
                bind.sourceObject = vs
                bind.sourceAttribute = 'value'
                set.curves.append(vs)
                set.curves.append(vc)
                set.bindings.append(bind)
                set.name = str(ball.id) + '_fprint'
                set.Play()
                scene.curveSets.append(set)
                self.usedCurveSets.append(set)
                connector.display = geo2.Vec3Length(footprintPlane.translation) < 200000.0
            self.connectors.children.append(connector)
            if ball.id == sm.GetService('state').GetExclState(state.selected):
                self.ShowDirectionTo(ball.id)
            return

    def OnEwarStart(self, sourceBallID, moduleID, targetBallID, jammingType):
        if not jammingType:
            self.LogError('Tactical::OnEwarStart', sourceBallID, jammingType)
            return
        if not hasattr(self, 'jammers'):
            self.jammers = {}
        if not hasattr(self, 'jammersByJammingType'):
            self.jammersByJammingType = {}
        if targetBallID == session.shipid:
            if sourceBallID not in self.jammers:
                self.jammers[sourceBallID] = {}
            self.jammers[sourceBallID][jammingType] = sm.GetService('state').GetEwarFlag(jammingType)
            if jammingType not in self.jammersByJammingType:
                self.jammersByJammingType[jammingType] = set()
            self.jammersByJammingType[jammingType].add((sourceBallID, moduleID))
            sm.ScatterEvent('OnEwarStartFromTactical')

    def OnEwarEnd(self, sourceBallID, moduleID, targetBallID, jammingType):
        if not jammingType:
            self.LogError('Tactical::OnEwarEnd', sourceBallID, jammingType)
            return
        if not hasattr(self, 'jammers'):
            return
        if sourceBallID in self.jammers and jammingType in self.jammers[sourceBallID]:
            del self.jammers[sourceBallID][jammingType]
        if jammingType in self.jammersByJammingType and (sourceBallID, moduleID) in self.jammersByJammingType[jammingType]:
            self.jammersByJammingType[jammingType].remove((sourceBallID, moduleID))
        ewarId = (sourceBallID, moduleID, targetBallID)
        sm.ScatterEvent('OnEwarEndFromTactical', jammingType, ewarId)

    def OnEwarOnConnect(self, shipID, m, moduleTypeID, targetID, *args):
        if targetID != session.shipid:
            return
        else:
            ewarType = self.FindEwarTypeFromModuleTypeID(moduleTypeID)
            if ewarType is not None:
                self.OnEwarStart(shipID, m, targetID, ewarType)
            return

    def FindEwarTypeFromModuleTypeID(self, moduleTypeID, *args):
        try:
            effectID = self.clientDogmaStaticSvc.GetDefaultEffect(moduleTypeID)
            return dogma.effects.GetEwarTypeByEffectID(effectID)
        except KeyError:
            pass

    def ImportOverviewSettings(self, *args):
        form.ImportOverviewWindow.Open()

    def ExportOverviewSettings(self, *args):
        form.ExportOverviewWindow.Open()

    def OnEveGetsFocus(self, *args):
        pass

    def GetInBayDroneDamageTracker(self):
        dogmaLM = sm.GetService('godma').GetDogmaLM()
        if self.inBayDroneDamageTracker is None:
            self.inBayDroneDamageTracker = InBayDroneDamageTracker(dogmaLM)
        else:
            self.inBayDroneDamageTracker.SetDogmaLM(dogmaLM)
        return self.inBayDroneDamageTracker