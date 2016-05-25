# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\hangarBehaviours\capitalHangarBehaviours.py
import evecamera
import evetypes
import const
import geo2
import trinity
from baseHangarBehaviours import BaseHangarCameraBehaviour, BaseHangarShipBehaviour, BaseHangarTrafficBehaviour
import eveHangar.hangar as hangarUtil
TITAN_CAMERA_POSITION = (9995.4853515625, -2001.05224609375, 10192.3359375)
SUPER_CAPITAL_CAMERA_DIRECTION = (-0.2522106051445007, 0.3255149364471436, 0.8546369075775146)

class CapitalHangarCameraBehaviour(BaseHangarCameraBehaviour):
    CAMERA_ANIMATION_DURATION = 3.0

    def __init__(self, layer):
        super(CapitalHangarCameraBehaviour, self).__init__(layer)
        self.hangarMaxZoom = 15000
        self.hangarMinZoom = 5000
        self.currentShipGroup = const.groupSupercarrier

    def SetupCamera(self):
        super(CapitalHangarCameraBehaviour, self).SetupCamera()
        self.camera.SetSuperCapitalHangarCamera(geo2.Vec3Scale(geo2.Vec3Add(TITAN_CAMERA_POSITION, SUPER_CAPITAL_CAMERA_DIRECTION), 0.75))

    def RepositionCamera(self, model, typeID, cameraAnimationDuration=CAMERA_ANIMATION_DURATION):
        oldModelGroup = self.currentShipGroup
        newLookAtPos = model.translationCurve.value
        if evetypes.GetGroupID(typeID) == const.groupSupercarrier:
            self.MoveToSuperCapitalCameraPosition(model, newLookAtPos, cameraAnimationDuration)
            self.currentShipGroup = const.groupSupercarrier
        else:
            self.MoveToTitanCameraPosition(newLookAtPos, cameraAnimationDuration)
            self.currentShipGroup = const.groupTitan
        if oldModelGroup == self.currentShipGroup:
            return 0.0
        return cameraAnimationDuration

    def MoveToTitanCameraPosition(self, lookAtPos, cameraAnimationDuration):
        self.camera.MoveTo(TITAN_CAMERA_POSITION, lookAtPos, cameraAnimationDuration)

    def MoveToSuperCapitalCameraPosition(self, model, lookAtPos, cameraAnimationDuration):
        optimalZoom = min(self.hangarMaxZoom, max(self.hangarMinZoom, 2.5 * model.boundingSphereRadius))
        newEyePos = geo2.Vec3Scale(SUPER_CAPITAL_CAMERA_DIRECTION, optimalZoom)
        newEyePos = geo2.Vec3Add(newEyePos, lookAtPos)
        self.camera.MoveTo(newEyePos, lookAtPos, cameraAnimationDuration)

    def CleanUp(self):
        if self.camera is not None:
            self.camera.StopEyeAndAtAnimation()
        self.camera = None
        return


class CapitalHangarShipBehaviour(BaseHangarShipBehaviour):

    def SetAnchorPoint(self, hangarScene):
        if hangarScene is None:
            self.log.error('CapitalHangarShipBehaviour.SetAnchorPoint: Setting anchor point when scene is None')
            return
        else:
            eveStations = hangarScene.Find('trinity.EveStation2')
            for stationObject in eveStations:
                anchorPointLocatorSets = [ locatorSet for locatorSet in getattr(stationObject, 'locatorSets', []) if locatorSet.name == 'anchorpoint' ]
                if len(anchorPointLocatorSets) > 0:
                    if len(getattr(anchorPointLocatorSets[0], 'locators', [])) > 0:
                        self.shipAnchorPoint = anchorPointLocatorSets[0].locators[0][0]
                        return

            self.log.warning('CapitalHangarShipBehaviour.SetAnchorPoint: Could not find anchor point')
            return

    def PlaceShip(self, model, typeID):
        model.translationCurve = trinity.TriVectorCurve()
        trinity.WaitForResourceLoads()
        localBB = model.GetLocalBoundingBox()
        width = abs(localBB[0][0])
        if evetypes.GetGroupID(typeID) == const.groupTitan:
            width += 2000
        model.translationCurve.value = geo2.Vec3Add(self.shipAnchorPoint, (width, 0.0, 0.0))
        self.ApplyShipBobbing(model, (0.0, model.translationCurve.value[1], 0.0), (0.0, 250.0, 0.0), model.GetBoundingSphereRadius())


class CapitalHangarTrafficBehaviour(BaseHangarTrafficBehaviour):

    def __init__(self):
        super(CapitalHangarTrafficBehaviour, self).__init__()
        self.hangarTraffic = hangarUtil.HangarTraffic()

    def Setup(self, scene):
        self.hangarTraffic.SetupScene(scene)

    def CleanUp(self):
        if self.hangarTraffic:
            self.hangarTraffic.CleanupScene()
        self.hangarTraffic = None
        return