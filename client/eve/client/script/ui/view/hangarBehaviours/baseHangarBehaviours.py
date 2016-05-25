# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\hangarBehaviours\baseHangarBehaviours.py
import evecamera
import evetypes
import trinity
import logging
from inventorycommon.util import IsModularShip
import evegraphics.utils as gfxutils
from eve.common.script.net import eveMoniker
from inventorycommon.typeHelpers import GetAnimationStates
from eveSpaceObject.spaceobjanimation import SetShipAnimationStance, LoadAnimationStates
from eve.client.script.ui.inflight.shipstance import get_ship_stance
from eve.client.script.environment.model.turretSet import TurretSet
log = logging.getLogger(__name__)

class BaseHangarCameraBehaviour(object):

    def __init__(self, layer):
        self.layer = layer
        self.camera = None
        self.log = log
        self.defaultCameraPos = (10, 10, 10)
        self.defaultCameraLookAt = (0, 0, 0)
        return

    def GetCamera(self):
        return self.camera

    def PositionCameraAtDefaultPosition(self):
        self.camera.MoveTo(self.defaultCameraPos, self.defaultCameraLookAt, 1.0)

    def SetupCamera(self):
        hangarCamera = sm.GetService('sceneManager').SetPrimaryCamera(evecamera.CAM_HANGAR)
        if hangarCamera is None:
            hangarCamera = sm.GetService('sceneManager').GetActivePrimaryCamera()
        self.camera = hangarCamera
        self.layer.camera = self.camera
        self.layer.OnActiveCameraChanged(evecamera.CAM_HANGAR)
        return

    def RepositionCamera(self, model, typeID, cameraAnimationDuration=0.0):
        raise NotImplementedError("%s does not implement 'RepositionCamera'", self)

    def CleanUp(self):
        raise NotImplementedError("%s does not implement 'RepositionCamera'", self)


