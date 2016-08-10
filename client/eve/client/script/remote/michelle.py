# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\remote\michelle.py
import sys
import math
import collections
from eve.client.script.environment.jumptimer import GetJumpTimer
from eveInflight.damageStateValue import CalculateCurrentDamageStateValues
from inventorycommon.util import IsModularShip
import log
import stackless
from spacecomponents.client.messages import MSG_ON_SLIM_ITEM_UPDATED, MSG_ON_ADDED_TO_SPACE, MSG_ON_REMOVED_FROM_SPACE
from spacecomponents.common.componentregistry import ComponentRegistry, CreateComponentMapping
import uthread
import destiny
import blue
import util
import decometaclass
import moniker
import service
import foo
from eve.client.script.parklife.spewContainerManager import SpewContainerManager
import telemetry
import geo2
import const
from spacecomponents.client.factory import COMPONENTS
import uthread2
from gametime import Timer
from eve.client.script.ui.view.viewStateConst import ViewOverlay
from eve.client.script.ui.shared.fitting.fittingController import FittingController
from operator import attrgetter
import evetypes
from utillib import KeyVal
VISIBILITY_RANGE = 50000000

class Michelle(service.Service):
    __guid__ = 'svc.michelle'
    __exportedcalls__ = {'AddBallpark': [service.ROLE_ANY],
     'RemoveBallpark': [service.ROLE_ANY],
     'GetBallpark': [service.ROLE_ANY],
     'GetRemotePark': [service.ROLE_ANY],
     'GetBallparkForScene': [service.ROLE_ANY],
     'GetBall': [service.ROLE_ANY],
     'GetItem': [service.ROLE_ANY],
     'GetDroneState': [service.ROLE_ANY],
     'GetDrones': [service.ROLE_ANY],
     'Refresh': [service.ROLE_ANY],
     'GetCharIDFromShipID': [service.ROLE_ANY],
     'GetFleetState': [service.ROLE_ANY]}
    __notifyevents__ = ['DoDestinyUpdate',
     'DoDestinyUpdates',
     'OnFleetStateChange',
     'OnDroneStateChange',
     'OnDroneActivityChange',
     'OnAudioActivated',
     'DoSimClockRebase',
     'OnPrimaryViewChanged']
    __dependencies__ = ['machoNet',
     'dataconfig',
     'crimewatchSvc',
     'godma',
     'viewState']

    def Run(self, ms):
        self.state = service.SERVICE_START_PENDING
        self.__bp = None
        self.bpReady = False
        self.quit = 0
        self.scenes = {}
        self.ballNotInParkErrors = {}
        self.handledBallErrors = set()
        self.ballQueue = uthread.Queue()
        uthread.pool('michelle:ballDispatcher', self.Dispatcher)
        self.componentRegistryDependencies = None
        if self.logChannel.IsOpen(1):
            self.logInfo = True
        else:
            self.logInfo = False
        self.state = service.SERVICE_RUNNING
        self.jumpTimer = GetJumpTimer()
        return

    def OnPrimaryViewChanged(self, *args):
        self.UpdateBallpark()

    def UpdateBallpark(self):
        if session.solarsystemid and self.viewState.IsPrimaryViewActive('inflight', 'structure'):
            if self.__bp and self.__bp.solarsystemID != session.solarsystemid:
                self.RemoveBallpark()
            if self.__bp is None:
                sm.GetService('space')
                self.AddBallpark(session.solarsystemid)
                self.DetectAndFixMissingHudModules()
            sm.ScatterEvent('OnEnterSpace')
        else:
            self.RemoveBallpark()
        if self.__bp is None:
            sm.GetService('sceneManager').UnregisterScene('default')
            sm.GetService('sceneManager').CleanupSpaceResources()
            blue.recycler.Clear()
        return

    @telemetry.ZONE_METHOD
    def DetectAndFixMissingHudModules(self):
        try:
            t = uthread2.StartTasklet(self._DetectAndFixMissingHudModules)
            t.context = 'michelle.py::DetectAndFixMissingHudModules (EVE-120280)'
        except Exception as e:
            log.LogException("Exception in Unnar's magical _DetectAndFixMissingHudModules. Thank god we're not taking that seriously. %s" % e)

    def _DetectAndFixMissingHudModules(self):

        def _IsPassiveModule(typeID):
            effects = cfg.dgmtypeeffects.get(typeID, [])
            activeEffectsList = [ effect for effect in effects if effect.isDefault and cfg.dgmeffects.Get(effect.effectID).effectName != 'online' and cfg.dgmeffects.Get(effect.effectID).effectCategory in (const.dgmEffActivation, const.dgmEffTarget) ]
            return len(activeEffectsList) == 0

        def _GetReducedModuleList(listName, modules, attrgetters):
            ret = []
            godma = sm.StartService('godma')
            reportString = ''
            for module in modules:
                itemID = attrgetters['itemID'](module)
                typeID = attrgetters['typeID'](module)
                flagID = attrgetters['flagID'](module)
                reportString += '\nModule %s (%s):\n' % (itemID, evetypes.GetName(typeID))
                godmaItem = None
                if not isinstance(itemID, tuple):
                    godmaItem = godma.GetItem(itemID)
                if isinstance(itemID, tuple) or godmaItem and godmaItem.typeID != typeID:
                    newItemIDReport = 'Checking if I need to substitute parent module itemID.... %s\n'
                    itemWrapper = godma.GetItem(session.shipid)
                    sloccupants = itemWrapper.GetSlotOccupants(flagID)
                    for sloccupant in sloccupants:
                        if sloccupant.flagID == flagID and sloccupant.typeID == typeID and sloccupant.itemID != itemID:
                            newItemIDReport = newItemIDReport % 'itemID %s -> %s' % (itemID, sloccupant.itemID)
                            reportString += newItemIDReport
                            itemID = sloccupant.itemID
                            godmaItem = godma.GetItem(itemID)
                            break
                    else:
                        newItemIDReport = newItemIDReport % 'Nope!'
                        reportString += newItemIDReport

                if not godmaItem:
                    reportString += 'ABORT: No godma item found!\n'
                    continue
                if not const.flagLoSlot0 <= flagID <= const.flagHiSlot7:
                    reportString += 'ABORT: Is not a module!\n'
                    continue
                if clientDogmaLM.IsModuleSlave(itemID, session.shipid):
                    reportString += 'ABORT: Is a slave module!\n'
                    continue
                if evetypes.GetCategoryID(typeID) == const.categoryCharge:
                    reportString += 'ABORT: Is a charge category!\n'
                    continue
                if _IsPassiveModule(typeID) and hidePassive:
                    reportString += 'ABORT: Is filtered by passive settings!\n'
                    continue
                reportString += 'Added (%s, %s, %s)\n' % (itemID, typeID, flagID)
                ret.append((itemID, typeID, flagID))

            ret.sort()
            return (ret, reportString)

        sleepUntil = blue.os.GetWallclockTime() + 10 * const.SEC
        log.LogInfo('_DetectAndFixMissingHudModules sleeping until %s' % util.FmtDate(sleepUntil))
        sessionWaitTimer = Timer(blue.os.GetWallclockTime, blue.synchro.SleepWallclock, const.MIN)
        sessionWaitTimer.SleepUntil(sleepUntil)
        if not self.viewState.IsPrimaryViewActive('inflight'):
            log.LogInfo('_DetectAndFixMissingHudModules slept until player was no longer in space. Aborting check!')
            return
        else:
            log.LogInfo('_DetectAndFixMissingHudModules done sleeping! Checking HUD module state against clientdogma!')
            hidePassive = not settings.user.ui.Get('showPassiveModules', True)
            shipUI = sm.GetService('viewState').overlaysByName.get(ViewOverlay.ShipUI, None)
            if not shipUI:
                log.LogInfo('Viewstate not found. Bailing.')
                return
            clientDogmaLM = sm.GetService('clientDogmaIM').GetDogmaLocation()
            hudController = getattr(shipUI, 'controller', None)
            slotsContainer = getattr(shipUI, 'slotsContainer', None)
            if not hudController or not slotsContainer:
                log.LogInfo("No controller found in shipUI. We're not in space yet!")
                return
            attrgetters = {'itemID': attrgetter('itemID'),
             'typeID': attrgetter('typeID'),
             'flagID': attrgetter('flagID')}
            dogmaModules, dogmaReport = _GetReducedModuleList('dogmaModules', FittingController(session.shipid).GetFittedModules(), attrgetters)
            godmaModules, godmaReport = _GetReducedModuleList('godmaModules', hudController.GetModules(), attrgetters)
            attrgetters = {'itemID': attrgetter('id'),
             'typeID': attrgetter('moduleinfo.typeID'),
             'flagID': attrgetter('moduleinfo.flagID')}
            shipModuleButtons, shipModuleReport = _GetReducedModuleList('shipUIButtons', [ x for x in shipUI.slotsContainer.modulesByID.itervalues() ], attrgetters)
            if dogmaModules != godmaModules:
                dogmaReport = '\n---------------- %s ----------------\n=>%s\n%s' % ('dogmaModules', dogmaModules, dogmaReport)
                godmaReport = '\n---------------- %s ----------------\n=>%s\n%s' % ('godmaModules', godmaModules, godmaReport)
                log.LogException('_DetectAndFixMissingHudModules found missing modules in spaceUI data! I will attempt to refresh godma items and redraw!\n%s %s' % (dogmaReport, godmaReport))
                sm.GetService('godma').GetStateManager().ForcePrimeLocation([session.shipid])
                shipUI.SetupShip()
            elif dogmaModules != shipModuleButtons:
                dogmaReport = '\n---------------- %s ----------------\n=>%s\n%s' % ('dogmaModules', dogmaModules, dogmaReport)
                godmaReport = '\n---------------- %s ----------------\n=>%s\n%s' % ('godmaModules', godmaModules, godmaReport)
                shipModuleReport = '\n---------------- %s ----------------\n=>%s\n%s' % ('shipUIButtons', shipModuleButtons, shipModuleReport)
                log.LogException('_DetectAndFixMissingHudModules found missing modules in spaceUI view. I will attempt to redraw!\n%s%s%s' % (dogmaReport, godmaReport, shipModuleReport))
                shipUI.SetupShip()
            return

    def OnFleetStateChange(self, fleetState):
        if self.__bp is not None:
            self.__bp.OnFleetStateChange(fleetState)
        return

    def OnDroneStateChange(self, droneID, ownerID, controllerID, activityState, droneTypeID, controllerOwnerID, targetID):
        if self.__bp is not None:
            self.__bp.OnDroneStateChange(droneID, ownerID, controllerID, activityState, droneTypeID, controllerOwnerID, targetID)
        return

    def OnDroneActivityChange(self, droneID, activityID, activity):
        if self.__bp is not None:
            self.__bp.OnDroneActivityChange(droneID, activityID, activity)
        return

    def GetFleetState(self):
        if self.__bp is None:
            return
        elif session.fleetid is None:
            return
        else:
            if self.__bp.fleetState is None:
                self.__bp.fleetState = self.GetRemotePark().GetFleetState()
            return self.__bp.fleetState

    def Refresh(self):
        if self.__bp is not None:
            self.__bp.Refresh()
        return

    def RequestReset(self):
        if self.__bp is not None:
            self.__bp.RequestReset()
        return

    def Stop(self, ms):
        if self.__bp is not None:
            self.__bp.Release()
            self.__bp = None
        self.ballQueue.non_blocking_put(None)
        self.quit = 1
        return

    def AddBallpark(self, solarsystemID):
        self.LogNotice('Adding ballpark', solarsystemID)
        self.bpReady = False
        if self.__bp is not None:
            self.__bp.Release()
        self.__bp = blue.classes.CreateInstance('destiny.Ballpark')
        self.LogInfo('GetBallpark1 object', self.__bp, 'now has:', sys.getrefcount(self.__bp), 'references')
        Park(self.__bp, {'broker': self,
         'solarsystemID': long(solarsystemID),
         'hideDesyncSymptoms': True})
        self.LogInfo('GetBallpark2 object', self.__bp, 'now has:', sys.getrefcount(self.__bp), 'references')
        formations = sm.RemoteSvc('beyonce').GetFormations()
        self.__bp.LoadFormations(formations)
        self.ballNotInParkErrors = {}
        self.handledBallErrors = set()
        self.__bp.SetBallNotInParkCallback(self.HandleBallNotInParkError)
        sm.ScatterEvent('OnAddBallpark')
        self.__bp.Start()
        self.bpReady = True
        self.LogNotice('Done adding ballpark', solarsystemID)
        return self.__bp

    def RemoveBallpark(self):
        if self.__bp is not None:
            self.__bp.Release()
            self.__bp = None
        return

    def GetBallpark(self, doWait=False):
        if self.bpReady:
            return self.__bp
        elif not doWait:
            return None
        else:
            tries = self.WaitForBallpark()
            if not self.bpReady:
                logstring = 'Failed to get a valid ballpark in time after trying %d times' % tries
                self.LogError(logstring)
                if session.charid:
                    uthread.new(sm.ProxySvc('clientStatLogger').LogString, logstring)
                return None
            return self.__bp
            return None

    def WaitForBallpark(self):
        WAIT_TIME = 1
        MAX_TRIES = 30
        tries = 0
        while not self.bpReady and tries < MAX_TRIES:
            self.LogInfo('Waiting for ballpark', tries)
            tries = tries + 1
            blue.pyos.synchro.SleepSim(WAIT_TIME * 1000)

        return tries

    def GetRemotePark(self):
        if self.__bp is None:
            return
        else:
            return self.__bp.remoteBallpark

    def GetBallparkForScene(self, scene):
        self.LogInfo('GetBallpark object', self.__bp, 'now has:', sys.getrefcount(self.__bp), 'references')
        if not self.__bp:
            return None
        else:
            if self.__bp not in self.scenes:
                self.scenes[self.__bp] = []
            self.scenes[self.__bp].append(scene)
            return self.__bp

    def GetBall(self, id):
        if self.__bp is not None:
            return self.__bp.GetBall(id)
        else:
            return
            return

    def GetItem(self, id):
        if self.__bp is not None:
            return self.__bp.GetInvItem(id)
        else:
            return

    def InWarp(self):
        ball = self.GetBall(session.shipid)
        return ball and ball.mode == destiny.DSTBALL_WARP

    def IsBallVisible(self, id):
        if self.__bp is not None:
            return self.__bp.IsBallVisible(id)
        else:
            return False
            return

    def GetDroneState(self, droneID):
        if self.__bp is not None:
            return self.__bp.stateByDroneID.get(droneID, None)
        else:
            return

    def GetDroneActivity(self, droneID):
        if self.__bp is not None:
            return self.__bp.activityByDrone.get(droneID, None)
        else:
            return

    def GetDrones(self):
        if self.__bp is not None:
            return self.__bp.stateByDroneID
        else:
            return

    def DoDestinyUpdate(self, state, waitForBubble, dogmaMessages=[], doDump=True):
        self.LogInfo('DoDestinyUpdate call for tick', state[0][0], 'containing', len(state), 'updates.  waitForBubble=', waitForBubble)
        if self.__bp is None:
            return
        else:
            if dogmaMessages:
                self.LogInfo('OnMultiEvent has', len(dogmaMessages), 'messages')
                sm.ScatterEvent('OnMultiEvent', dogmaMessages)
            expandedStates = []
            for action in state:
                if action[1][0] == 'PackagedAction':
                    try:
                        unpackagedActions = blue.marshal.Load(action[1][1])
                        expandedStates.extend(unpackagedActions)
                    except:
                        log.LogException('Exception whilst expanding a PackagedAction')
                        sys.exc_clear()

                else:
                    expandedStates.append(action)

            state = expandedStates
            timestamps = set()
            for action in state:
                timestamps.add(action[0])

            if len(timestamps) > 1:
                self.LogError('Found update batch with', len(state), 'items and', len(timestamps), 'timestamps')
                for action in state:
                    self.LogError('Action:', action)

                sm.GetService('clientStatsSvc').OnFatalDesync()
                if not self.__bp.hideDesyncSymptoms:
                    uthread.new(eve.Message, 'CustomInfo', {'info': 'Desync mismatched updates problem occurred'})
            self.__bp.FlushState(state, waitForBubble, doDump)
            return

    def DoDestinyUpdates(self, updates):
        self.LogInfo('DoDestinyUpdates call, count=', len(updates))
        localDump = False
        idx = 0
        for args in updates:
            idx += 1
            self.LogInfo('DoDestinyUpdate(s)', idx, '/', len(updates))
            if len(args) == 2:
                state, waitForBubble = args
                self.DoDestinyUpdate(state, waitForBubble, doDump=not localDump)
            else:
                state, waitForBubble, dogmaMessages = args
                self.DoDestinyUpdate(state, waitForBubble, dogmaMessages, doDump=not localDump)

        if self.logInfo and localDump:
            self.__bp.DumpHistory()

    def GetCharIDFromShipID(self, shipID):
        if self.__bp is None:
            return
        elif shipID not in self.__bp.slimItems:
            return
        else:
            slimItem = self.__bp.slimItems[shipID]
            return slimItem.charID

    def GetRelativity(self):
        lpark = self.GetBallpark()
        ball = self.GetBall(eve.session.shipid)
        presTime = lpark.currentTime
        pretTime = blue.os.GetWallclockTime()
        prerTime = blue.os.GetWallclockTimeNow()
        preX = ball.x
        preY = ball.y
        preZ = ball.z
        diff, x, y, z, sTime, tTime, rTime = self.GetRemotePark().GetRelativity(preX, preY, preZ, presTime, pretTime, prerTime)
        ldiff = math.sqrt((preX - x) ** 2 + (preY - y) ** 2 + (preZ - z) ** 2)
        postsTime = lpark.currentTime
        posttTime = blue.os.GetWallclockTime()
        postrTime = blue.os.GetWallclockTimeNow()
        pdiff = math.sqrt((ball.x - x) ** 2 + (ball.y - y) ** 2 + (ball.z - z) ** 2)
        print '------------------------------------------------------------------------------------'
        print 'Ticks: client(%s) to server(%s) = %s, server(%s) to client(%s) = %s' % (presTime,
         sTime,
         sTime - presTime,
         sTime,
         postsTime,
         postsTime - sTime)
        print 'Time: client to server %s, server to client %s. Total time to handle call %s' % (util.FmtSec(rTime - prerTime), util.FmtSec(postrTime - rTime), util.FmtSec(postrTime - prerTime))
        print 'pre diff %s on server %s, post diff %s' % (ldiff, diff, pdiff)
        if sTime - postsTime > 0:
            print 'We are behind the server, lets catch up'
            last = lpark.currentTime
            while sTime - lpark.currentTime >= 0:
                if last != lpark.currentTime:
                    last = lpark.currentTime
                    print 'pos diff at step %s is %s' % (lpark.currentTime, math.sqrt((ball.x - x) ** 2 + (ball.y - y) ** 2 + (ball.z - z) ** 2))
                blue.pyos.synchro.Yield()

        elif sTime - postsTime == 0:
            print 'client and server match, as the client should be ahead there is some lag'
        else:
            print 'We are ahead of the server (at least when the call had come back), to handle this case we need the pos history for the last 10 ticks or so'

    def Dispatcher(self):
        while self.state in (service.SERVICE_RUNNING, service.SERVICE_START_PENDING):
            try:
                orders = None
                orders = self.ballQueue.get()
                if orders is None:
                    return
                self.ProcessDispatchOrders(orders)
            except StandardError:
                self.LogError('In michelle.Dispatcher')
                log.LogException()
                sys.exc_clear()

        return

    def ProcessDispatchOrders(self, orders):
        ownersToPrime, tickersToPrime, allyTickersToPrime, stuffToAdd, newState, locationsToPrime = orders
        if locationsToPrime:
            try:
                cfg.evelocations.Prime(locationsToPrime)
            except StandardError:
                self.LogError('In michelle.Dispatcher')
                log.LogException()
                sys.exc_clear()

        if ownersToPrime:
            try:
                cfg.eveowners.Prime(ownersToPrime)
            except StandardError:
                self.LogError('In michelle.Dispatcher')
                log.LogException()
                sys.exc_clear()

        if tickersToPrime:
            try:
                cfg.corptickernames.Prime(tickersToPrime)
            except StandardError:
                self.LogError('In michelle.Dispatcher')
                log.LogException()
                sys.exc_clear()

        if allyTickersToPrime:
            try:
                cfg.allianceshortnames.Prime(allyTickersToPrime)
            except StandardError:
                self.LogError('In michelle.Dispatcher')
                log.LogException()
                sys.exc_clear()

        realBalls = {}
        for ballID, slimItem in stuffToAdd:
            try:
                if self.__bp and ballID in self.__bp.balls:
                    ball = self.__bp.balls[ballID]
                    if not self.__bp.slimItems.has_key(ballID):
                        realBalls[ballID] = (ball, slimItem)
                    self.__bp.slimItems[ballID] = slimItem
            except StandardError:
                self.LogError('In michelle.Dispatcher')
                log.LogException()
                sys.exc_clear()

        if len(realBalls):
            t = stackless.getcurrent()
            timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::DoBallsAdded')
            sm.SendEvent('DoBallsAdded', realBalls.values())
            t.PopTimer(timer)
        if newState is not None:
            t = stackless.getcurrent()
            timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::OnNewState')
            sm.ScatterEvent('OnNewState', newState)
            t.PopTimer(timer)
        return

    def HandleBallNotInParkError(self, ball):
        reportBallNotInPark = prefs.GetValue('reportBallNotInPark', False)
        if not reportBallNotInPark:
            return
        else:
            now = blue.os.GetWallclockTime()
            ballID = ball.id
            if ballID in self.ballNotInParkErrors and ballID not in self.handledBallErrors:
                diff = now - self.ballNotInParkErrors[ballID]
                if 5 * const.SEC < diff:
                    if not self.logChannel.IsOpen(4):
                        print 'Ball', ballID, 'not in park!'
                    else:
                        self.LogError('-----------------------------------------------------------------------------------')
                        self.LogError('BALL NOT IN PARK:', ballID)
                        self.LogError('-----------------------------------------------------------------------------------')
                        self.LogError('Ball has not been in park for', diff / const.SEC, 'seconds.')
                        self.LogError("Probable cause is trinity graphics that haven't been cleaned up.")
                        self.LogError('Ball Info:')
                        self.LogError('\tBall deco type:', getattr(ball, '__class__', '?'))
                        self.LogError('\tModel:', getattr(ball, 'model', None))
                        self.LogError('\tExploded:', getattr(ball, 'exploded', '?'))
                        if ball.ballpark is None:
                            self.LogError('\tNot in any ballpark')
                        else:
                            self.LogError('\tIn Ballpark:', getattr(ball.ballpark, 'solarsystemID', '?'))
                        slimItem = self.GetItem(ball.id)
                        if slimItem:
                            self.LogError('Slim Item Info:')
                            self.LogError('\tType:', slimItem.typeID)
                        self.LogError('Checking Scene')
                        scene = sm.GetService('sceneManager').GetActiveScene()
                        if scene is not None:
                            for obj in scene.objects:
                                if len([ foundBall for foundBall in obj.Find('destiny.ClientBall') if foundBall == ball ]):
                                    if hasattr(obj, 'display'):
                                        obj.display = 0
                                    if hasattr(obj, 'update'):
                                        obj.update = 0
                                    self.LogError('\tAttached to', obj.__bluetype__, 'named', getattr(obj, 'name', '?'), ' in Scene')

                    self.handledBallErrors.add(ballID)
                    del self.ballNotInParkErrors[ballID]
            else:
                self.ballNotInParkErrors[ballID] = now
            return

    def OnAudioActivated(self):
        if self.__bp is not None:
            self.__bp.OnAudioActivated()
        return

    def DoSimClockRebase(self, times):
        oldSimTime, newSimTime = times
        if self.__bp:
            self.__bp.AdjustTimes(newSimTime - oldSimTime)

    def IsPositionWithinWarpDistance(self, position):
        ballpark = self.GetBallpark()
        egoBall = ballpark.GetBall(ballpark.ego)
        distance = geo2.Vec3Distance((egoBall.x, egoBall.y, egoBall.z), position)
        return distance > const.minWarpDistance

    def InitializeComponentRegistryDependencies(self):
        componentClassTypes, typeIDToClassMapping = CreateComponentMapping(cfg.spaceComponentStaticData, COMPONENTS)
        self.componentRegistryDependencies = KeyVal(attributeLoader=cfg.spaceComponentStaticData, componentClassTypes=componentClassTypes, typeIDToClassMapping=typeIDToClassMapping, asyncFuncs=KeyVal(GetWallclockTime=blue.os.GetWallclockTime, SleepWallclock=blue.pyos.synchro.SleepWallclock, GetSimTime=blue.os.GetSimTime, SleepSim=blue.pyos.synchro.SleepSim, TimeDiffInMs=blue.os.TimeDiffInMs, UThreadNew=uthread.new))

    def CreateComponentRegistry(self):
        if self.componentRegistryDependencies is None:
            self.InitializeComponentRegistryDependencies()
        return ComponentRegistry(self.componentRegistryDependencies.attributeLoader, self.componentRegistryDependencies.asyncFuncs, None, self.componentRegistryDependencies.componentClassTypes, self.componentRegistryDependencies.typeIDToClassMapping)


