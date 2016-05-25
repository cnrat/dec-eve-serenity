# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\hangarView.py
import telemetry
from billboards import get_billboard_fallback_image, get_billboard_video_path
import const
import uicls
import uthread
import evetypes
import trinity
import blue
from eveSpaceObject import spaceobjaudio
from videoplayer import playlistresource
from eve.client.script.ui.services.viewStateSvc import View
from hangarBehaviours import capitalHangarBehaviours, defaultHangarBehaviours
from eve.client.script.parklife.sceneManagerConsts import SCENE_TYPE_SPACE
from eve.client.script.ui.view.viewStateConst import ViewState
from eveSpaceObject import spaceobjanimation
AMARR_NORMAL_HANGAR_SIZE = 'AMARR_NORMAL'
CALDARI_NORMAL_HANGAR_SIZE = 'CALDARI_NORMAL'
GALLENTE_NORMAL_HANGAR_SIZE = 'GALLENTE_NORMAL'
MINMATAR_NORMAL_HANGAR_SIZE = 'MINMTAR_NORMAL'
CITADEL_NORMAL_HANGAR_SIZE = 'CITADEL_NORMAL'
CITADEL_CAPITAL_HANGAR_SIZE = 'CITADEL_LARGE'
EXIT_AUDIO_EVENT_FOR_HANGAR_TYPE = {AMARR_NORMAL_HANGAR_SIZE: 'music_switch_race_amarr',
 CALDARI_NORMAL_HANGAR_SIZE: 'music_switch_race_caldari',
 GALLENTE_NORMAL_HANGAR_SIZE: 'music_switch_race_gallente',
 MINMATAR_NORMAL_HANGAR_SIZE: 'music_switch_race_minmatar',
 CITADEL_CAPITAL_HANGAR_SIZE: 'music_switch_race_caldari',
 CITADEL_NORMAL_HANGAR_SIZE: 'music_switch_race_caldari'}
ALL_DEFAULT_BEHAVIOURS = (defaultHangarBehaviours.DefaultHangarCameraBehaviour, defaultHangarBehaviours.DefaultHangarShipBehaviour, defaultHangarBehaviours.DefaultHangarTrafficBehaviour)
ALL_CAPITAL_BEHAVIOURS = (capitalHangarBehaviours.CapitalHangarCameraBehaviour, capitalHangarBehaviours.CapitalHangarShipBehaviour, capitalHangarBehaviours.CapitalHangarTrafficBehaviour)
HANGAR_BEHAVIOURS = {AMARR_NORMAL_HANGAR_SIZE: ALL_DEFAULT_BEHAVIOURS,
 CALDARI_NORMAL_HANGAR_SIZE: ALL_DEFAULT_BEHAVIOURS,
 GALLENTE_NORMAL_HANGAR_SIZE: ALL_DEFAULT_BEHAVIOURS,
 MINMATAR_NORMAL_HANGAR_SIZE: ALL_DEFAULT_BEHAVIOURS,
 CITADEL_NORMAL_HANGAR_SIZE: ALL_DEFAULT_BEHAVIOURS,
 CITADEL_CAPITAL_HANGAR_SIZE: ALL_CAPITAL_BEHAVIOURS}
HANGAR_GRAPHIC_ID = {AMARR_NORMAL_HANGAR_SIZE: 20273,
 CALDARI_NORMAL_HANGAR_SIZE: 20271,
 GALLENTE_NORMAL_HANGAR_SIZE: 20274,
 MINMATAR_NORMAL_HANGAR_SIZE: 20272,
 CITADEL_NORMAL_HANGAR_SIZE: 21259,
 CITADEL_CAPITAL_HANGAR_SIZE: 21260}
USE_CITADEL_HANGAR = False

def ShipNeedsBigHangar(shipTypeID):
    typeGroup = evetypes.GetGroupID(shipTypeID)
    return typeGroup in (const.groupSupercarrier, const.groupTitan)


