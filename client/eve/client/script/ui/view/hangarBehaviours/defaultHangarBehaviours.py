# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\view\hangarBehaviours\defaultHangarBehaviours.py
import geo2
import trinity
from baseHangarBehaviours import BaseHangarCameraBehaviour, BaseHangarShipBehaviour, BaseHangarTrafficBehaviour
import evecamera
import eveHangar.hangar as hangarUtil

class DefaultHangarCameraBehaviour(BaseHangarCameraBehaviour):
    CAMERA_ANIMATION_DURATION = 2.0

    def __init__(self, layer):
        super(DefaultHangarCameraBehaviour, self).__init__(layer)
        self.hangarMaxZoom = 2050.0
        self.hangarMinZoom = 10.0
        self.defaultCameraPos = (0, 600, -500)
        self.defaultCameraLookAt = (0, 500, 0)

    def SetupCamera(self):
        super(DefaultHangarCameraBehaviour, self).SetupCamera()
        self.camera.SetDefaultHangarCamera()
        self.hangarMinZoom = 2.0 * self.camera.nearClip

    def RepositionCamera(self, model, typeID, cameraAnimationDuration=CAMERA_ANIMATION_DURATION):
        self.camera.maxZoom = max(self.hangarMinZoom, 1.5 * model.boundingSphereRadius)
        self.camera.minZoom = self.hangarMaxZoom
        optimalZoom = min(self.hangarMaxZoom, max(self.hangarMinZoom, 3.0 * model.boundingSphereRadius))
        oldZoom = min(self.camera.GetZoomDistance(), 5.0 * optimalZoom)
        lookDir = self.camera.GetLookAtDirection()
        newZoom = min(self.hangarMaxZoom, max(optimalZoom, oldZoom))
        newLookAtPos = model.translationCurve.value
        newCameraPos = geo2.Vec3Add(newLookAtPos, geo2.Vec3Scale(lookDir, newZoom))
        self.camera.MoveTo(newCameraPos, newLookAtPos, cameraAnimationDuration)
        return cameraAnimationDuration

    def CleanUp(self):
        if self.camera is not None:
            self.camera.StopEyeAndAtAnimation()
        self.camera = None
        return

    def _StopCameraZoom(self, itemID):
        self.camera.LookAt(itemID)


class DefaultHangarShipBehaviour(BaseHangarShipBehaviour):

    def SetAnchorPoint(self, hangarScene):
        self.shipAnchorPoint = (0.0, hangarUtil.SHIP_FLOATING_HEIGHT, 0.0)

    def PlaceShip(self, model, typeID):
        center = model.boundingSphereCenter
        trinity.WaitForResourceLoads()
        localBB = model.GetLocalBoundingBox()
        initialPos = (-center[0], 0.0, -center[2])
        yDelta = min(BaseHangarShipBehaviour.MIN_SHIP_BOBBING_HALF_DISTANCE, model.boundingSphereRadius * 0.05)
        delta = (0.0, yDelta, 0.0)
        bobTime = max(BaseHangarShipBehaviour.MIN_SHIP_BOBBING_TIME, model.boundingSphereRadius)
        bobTime = min(bobTime, BaseHangarShipBehaviour.MAX_SHIP_BOBBING_TIME)
        self.ApplyShipBobbing(model, initialPos, delta, bobTime)
        model.translationCurve = trinity.TriVectorCurve()
        model.translationCurve.value = geo2.Vec3Subtract(self.shipAnchorPoint, (0.0, localBB[0][1], 0.0))


class DefaultHangarTrafficBehaviour(BaseHangarTrafficBehaviour):

    def __init__(self):
        super(DefaultHangarTrafficBehaviour, self).__init__()
        self.hangarTraffic = hangarUtil.HangarTraffic()

    def Setup(self, scene):
        self.hangarTraffic.SetupScene(scene)

    def CleanUp(self):
        if self.hangarTraffic:
            self.hangarTraffic.CleanupScene()
        self.hangarTraffic = None
        return