class BallQueueData():

    def __init__(self):
        self.stuffToAdd = []
        self.ownersToPrime = []
        self.tickersToPrime = []
        self.allyTickersToPrime = []
        self.locationsToPrime = []


class Park(decometaclass.WrapBlueClass('destiny.Ballpark')):
    __guid__ = 'michelle.Park'
    __nonpersistvars__ = ['states',
     'broker',
     'lastStamp',
     'dirty',
     'remoteBallpark',
     'slimItems',
     'damageState',
     'solItem',
     'validState',
     'history']
    __persistdeco__ = 0
    __categoryRequireOwnerPrime__ = None
    __predefs__ = 0

    def __init__(self):
        if not self.__predefs__:
            self.__predefs__ = 1
            self.__categoryRequireOwnerPrime__ = (const.categoryShip, const.categoryDrone)
        self.tickInterval = const.simulationTimeStep
        self.lastStamp = -1
        self.dirty = 0
        self.states = []
        self.slimItems = {}
        self.damageState = {}
        self.stateByDroneID = {}
        self.componentRegistry = None
        self.spewContainerManager = SpewContainerManager(self)
        self.fleetState = None
        self.solItem = None
        self.validState = 0
        self.history = []
        self.latestSetStateTime = 0
        self.shouldRebase = False
        self.activityByDrone = {}
        self.clientBallNextID = -8000000000000000000L
        self.remoteBallpark = moniker.GetBallPark(self.solarsystemID)
        self.remoteBallpark.Bind()
        self.scatterEvents = {'Orbit': 1,
         'GotoDirection': 1,
         'WarpTo': 1,
         'SetBallRadius': 1,
         'GotoPoint': 1,
         'SetBallInteractive': 1,
         'SetBallFree': 1,
         'SetBallHarmonic': 1,
         'FollowBall': 1}
        self.nonDestinyCriticalFunctions = set(['OnDamageStateChange',
         'OnSpecialFX',
         'OnFleetDamageStateChange',
         'OnShipStateUpdate',
         'OnSlimItemChange',
         'OnDroneStateChange',
         'OnSovereigntyChanged'])
        self.componentRegistry = self.broker.GetComponentRegistry()
        return

    def __del__(self):
        self.remoteBallpark = None
        self.broker = None
        self.states = []
        return

    def RequestReset(self):
        self.validState = False
        if self.hideDesyncSymptoms:
            self.FlushSimulationHistory(newBaseSnapshot=False)
        else:
            self.RebaseStates(1)
        uthread.pool('michelle::UpdateStateRequest', self.remoteBallpark.UpdateStateRequest)

    def DoPostTick(self, stamp):
        if self.shouldRebase:
            if self.hideDesyncSymptoms:
                self.FlushSimulationHistory()
            else:
                self.RebaseStates()
            self.shouldRebase = False
        elif stamp > self.lastStamp + 10:
            self.StoreState()

    def DumpHistory(self):
        self.broker.LogInfo('------ History Dump', self.currentTime, '-------')
        rev = self.history[:]
        rev.reverse()
        for state, waitForBubble in rev:
            self.broker.LogInfo('state waiting:', ['no', 'yes'][waitForBubble])
            lastState = None
            lastStateCount = 0
            for entry in state:
                eventStamp, event = entry
                funcName, args = event
                nextState = ['[',
                 eventStamp,
                 ']',
                 funcName]
                if nextState != lastState:
                    if lastState is not None:
                        if lastStateCount != 1:
                            lastState.append('(x %d)' % lastStateCount)
                        self.broker.LogInfo(*lastState)
                    lastState = nextState
                    lastStateCount = 1
                else:
                    lastStateCount += 1

            if lastState is not None:
                if lastStateCount != 1:
                    lastState.append('(x %d)' % lastStateCount)
                self.broker.LogInfo(*lastState)
            self.broker.LogInfo(' ')

        return

    def DoPreTick(self, stamp):
        if not self.hideDesyncSymptoms:
            while len(self.history) > 0:
                state, waitForBubble = self.history[0]
                if waitForBubble:
                    return
                eventStamp, event = state[0]
                if eventStamp > self.currentTime and eventStamp - self.currentTime < 3:
                    break
                funcName, args = event
                self.RealFlushState(state)
                del self.history[0]
                if len(self.history) > 1:
                    if self.history[0][1]:
                        return
                    self._parent_Evolve()

            return
        while len(self.history) > 0:
            state, waitForBubble = self.history[0]
            if waitForBubble:
                return
            eventStamp = state[0][0]
            if eventStamp > self.currentTime and eventStamp - self.currentTime < 3:
                break
            self.RealFlushState(state)
            del self.history[0]
            if self.validState and self.shouldRebase:
                self.StoreState(midTick=True)
            if len(self.history) > 1:
                if self.history[0][1]:
                    return
                self._parent_Evolve()

    def StoreState(self, midTick=False):
        if self.dirty or not self.isRunning:
            return
        ms = blue.MemStream()
        self.WriteFullStateToStream(ms)
        if self.hideDesyncSymptoms:
            self.states.append([ms, self.currentTime, midTick])
        else:
            self.states.append([ms, self.currentTime])
        if self.broker.logInfo:
            self.broker.LogInfo('StoreState:', self.currentTime, 'midTick:', midTick)
        if len(self.states) > 10:
            self.states = self.states[:1] + self.states[3:3] + self.states[-5:]
        self.lastStamp = self.currentTime

    def Release(self):
        sm.ScatterEvent('OnReleaseBallpark')
        self._parent_Pause()
        self.RemoveBalls(self.balls.iterkeys(), isRelease=True)
        self._parent_ClearAll()
        if self.hideDesyncSymptoms:
            self.FlushSimulationHistory(newBaseSnapshot=False)
        else:
            self.RebaseStates(1)
        if self in self.broker.scenes:
            for scene in self.broker.scenes[self]:
                if scene and hasattr(scene, 'ballpark'):
                    scene.ballpark = None

            del self.broker.scenes[self]
        self.validState = False
        self.solItem = None
        self.remoteBallpark.Unbind()
        self.remoteBallpark = None
        self.slimItems = {}
        self.damageState = {}
        self.activityByDrone = {}
        self.history = []
        self.latestSetStateTime = 0
        return

    def SetState(self, bag):
        self.componentRegistry = self.broker.CreateComponentRegistry()
        self.stateByDroneID = bag.droneState.Index('droneID')
        with util.ExceptionEater('Failed logging DoBallClear'):
            self.broker.LogNotice('SetState called. Spamming DoBallClear', bag.solItem.itemID)
        sm.SendEvent('DoBallClear', bag.solItem)
        self.ClearAll()
        ms = blue.MemStream()
        ms.Write(bag.state)
        self._parent_ReadFullStateFromStream(ms)
        self.ego = long(bag.ego)
        self._parent_Start()
        self.slimItems = {}
        ballQueueData = BallQueueData()
        for slimItem in bag.slims:
            if type(slimItem) is int:
                raise TypeError
            if slimItem.itemID not in self.balls:
                raise RuntimeError('BallNotInPark', slimItem.itemID, slimItem)
            self.ProcessBallAdd(slimItem, ballQueueData)

        self.validState = True
        if self.hideDesyncSymptoms:
            self.FlushSimulationHistory()
        else:
            self.RebaseStates()
        self.QueueBallData(ballQueueData, newState=self)
        now = blue.os.GetSimTime()
        self.damageState = {}
        for k, v in bag.damageState.iteritems():
            self.damageState[k] = (v, now)

        for effectInfo in bag.effectStates:
            self.OnSpecialFX(*effectInfo)
            self.ScatterEwars(*effectInfo)

        sm.services['pwn'].ProcessAllianceBridgeModePurge()
        for shipID, toSolarsystemID, toBeaconID in bag.allianceBridges:
            sm.services['pwn'].OnAllianceBridgeModeChange(shipID, toSolarsystemID, toBeaconID, True)

        self.solItem = bag.solItem
        self.industryLevel = bag.industryLevel
        self.researchLevel = bag.researchLevel
        sm.ScatterEvent('OnBallparkSetState')

    def QueueBallData(self, ballQueueData, newState=None):
        self.broker.ballQueue.non_blocking_put((ballQueueData.ownersToPrime,
         ballQueueData.tickersToPrime,
         ballQueueData.allyTickersToPrime,
         ballQueueData.stuffToAdd,
         newState,
         ballQueueData.locationsToPrime))

    def GetDamageState(self, itemID):
        if itemID not in self.damageState:
            return
        else:
            mainctx = blue.pyos.taskletTimer.EnterTasklet('Michelle::GetDamageState')
            try:
                state, time = self.damageState[itemID]
                if not state:
                    return
                ret = CalculateCurrentDamageStateValues(state, time)
                ret = ret + list(state[-2:])
            finally:
                blue.pyos.taskletTimer.ReturnFromTasklet(mainctx)

            return ret

    def DistanceBetween(self, srcID, dstID):
        dist = self.GetSurfaceDist(srcID, dstID)
        if dist is None:
            raise RuntimeError('DistanceBetween:: invalid balls', srcID, dstID)
        if dist < 0.0:
            dist = 0.0
        return dist

    def IsShipInRangeOfStructureControlTower(self, shipID, structureID):
        structureSlim = self.slimItems.get(structureID)
        if structureSlim is None:
            return False
        else:
            controlTowerID = None
            if structureSlim.groupID == const.groupControlTower:
                controlTowerID = structureID
            elif structureSlim.controlTowerID is not None:
                controlTowerID = structureSlim.controlTowerID
            if controlTowerID is None:
                return False
            towerSlim = self.slimItems.get(controlTowerID)
            if towerSlim is None:
                return False
            towerShieldRadius = self.broker.godma.GetStateManager().GetType(towerSlim.typeID).shieldRadius
            return self.GetCenterDist(controlTowerID, shipID) < towerShieldRadius

    def RebaseStates(self, wipe=0):
        if self.broker.logInfo:
            self.broker.LogInfo('State history rebased at', self.currentTime)
        self.states = []
        if not wipe:
            self.StoreState()

    def FlushSimulationHistory(self, newBaseSnapshot=True):
        if self.broker.logInfo:
            self.broker.LogInfo('State history rebased at', self.currentTime, 'newBaseSnapshot', newBaseSnapshot)
        lastMidState = None
        if newBaseSnapshot and len(self.states):
            lastMidState = self.states[-1]
            if not lastMidState[2] or lastMidState[1] != self.currentTime - 1:
                lastMidState = None
        self.states = []
        if newBaseSnapshot:
            if lastMidState:
                self.states.append(lastMidState)
            self.StoreState()
            for item in self.states:
                if self.broker.logInfo:
                    self.broker.LogInfo('State entry', item)

        return

    def SynchroniseToSimulationTime(self, stamp):
        if self.broker.logInfo:
            self.broker.LogInfo('SynchroniseToSimulationTime looking for:', stamp, '- current:', self.currentTime)
        if stamp < self.currentTime:
            lastStamp = 0
            lastState = None
            for item in self.states:
                if item[1] <= stamp:
                    lastStamp = item[1]
                    lastState = item[0]
                else:
                    continue

            if not lastState:
                self.broker.LogWarn('SynchroniseToSimulationTime: Did not find any state')
                return 0
            self._parent_ReadFullStateFromStream(lastState, 1)
        else:
            lastStamp = self.currentTime
        for i in range(stamp - lastStamp):
            self._parent_Evolve()

        if self.broker.logInfo:
            self.broker.LogInfo('SynchroniseToSimulationTime found:', self.currentTime)
        return 1

    def FlushState(self, state, waitForBubble, doDump=True):
        self.broker.LogInfo('Server Update with', len(state), 'event(s) added to history')
        if len(state) == 0:
            self.broker.LogWarn('Empty state received from remote ballpark')
            return
        if state[0][1][0] == 'SetState':
            self.latestSetStateTime = state[0][0]
            self.broker.LogInfo('Michelle received a SetState at time', self.latestSetStateTime, '. Clearing out-of-date entries...')
            self.history[:] = [ historyEntry for historyEntry in self.history if historyEntry[0][0][0] >= self.latestSetStateTime ]
            if self.broker.logInfo and doDump:
                self.DumpHistory()
        else:
            entryTime = state[0][0]
            if entryTime < self.latestSetStateTime:
                self.broker.LogWarn('Michelle discarded a state that was too old', entryTime, ' < ', self.latestSetStateTime)
                if self.broker.logInfo and doDump:
                    self.DumpHistory()
                return
        if not hasattr(self, 'hideDesyncSymptoms'):
            sm.services['michelle'].LogError('UNABLE TO FIND ATTRIBUTE ON BALLPARK, RELEASED?', getattr(self, 'broker', 'NO BROKER'), getattr(self, 'solarSystemID', 'NO SOLAR SYSTEM ID'))
            return
        if not self.hideDesyncSymptoms:
            if len(self.history) and self.history[-1][0][0][0] == state[0][0]:
                if self.broker.logInfo:
                    self.broker.LogInfo('FlushState: Coalescing states')
                self.history[-1][0].extend(state)
                self.history[-1][1] = False
            else:
                self.history.append([state, waitForBubble])
            if self.broker.logInfo and doDump:
                self.DumpHistory()
            return
        oldStatesByTime = {}
        newestOldStateTime = 0
        for oldState in self.history:
            oldStatesByTime[oldState[0][0][0]] = oldState

        if len(self.history):
            newestOldStateTime = self.history[-1][0][0][0]
        entriesByTime = {}
        for entry in state:
            entryTime = entry[0]
            if not entriesByTime.has_key(entryTime):
                entriesByTime[entryTime] = [entry]
            else:
                entriesByTime[entryTime].append(entry)

        timeList = entriesByTime.keys()
        timeList.sort()
        for entryTime in timeList:
            if entryTime in oldStatesByTime:
                if self.broker.logInfo:
                    self.broker.LogInfo('FlushState: Incorporating events into existing tick', entryTime)
                oldStatesByTime[entryTime][0].extend(entriesByTime[entryTime])
                oldStatesByTime[entryTime][1] = False
            elif entryTime > newestOldStateTime:
                if self.broker.logInfo:
                    self.broker.LogInfo('FlushState: Adding update for new tick', entryTime)
                self.history.append([entriesByTime[entryTime], waitForBubble])
                waitForBubble = False
            else:
                for i in range(len(self.history)):
                    if self.history[i][0][0][0] > entryTime:
                        if self.broker.logInfo:
                            self.broker.LogInfo('FlushState: Injecting update for previous tick', entryTime)
                        self.history.insert(i, [entriesByTime[entryTime], waitForBubble])
                        waitForBubble = False
                        break

        if self.broker.logInfo and doDump:
            self.DumpHistory()

    def RealFlushState(self, state):
        if self.broker.logInfo:
            self.broker.LogInfo('Handling Server Update with', len(state), 'event(s)')
        if len(state) == 0:
            self.broker.LogWarn('Empty state received from remote ballpark')
            return
        entryStamp = self.currentTime
        eventStamp, event = state[0]
        funcName, args = event
        if funcName == 'SetState':
            if self.broker.logInfo and util.IsFullLogging():
                self.broker.LogInfo('Action: %12.12s' % funcName, eventStamp, '- current:', self.currentTime, args)
            apply(self.SetState, args)
        if self.validState:
            self.shouldRebase = False
            synchronised = False
            for action in state:
                eventStamp, event = action
                funcName, args = event
                if funcName == 'SetState':
                    continue
                if funcName == 'Challenge':
                    self.broker.LogWarn(eventStamp, '->', args)
                    continue
                if self.broker.logInfo and util.IsFullLogging():
                    self.broker.LogInfo('Action: %12.12s' % funcName, eventStamp, '- current:', self.currentTime, args)
                try:
                    if funcName in self.nonDestinyCriticalFunctions:
                        apply(getattr(self, funcName), args)
                    else:
                        if not synchronised:
                            synchronised = self.SynchroniseToSimulationTime(eventStamp)
                        if not synchronised:
                            sm.GetService('clientStatsSvc').OnRecoverableDesync()
                            self.broker.LogWarn('Failed to synchronize to', eventStamp, 'Requesting new state')
                            self.RequestReset()
                            return
                        self.shouldRebase = True
                        if funcName in ('AddBalls', 'AddBalls2', 'RemoveBalls', 'SetState', 'RemoveBall', 'TerminalExplosion'):
                            if funcName == 'RemoveBalls':
                                exploders = [ x[1][1][0] for x in state if x[1][0] == 'TerminalExplosion' ]
                                args = args + (exploders,)
                            apply(getattr(self, funcName), args)
                        else:
                            apply(getattr(self, '_parent_' + funcName), args)
                            if funcName in self.scatterEvents:
                                sm.ScatterEvent('OnBallparkCall', funcName, args)
                except Exception as e:
                    log.LogException('Something potentially bad happened with %s' % funcName)
                    sys.exc_clear()
                    continue

        else:
            self.broker.LogInfo('Events ignored')

    def TerminalExplosion(self, shipID, bubbleID=None, ballIsGlobal=False):
        pass

    def ProcessBallAdd(self, slimItem, ballQueueData):
        ball = self.balls[slimItem.itemID]
        if slimItem.itemID > destiny.DSTLOCALBALLS:
            ballQueueData.stuffToAdd.append((slimItem.itemID, slimItem))
            if slimItem.categoryID in self.__categoryRequireOwnerPrime__:
                ballQueueData.ownersToPrime.append(slimItem.ownerID)
                if slimItem.charID is not None:
                    ballQueueData.ownersToPrime.append(slimItem.charID)
                    ballQueueData.ownersToPrime.append(slimItem.corpID)
            if slimItem.corpID and slimItem.corpID not in ballQueueData.tickersToPrime:
                ballQueueData.tickersToPrime.append(slimItem.corpID)
            if slimItem.allianceID and slimItem.allianceID not in ballQueueData.allyTickersToPrime:
                ballQueueData.allyTickersToPrime.append(slimItem.allianceID)
            if util.IsCelestial(slimItem.itemID) or util.IsStargate(slimItem.itemID):
                ballQueueData.locationsToPrime.append(slimItem.itemID)
            elif slimItem.itemID >= const.minFakeItem and slimItem.nameID is not None:
                location = [slimItem.itemID,
                 '',
                 self.solarsystemID,
                 ball.x,
                 ball.y,
                 ball.z,
                 slimItem.nameID]
                cfg.evelocations.Hint(slimItem.itemID, location)
            elif not (slimItem.categoryID == const.categoryAsteroid or slimItem.groupID == const.groupHarvestableCloud):
                location = [slimItem.itemID,
                 slimItem.name,
                 self.solarsystemID,
                 ball.x,
                 ball.y,
                 ball.z,
                 slimItem.nameID]
                cfg.evelocations.Hint(slimItem.itemID, location)
        if self.componentRegistry.GetComponentClassesForTypeID(slimItem.typeID):
            self.componentRegistry.CreateComponentInstances(slimItem.itemID, slimItem.typeID)
            self.componentRegistry.SendMessageToItem(slimItem.itemID, MSG_ON_ADDED_TO_SPACE, slimItem)
        sm.ScatterEvent('OnBallAdded', slimItem)
        return

    def AddBalls(self, chunk):
        state, slims, damageDict = chunk
        ms = blue.MemStream()
        ms.Write(state)
        self._parent_ReadFullStateFromStream(ms, 2)
        ballQueueData = BallQueueData()
        for slimItem in slims:
            if type(slimItem) is int:
                raise TypeError
            if slimItem.itemID in self.slimItems:
                continue
            self.ProcessBallAdd(slimItem, ballQueueData)

        self.QueueBallData(ballQueueData)
        t = blue.os.GetSimTime()
        for ballID, damage in damageDict.iteritems():
            self.damageState[ballID] = (damage, t)

    def AddBalls2(self, chunk):
        state, extraBallData = chunk
        ms = blue.MemStream()
        ms.Write(state)
        self._parent_ReadFullStateFromStream(ms, 2)
        ballQueueData = BallQueueData()
        damageTime = blue.os.GetSimTime()
        for data in extraBallData:
            if type(data) is tuple:
                slimItemDict, damageState = data
            else:
                slimItemDict = data
                damageState = None
            slimItem = foo.SlimItem()
            slimItem.__dict__ = slimItemDict
            self.damageState[slimItem.itemID] = (damageState, damageTime)
            if slimItem.itemID in self.slimItems:
                continue
            self.ProcessBallAdd(slimItem, ballQueueData)

        self.QueueBallData(ballQueueData)
        return

    def AddClientSideBall(self, position, isGlobal=False):
        x, y, z = position
        ball = self.AddBall(self.clientBallNextID, 1.0, 0.0, 0, False, isGlobal, False, False, False, x, y, z, 0, 0, 0, 0, 0)
        self.clientBallNextID -= 1
        return ball

    def RemoveClientSideBall(self, ballID):
        ball = self.GetBall(ballID)
        self._parent_RemoveBall(ballID, 0)
        if ball:
            sm.SendEvent('DoClientSideBallRemove', ball)

    def UpdateClientSideBallPosition(self, ballID, position):
        ball = self.GetBall(ballID)
        ball.x, ball.y, ball.z = position

    @telemetry.ZONE_METHOD
    def RemoveBall(self, ballID, terminal=False, bubbleID=-1):
        if self.broker.logInfo:
            self.broker.LogInfo('Removing ball', ballID, '(terminal)' if terminal else '')
        ball = self.balls.get(ballID, None)
        delay = 0
        if hasattr(ball, 'KillBooster'):
            ball.KillBooster()
        if terminal and hasattr(ball, '__class__'):
            delay = const.terminalExplosionDelay
            ball.explodeOnRemove = True
        self._parent_RemoveBall(ballID, delay)
        self.DeleteComponents(ballID)
        if ballID in self.damageState:
            del self.damageState[ballID]
        if self.activityByDrone.has_key(ballID):
            del self.activityByDrone[ballID]
        if ballID not in self.slimItems:
            return
        else:
            slimItem = self.slimItems[ballID]
            if ballID > destiny.DSTLOCALBALLS:
                if ball is None:
                    self.broker.LogWarn('DoBallRemove sending a None ball', slimItem, terminal)
                sm.SendEvent('DoBallRemove', ball, slimItem, terminal)
            if ballID in self.slimItems:
                del self.slimItems[ballID]
            return

    @telemetry.ZONE_METHOD
    def RemoveBalls(self, ballIDs, exploders=None, isRelease=False):
        if exploders:
            if self.broker.logInfo:
                self.broker.LogInfo('RemoveBalls: Has exploders')
            for ballID in exploders:
                ball = self.balls.get(ballID, None)
                if ball is not None and hasattr(ball, '__class__'):
                    ball.explodeOnRemove = True

        pythonBalls = []
        destinyBalls = []
        for ballID in ballIDs:
            ball = self.balls.get(ballID)
            if ballID < 0:
                continue
            if ball is None:
                continue
            if hasattr(ball, 'KillBooster'):
                ball.KillBooster()
            destinyBalls.append(ball)
            if ballID in self.slimItems and ballID > destiny.DSTLOCALBALLS:
                terminal = getattr(ball, 'explodeOnRemove', False)
                pythonBalls.append((ball, self.slimItems[ballID], terminal))

        sm.SendEvent('DoBallsRemove', pythonBalls, isRelease)
        for ball in destinyBalls:
            delay = 0
            if getattr(ball, 'explodeOnRemove', False):
                delay = const.terminalExplosionDelay
            self._parent_RemoveBall(ball.id, delay)
            self.DeleteComponents(ball.id)

        for ballID in ballIDs:
            if ballID in self.damageState:
                del self.damageState[ballID]
            if self.activityByDrone.has_key(ballID):
                del self.activityByDrone[ballID]
            if ballID in self.slimItems:
                del self.slimItems[ballID]

        return

    def DeleteComponents(self, itemID):
        if self.componentRegistry is None:
            return
        else:
            self.componentRegistry.SendMessageToItem(itemID, MSG_ON_REMOVED_FROM_SPACE)
            try:
                self.componentRegistry.DeleteComponentInstances(itemID)
            except KeyError:
                pass

            return

    def GetBallsAndItems(self):
        ballList = []
        for ball in self.balls.itervalues():
            if ball.id in self.slimItems:
                ballList.append((ball, self.slimItems[ball.id]))

        return ballList

    def GetBall(self, ballID):
        return self.balls.get(ballID, None)

    def GetBallById(self, ballID):
        return self.GetBall(ballID)

    def GetWarpinPoint(self, ballID):
        ball = self.GetBall(ballID)
        item = self.GetInvItem(ballID)
        if item.groupID == const.groupPlanet:
            return util.GetPlanetWarpInPoint(ballID, (ball.x, ball.y, ball.z), ball.radius)
        else:
            return util.GetWarpInPoint(ballID, (ball.x, ball.y, ball.z), ball.radius)

    def GetWarpinPoints(self):
        balls = []
        for ball in self.globals.itervalues():
            if ball.radius > 90000:
                ballItem = self.GetInvItem(ball.id)
                if ballItem is None:
                    continue
                balls.append((ball, ballItem, self.GetWarpinPoint(ball.id)))

        return balls

    def OnFleetStateChange(self, fleetState):
        self.broker.LogInfo('OnFleetStateChange', fleetState)
        self.fleetState = fleetState

    def GetLootRights(self, objectID):
        if self.slimItems.has_key(objectID):
            slim = self.slimItems[objectID]
            return getattr(slim, 'lootRights', None)
        else:
            return None

    def IsAbandoned(self, objectID):
        if self.slimItems.has_key(objectID):
            slim = self.slimItems[objectID]
            lootRights = getattr(slim, 'lootRights', None)
            if lootRights is not None:
                ownerID, corpID, fleetID, abandoned = lootRights
                return abandoned
        return False

    def HaveLootRight(self, objectID):
        if self.slimItems.has_key(objectID):
            slim = self.slimItems[objectID]
            if session.charid == slim.ownerID:
                return True
            lootRights = getattr(slim, 'lootRights', None)
            if lootRights is not None:
                ownerID, corpID, fleetID, abandoned = lootRights
                if abandoned:
                    return True
                if session.charid == ownerID:
                    return True
                if not util.IsNPCCorporation(session.corpid) and session.corpid in (ownerID, corpID):
                    return True
                if session.fleetid is not None and session.fleetid == fleetID:
                    return True
                if self.broker.crimewatchSvc.CanAttackFreely(slim):
                    return True
            elif not util.IsNPCCorporation(session.corpid) and session.corpid == slim.ownerID:
                return True
        return False

    def GetTypeIDsAndFlagIDsForModules(self, modules):
        return {(typeID, flagID) for _, typeID, flagID in modules}

    def IsSubSystemChange(self, oldSlim, newSlim):
        if not IsModularShip(newSlim.typeID):
            return False
        return self.GetTypeIDsAndFlagIDsForModules(oldSlim.modules) != self.GetTypeIDsAndFlagIDsForModules(newSlim.modules)

    def OnSlimItemChange(self, itemID, newSlim):
        if self.slimItems.has_key(itemID):
            oldSlim = self.slimItems[itemID]
            self.slimItems[itemID] = newSlim
            sm.ScatterEvent('OnSlimItemChange', oldSlim, newSlim)
            ball = self.GetBall(itemID)
            if ball is not None:
                if hasattr(ball, 'OnSlimItemUpdated'):
                    ball.OnSlimItemUpdated(newSlim)
                if self.IsSubSystemChange(oldSlim, newSlim):
                    ball.OnSubSystemChanged(newSlim)
            self.componentRegistry.SendMessageToItem(itemID, MSG_ON_SLIM_ITEM_UPDATED, newSlim)
        return

    def OnDroneStateChange(self, itemID, ownerID, controllerID, activityState, typeID, controllerOwnerID, targetID):
        if session.charid != ownerID and session.shipid != controllerID:
            if self.stateByDroneID.has_key(itemID):
                del self.stateByDroneID[itemID]
            if self.activityByDrone.has_key(itemID):
                del self.activityByDrone[itemID]
            sm.ScatterEvent('OnDroneControlLost', itemID)
            return
        else:
            state = self.stateByDroneID.get(itemID, None)
            if state is None:
                oldActivityState = None
                self.stateByDroneID.UpdateLI([[itemID,
                  ownerID,
                  controllerID,
                  activityState,
                  typeID,
                  controllerOwnerID,
                  targetID]], 'droneID')
            else:
                state.ownerID = ownerID
                state.controllerID = controllerID
                state.controllerOwnerID = controllerOwnerID
                oldActivityState = state.activityState
                state.activityState = activityState
                state.targetID = targetID
            sm.ScatterEvent('OnDroneStateChange2', itemID, oldActivityState, activityState)
            return

    def OnDroneActivityChange(self, droneID, activityID, activity):
        if not activity:
            if self.activityByDrone.has_key(droneID):
                del self.activityByDrone[droneID]
        else:
            self.activityByDrone[droneID] = (activity, activityID)

    def OnShipStateUpdate(self, shipState):
        if self.broker.logInfo:
            self.broker.LogInfo('OnModuleAttributeChange', shipState)
        for moduleID, moduleState in shipState.iteritems():
            sm.ScatterEvent('OnModuleAttributeChange', *moduleState)

    def OnDamageStateChange(self, shipID, damageState):
        if self.broker.logInfo:
            if util.IsFullLogging():
                self.broker.LogInfo('OnDamageStateChange', shipID, damageState)
            else:
                self.broker.LogInfo('OnDamageStateChange')
        shield = damageState[0]
        self.damageState[shipID] = (damageState, blue.os.GetSimTime())
        sm.ScatterEvent('OnDamageStateChange', shipID, self.GetDamageState(shipID))

    def OnFleetDamageStateChange(self, shipID, damageState):
        if self.broker.logInfo:
            self.broker.LogInfo('OnFleetDamageStateChange', shipID, damageState)
        self.damageState[shipID] = (damageState, blue.os.GetSimTime())
        sm.ScatterEvent('OnFleetDamageStateChange', shipID, self.GetDamageState(shipID))

    def OnSpecialFX(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration=-1, repeat=None, startTime=None, timeFromStart=0, graphicInfo=None):
        if isinstance(moduleID, collections.Iterable):
            for m in moduleID:
                sm.ScatterEvent('OnSpecialFX', shipID, m, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration, repeat, startTime, timeFromStart, graphicInfo)

        else:
            sm.ScatterEvent('OnSpecialFX', shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration, repeat, startTime, timeFromStart, graphicInfo)

    def ScatterEwars(self, shipID, moduleID, moduleTypeID, targetID, otherTypeID, guid, isOffensive, start, active, duration=-1, repeat=None, startTime=None, timeFromStart=0, graphicInfo=None):
        if isinstance(moduleID, collections.Iterable):
            for m in moduleID:
                sm.ScatterEvent('OnEwarOnConnect', shipID, m, moduleTypeID, targetID)

        else:
            sm.ScatterEvent('OnEwarOnConnect', shipID, moduleID, moduleTypeID, targetID)

    def OnSovereigntyChanged(self, *args):
        sm.ScatterEvent('OnSovereigntyChanged', *args)

    def GetInvItem(self, id):
        return self.slimItems.get(id, None)

    def OnAudioActivated(self):
        for ball in self.balls.itervalues():
            if ball and hasattr(ball, 'SetupAmbientAudio'):
                ball.SetupAmbientAudio()

    def OnActivatingWarp(self, srcID, stamp):
        ball = self.GetBall(srcID)
        if ball is not None:
            if hasattr(ball, 'EnterWarp'):
                ball.EnterWarp()
        return

    def OnDeactivatingWarp(self, srcID, stamp):
        ball = self.GetBall(srcID)
        if ball is not None:
            if hasattr(ball, 'ExitWarp'):
                ball.ExitWarp()
        return

    def GetSpewContainerManager(self):
        return self.spewContainerManager

    def IsBallVisible(self, ballID):
        if not self.ego:
            return False
        elif ballID == self.ego:
            return True
        else:
            try:
                distance = self.GetSurfaceDist(self.ego, ballID)
                if distance is not None and distance < VISIBILITY_RANGE:
                    return True
                return False
            except RuntimeError:
                return False

            return

    def GetBallsInRange(self, fromID, radius):
        balls = []
        for ballID in self.balls.iterkeys():
            if ballID == fromID:
                continue
            distance = self.GetSurfaceDist(fromID, ballID)
            if distance is not None and distance < radius:
                balls.append(ballID)

        return balls

    def GetComponentRegistry(self):
        return self.componentRegistry