class BaseHangarShipBehaviour(object):
    MIN_SHIP_BOBBING_TIME = 10
    MAX_SHIP_BOBBING_TIME = 300
    MIN_SHIP_BOBBING_HALF_DISTANCE = 100

    def __init__(self):
        self._activeMaterialSetID = None
        self._activeSkinID = None
        self.log = log
        self.skinChangeThread = None
        self.shipAnchorPoint = (0.0, 0.0, 0.0)
        return

    def LoadShipModel(self, itemID, typeID):
        if IsModularShip(typeID):
            model = self._LoadModularShipModel(itemID, typeID)
        else:
            model = self._LoadSOFShipModel(itemID, typeID)
        if getattr(model, 'boosters', None) is not None:
            model.boosters.display = False
        model.name = str(itemID)
        model.FreezeHighDetailMesh()
        self.SetShipDirtLevel(itemID, model)
        self.SetShipKillCounter(itemID, model)
        self.SetupShipAnimation(model, typeID, itemID)
        self.SetShipDamage(itemID, model)
        self.FitTurrets(itemID, typeID, model)
        return model

    def _LoadModularShipModel(self, itemID, typeID):
        raceName = None
        graphicInfo = cfg.graphics.GetIfExists(evetypes.GetGraphicID(typeID))
        if graphicInfo is not None:
            raceName = getattr(graphicInfo, 'sofRaceName', None)
        dogmaItem = sm.GetService('clientDogmaIM').GetDogmaLocation().dogmaItems.get(itemID, None)
        if dogmaItem is None:
            self.log.error('%s._LoadModularShip(itemID = %s, typeID = %s): Trying to show t3 ship which is not in dogma' % (self, itemID, typeID))
            return
        else:
            fittedSubsystems = [ fittedItem for fittedItem in dogmaItem.GetFittedItems().itervalues() if fittedItem.categoryID == const.categorySubSystem ]
            subSystemIds = {item.groupID:item.typeID for item in fittedSubsystems}
            return sm.GetService('t3ShipSvc').GetTech3ShipFromDict(dogmaItem.typeID, subSystemIds, raceName)

    def _LoadSOFShipModel(self, itemID, typeID):
        self._activeSkinID = self.GetShipSkin(itemID, typeID)
        self._activeMaterialSetID = self._activeSkinID.materialSetID if self._activeSkinID is not None else None
        shipDna = gfxutils.BuildSOFDNAFromTypeID(typeID, materialSetID=self._activeMaterialSetID)
        if shipDna is None:
            self.log.error('%s._LoadSOFShip(itemID = %s, typeID = %s): Trying to show a SOF ship that is not in the SOF' % (self, itemID, typeID))
            return
        else:
            return sm.GetService('sofService').spaceObjectFactory.BuildFromDNA(shipDna)

    def SetupShipAnimation(self, model, typeID, itemID):
        if model is None:
            return
        elif not evetypes.Exists(typeID):
            return
        else:
            animationStates = GetAnimationStates(typeID)
            LoadAnimationStates(animationStates, cfg.graphicStates, model, trinity)
            if model.animationSequencer is not None:
                model.animationSequencer.GoToState('normal')
                SetShipAnimationStance(model, get_ship_stance(itemID, typeID))
            return

    def SetShipDirtLevel(self, itemID, model):
        dirtTimeStamp = eveMoniker.GetShipAccess().GetDirtTimestamp(itemID)
        dirtLevel = gfxutils.CalcDirtLevelFromAge(dirtTimeStamp)
        model.dirtLevel = dirtLevel

    def SetShipKillCounter(self, itemID, model):
        killCounter = sm.RemoteSvc('shipKillCounter').GetItemKillCountPlayer(itemID)
        model.displayKillCounterValue = min(killCounter, 999)

    def SetShipDamage(self, itemID, model):
        shipState = sm.GetService('clientDogmaIM').GetDogmaLocation().GetDamageStateEx(itemID)
        if shipState is None:
            self.log.error('%s.SetShipDamage(itemID = %s, model = %s): Got no shipstate from dogma' % (self, itemID, model))
            return
        else:
            shieldState, armorState, hullState = shipState
            if isinstance(shieldState, tuple):
                shieldState = shieldState[0]
            model.SetImpactDamageState(shieldState, armorState, hullState, True)
            return

    def FitTurrets(self, itemID, typeID, model):
        sofFactionName = evetypes.GetSofFactionNameOrNone(typeID)
        if sofFactionName is None:
            graphic = cfg.graphics.GetIfExists(evetypes.GetGraphicID(typeID))
            sofFactionName = getattr(graphic, 'sofFactionName', None)
        TurretSet.FitTurrets(itemID, model, sofFactionName)
        return

    def GetShipSkin(self, itemID, typeID):
        return sm.GetService('skinSvc').GetAppliedSkin(session.charid, itemID, typeID)

    def ShouldSwitchSkin(self, skinID):
        return skinID != getattr(self._activeSkinID, 'skinID', None)

    def SetAnchorPoint(self, hangarScene):
        raise NotImplementedError("%s does not implement 'SetAnchorPoint'", self)

    def PlaceShip(self, model, typeID):
        raise NotImplementedError("%s does not implement 'PlaceShip'", self)

    def ApplyShipBobbing(self, model, initialPosition, deltaPosition, cycleLengthInSec):
        curve = trinity.TriVectorCurve()
        topPosition = (initialPosition[0] + deltaPosition[0], initialPosition[1] + deltaPosition[1], initialPosition[2] + deltaPosition[2])
        bottomPosition = (initialPosition[0] - deltaPosition[0], initialPosition[1] - deltaPosition[1], initialPosition[2] - deltaPosition[2])
        z = (0.0, 0.0, 0.0)
        curve.AddKey(0.0, topPosition, z, z, trinity.TRIINT_HERMITE)
        curve.AddKey(0.5 * cycleLengthInSec, bottomPosition, z, z, trinity.TRIINT_HERMITE)
        curve.AddKey(1.0 * cycleLengthInSec, topPosition, z, z, trinity.TRIINT_HERMITE)
        curve.extrapolation = trinity.TRIEXT_CYCLE
        model.modelTranslationCurve = curve


class BaseHangarTrafficBehaviour(object):

    def __init__(self):
        self.log = log

    def Setup(self, scene):
        raise NotImplementedError("%s does not implement 'Setup'", self)

    def CleanUp(self):
        raise NotImplementedError("%s does not implement 'CleanUp'", self)