def GetHangarType(stationTypeID, shipTypeID):
    if USE_CITADEL_HANGAR or evetypes.GetCategoryID(stationTypeID) == const.categoryStructure:
        hangarType = CITADEL_NORMAL_HANGAR_SIZE
        if shipTypeID and ShipNeedsBigHangar(shipTypeID):
            hangarType = CITADEL_CAPITAL_HANGAR_SIZE
    else:
        raceID = evetypes.GetRaceID(stationTypeID)
        if raceID == const.raceAmarr:
            hangarType = AMARR_NORMAL_HANGAR_SIZE
        elif raceID == const.raceCaldari:
            hangarType = CALDARI_NORMAL_HANGAR_SIZE
        elif raceID == const.raceGallente:
            hangarType = GALLENTE_NORMAL_HANGAR_SIZE
        elif raceID == const.raceMinmatar:
            hangarType = MINMATAR_NORMAL_HANGAR_SIZE
        else:
            hangarType = GALLENTE_NORMAL_HANGAR_SIZE
    return hangarType


def GetHangarBehaviours(stationTypeID, shipTypeID):
    return HANGAR_BEHAVIOURS[GetHangarType(stationTypeID, shipTypeID)]


def GetHangarGraphicID(stationTypeID, shipTypeID):
    return HANGAR_GRAPHIC_ID[GetHangarType(stationTypeID, shipTypeID)]


class HangarView(View):
    __guid__ = 'viewstate.HangarView'
    __notifyevents__ = ['OnDogmaItemChange',
     'ProcessActiveShipChanged',
     'OnActiveShipSkinChange',
     'OnDamageStateChanged',
     'OnStanceActive']
    __dependencies__ = ['godma',
     'loading',
     'station',
     'invCache',
     't3ShipSvc',
     'sceneManager',
     'clientDogmaIM',
     'skinSvc']
    __overlays__ = {'sidePanels'}
    __layerClass__ = uicls.HangarLayer

    def __init__(self):
        View.__init__(self)
        self.scenePath = ''
        self.activeShipItem = None
        self.activeShipModel = None
        self.activeHangarScene = None
        self.previousShipTypeID = None
        self.generalAudioEntity = None
        self.currentGraphicID = -1
        self.nameOfShipToRemove = None
        self.delayedShipRemovalThread = None
        self.delayedShipAddThread = None
        self.cameraBehaviour = None
        self.shipBehaviour = None
        self.trafficBehaviour = None
        playlistresource.register_resource_constructor('hangarvideos', 1024, 576, playlistresource.shuffled_videos(get_billboard_video_path()), get_billboard_fallback_image())
        return

    def GetActiveShipTypeID(self):
        if self.activeShipItem is None:
            return
        else:
            return self.activeShipItem.typeID

    def GetActiveShipItemID(self):
        if self.activeShipItem is None:
            return
        else:
            return self.activeShipItem.itemID

    @telemetry.ZONE_METHOD
    def ShowView(self, **kwargs):
        View.ShowView(self, **kwargs)
        self.activeShipModel = None
        self.activeShipItem = self.GetShipItemFromHangar(session.shipid)
        ccMethod, scMethod, tcMethod = GetHangarBehaviours(self.GetStationType(), self.GetActiveShipTypeID())
        self.cameraBehaviour = ccMethod(self.layer)
        self.shipBehaviour = scMethod()
        self.trafficBehaviour = tcMethod()
        self.LoadAndSetupScene(self.GetActiveShipTypeID())
        if self.GetActiveShipItemID() is not None and self.GetActiveShipTypeID() is not None:
            self.ReplaceExistingShipModel(self.GetActiveShipItemID(), self.GetActiveShipTypeID())
        else:
            self.LogWarn('Got no active ship item, defaulting to an arbitrary camera position')
            self.cameraBehaviour.PositionCameraAtDefaultPosition()
        settings.user.ui.Set('defaultDockingView', ViewState.Hangar)
        if session.structureid:
            settings.user.ui.Set('defaultStructureView', ViewState.Hangar)
        return

    def LoadAndSetupScene(self, shipTypeID):
        self.activeHangarScene = self.LoadScene(shipTypeID)
        self.StartHangarAnimations(self.activeHangarScene)
        self.cameraBehaviour.SetupCamera()
        self.trafficBehaviour.Setup(self.activeHangarScene)
        self.shipBehaviour.SetAnchorPoint(self.activeHangarScene)

    @telemetry.ZONE_METHOD
    def LoadView(self, change=None, **kwargs):
        self.station.CleanUp()
        self.station.StopAllStationServices()
        self.station.Setup()
        View.LoadView(self, **kwargs)

    @telemetry.ZONE_METHOD
    def UnloadView(self):
        self.layer.camera = None
        self.cameraBehaviour.CleanUp()
        self.trafficBehaviour.CleanUp()
        self.sceneManager.UnregisterScene(ViewState.Hangar)
        if self.delayedShipRemovalThread is not None:
            self.delayedShipRemovalThread.kill()
        if self.delayedShipAddThread is not None:
            self.delayedShipAddThread.kill()
        self.UnActivateSceneObjects()
        return

    def ReloadView(self):
        self.cameraBehaviour.CleanUp()
        self.trafficBehaviour.CleanUp()
        if self.delayedShipRemovalThread is not None:
            self.delayedShipRemovalThread.kill()
        if self.delayedShipAddThread is not None:
            self.delayedShipAddThread.kill()
        sm.GetService('viewState').ActivateView(ViewState.Hangar)
        return

    def UnActivateSceneObjects(self):
        if self.activeHangarScene:
            for obj in self.activeHangarScene.objects[:]:
                self.activeHangarScene.objects.remove(obj)

        self.activeHangarScene = None
        if hasattr(self.activeShipModel, 'animationSequencer'):
            self.activeShipModel.animationSequencer = None
        self.activeShipModel = None
        self.activeShipItem = None
        self.previousShipTypeID = None
        return

    def LoadScene(self, shipTypeID):
        self.currentGraphicID = GetHangarGraphicID(self.GetStationType(), shipTypeID)
        stationGraphic = cfg.graphics.GetIfExists(self.currentGraphicID)
        if stationGraphic is None:
            self.LogError("Could not find a graphic information for graphicID '%s', returning and showing nothing" % self.currentGraphicID)
        scene, camera = self.sceneManager.LoadScene(stationGraphic.graphicFile, registerKey=ViewState.Hangar)
        return scene

    def SetupGeneralAudioEntity(self, model):
        if model is not None and hasattr(model, 'observers'):
            self.generalAudioEntity = spaceobjaudio.SetupAudioEntity(model)
            self.SetupAnimationUpdaterAudio(model)
        return

    def SetupAnimationUpdaterAudio(self, model):
        if hasattr(model, 'animationUpdater'):
            model.animationUpdater.eventListener = self.generalAudioEntity

    def ReplaceExistingShipModel(self, itemID, typeID, playShipSwitchAudio=True, focusCamera=True, cameraAnimationTime=None):
        if self.delayedShipRemovalThread is not None:
            self.delayedShipRemovalThread.kill()
            self.delayedShipRemovalThread = None
        if self.delayedShipAddThread is not None:
            self.delayedShipAddThread.kill()
            self.delayedShipAddThread = None
        newModel = self.shipBehaviour.LoadShipModel(itemID, typeID)
        self.SetupGeneralAudioEntity(newModel)
        self.shipBehaviour.PlaceShip(newModel, typeID)
        if focusCamera:
            if cameraAnimationTime is None:
                delayTime = self.cameraBehaviour.RepositionCamera(newModel, typeID)
            else:
                delayTime = self.cameraBehaviour.RepositionCamera(newModel, typeID, max(0, cameraAnimationTime))
        else:
            delayTime = 0.0
        if self.activeShipModel:
            if self.activeShipModel.boundingSphereRadius < newModel.boundingSphereRadius:
                self.delayedShipRemovalThread = uthread.new(self.DelayedShipRemoval, self.activeShipModel.name, delayTime)
                self.delayedShipAddThread = uthread.new(self.DelayedShipAdd, newModel, delayTime)
            else:
                self.RemoveModelWithNameFromScene(self.activeShipModel.name)
                self.AddModelToScene(newModel)
        else:
            self.AddModelToScene(newModel)
        if playShipSwitchAudio:
            self.generalAudioEntity.SendEvent(unicode('hangar_spin_switch_ship_play'))
        self.previousShipTypeID = typeID
        return

    def DelayedShipRemoval(self, nameOfModelToRemove, delayInSeconds):
        self.nameOfShipToRemove = nameOfModelToRemove
        blue.synchro.Sleep(delayInSeconds * 1000)
        self.RemoveModelWithNameFromScene(nameOfModelToRemove)

    def DelayedShipAdd(self, modelToAdd, delayInSeconds):
        blue.synchro.Sleep(delayInSeconds * 1000)
        self.AddModelToScene(modelToAdd)

    def StartHangarAnimations(self, scene):
        for obj in scene.objects:
            for fx in obj.children:
                if fx.name.startswith('sfx_'):
                    fx.display = True

    def RemoveModelWithNameFromScene(self, modelName):
        if self.activeHangarScene:
            for m in [ o for o in self.activeHangarScene.objects if o.name == modelName ]:
                self.activeHangarScene.objects.remove(m)

    def AddModelToScene(self, model):
        if self.activeHangarScene and model:
            self.activeHangarScene.objects.append(model)
        self.activeShipModel = model

    def GetStationType(self):
        if session.structureid:
            return self.invCache.GetInventory(const.containerStructure).GetTypeID()
        else:
            return eve.stationItem.stationTypeID

    def GetShipItemFromHangar(self, shipID):
        hangarInv = self.invCache.GetInventory(const.containerHangar)
        hangarItems = hangarInv.List(const.flagHangar)
        for each in hangarItems:
            if each.itemID == shipID and each.categoryID == const.categoryShip:
                return each

        return None

    @telemetry.ZONE_METHOD
    def StartExitAnimation(self):
        if self.activeHangarScene is not None:
            for curveSet in self.activeHangarScene.curveSets:
                if curveSet.name == 'Undock':
                    curveSet.scale = 1.0
                    curveSet.PlayFrom(0.0)
                    break

        return

    @telemetry.ZONE_METHOD
    def StopExitAnimation(self):
        if self.activeHangarScene is not None:
            for curveSet in self.activeHangarScene.curveSets:
                if curveSet.name == 'Undock':
                    curveSet.scale = -1.0
                    curveSet.PlayFrom(curveSet.GetMaxCurveDuration())
                    break

        return

    def StartExitAudio(self):
        audioService = sm.GetService('audio')
        hangarType = GetHangarType(self.GetStationType(), self.GetActiveShipTypeID())
        audioService.SendUIEvent(EXIT_AUDIO_EVENT_FOR_HANGAR_TYPE[hangarType])
        audioService.SendUIEvent('transition_undock_play')

    def StopExitAudio(self):
        sm.GetService('audio').SendUIEvent('transition_undock_cancel')

    def ProcessActiveShipChanged(self, shipID, oldShipID):
        if shipID == oldShipID:
            return
        else:
            newShipItem = self.GetShipItemFromHangar(shipID)
            if newShipItem is None:
                return
            self.activeShipItem = newShipItem
            if self.currentGraphicID != GetHangarGraphicID(self.GetStationType(), self.GetActiveShipTypeID()):
                self.ReloadView()
                return
            self.ReplaceExistingShipModel(self.GetActiveShipItemID(), self.GetActiveShipTypeID())
            return

    def OnStanceActive(self, shipID, stanceID):
        if self.activeShipModel is not None:
            spaceobjanimation.SetShipAnimationStance(self.activeShipModel, stanceID)
        return

    def OnActiveShipSkinChange(self, itemID, skinID):
        if self.shipBehaviour.ShouldSwitchSkin(skinID) and itemID == self.GetActiveShipItemID():
            self.activeShipItem = self.GetShipItemFromHangar(itemID)
            self.ReplaceExistingShipModel(self.GetActiveShipItemID(), self.GetActiveShipTypeID(), playShipSwitchAudio=False, focusCamera=False)

    def OnDamageStateChanged(self, itemID):
        if self.GetActiveShipItemID() == itemID:
            self.shipBehaviour.SetShipDamage(itemID, self.activeShipModel)

    def OnDogmaItemChange(self, item, change):
        if item.locationID == change.get(const.ixLocationID, None) and item.flagID == change.get(const.ixFlag):
            return
        else:
            if item.flagID in const.subSystemSlotFlags:
                self.ReplaceExistingShipModel(self.activeShipItem.itemID, self.activeShipItem.typeID, playShipSwitchAudio=False, focusCamera=False)
                self.cameraBehaviour.RepositionCamera(self.activeShipModel, self.activeShipItem.typeID, cameraAnimationDuration=0.5)
            else:
                self.shipBehaviour.FitTurrets(self.activeShipItem.itemID, self.activeShipItem.typeID, self.activeShipModel)
            return