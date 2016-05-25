# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\baseCamera.py
import math
from eve.client.script.ui.camera.cameraUtil import GetBall, GetBallPosition, GetDurationByDistance, IsNanVector3, IsInfVector3, GetCameraInertiaMultiplier
from logmodule import LogException
import trinity
import geo2
import uthread
import blue
import evegraphics.settings as gfxsettings
K_ZOOMPOWER = 9

class Camera(object):
    __typename__ = None
    __notifyevents__ = ['OnSetDevice']
    name = 'util.Camera'
    default_fov = 1.0
    default_nearClip = 6.0
    default_farClip = 10000000.0
    default_eyePosition = (0, 500, 1000)
    default_atPosition = (0, 0, 0)
    default_upDirection = (0, 1, 0)
    maxFov = 1.5
    minFov = 0.2
    kZoomSpeed = 10.0
    kZoomStopDist = 1e-05
    maxZoom = 100
    minZoom = 10000
    kFovSpeed = 10.0
    kFovStopDist = 0.001
    kOrbitSpeed = 5.0
    kOrbitStopAngle = 0.0001
    kMinPitch = 0.05
    kMaxPitch = math.pi - kMinPitch
    kPanSpeed = 5.0
    kPanStopDist = 0.001

    def __init__(self):
        sm.RegisterNotify(self)
        self._fov = self.default_fov
        self._nearClip = self.default_nearClip
        self._farClip = self.default_farClip
        self._eyePosition = self.default_eyePosition
        self._atPosition = self.default_atPosition
        self._upDirection = self.default_upDirection
        self.panTarget = None
        self.panUpdateThread = None
        self.zoomTarget = None
        self.zoomUpdateThread = None
        self.orbitTarget = None
        self.orbitUpdateThread = None
        self.fovTarget = None
        self.fovUpdateThread = None
        self._fovOffset = 0.0
        self._eyeOffset = None
        self._atOffset = None
        self._eyeAndAtOffset = None
        self._atTransitOffset = None
        self._eyeTransitOffset = None
        self._effectOffset = None
        self.centerOffset = None
        self.isActive = False
        self._transitDoneTime = None
        self.viewMatrix = trinity.TriView()
        self.projectionMatrix = trinity.TriProjection()
        self.updateThread = uthread.new(self.UpdateThread)
        return

    def UpdateThread(self):
        while self.isActive:
            self._Update()
            blue.synchro.Yield()

        self.updateThread = None
        return

    def _Update(self):
        self._eyeOffset = None
        self._atOffset = None
        self._eyeAndAtOffset = None
        self.Update()
        self.UpdateProjection()
        self.UpdateView()
        return

    def Update(self):
        self._UpdateTransitOffset()
        self._UpdateEffectOffset()

    def _UpdateTransitOffset(self):
        if self._atTransitOffset:
            self._AddToAtOffset(self._atTransitOffset)
        if self._eyeTransitOffset:
            self._AddToEyeOffset(self._eyeTransitOffset)

    def OnSetDevice(self, *args):
        if self.isActive:
            self.UpdateProjection()

    def OnActivated(self, **kwargs):
        self.isActive = True
        self.Update()
        if not self.updateThread:
            self.updateThread = uthread.new(self.UpdateThread)

    def OnDeactivated(self):
        self.isActive = False
        self.StopAnimations()
        self.StopUpdateThreads()
        if self.updateThread:
            self.updateThread.kill()
            self.updateThread = None
        self.OnTransitEnd()
        self._eyeAndAtOffset = None
        self._atOffset = None
        self._eyeOffset = None
        return

    def UpdateProjection(self):
        aspectRatio = uicore.uilib.desktop.width / float(uicore.uilib.desktop.height)
        fov = self._fov - self._fovOffset
        if fov <= 0.0:
            fov = 1.0
            self.ResetCameraPosition()
            LogException('Camera: FOV Set to <= 0.0')
        if self.centerOffset:
            self._UpdateProjectionOffset(aspectRatio, fov)
        else:
            self._UpdateProjectionFov(aspectRatio, fov)

    def _UpdateProjectionFov(self, aspectRatio, fov):
        if aspectRatio > 1.6:
            fov *= 1.6 / aspectRatio
        self.projectionMatrix.PerspectiveFov(fov, aspectRatio, self._nearClip, self._farClip)

    def _UpdateProjectionOffset(self, aspectRatio, fov):
        tanFov = math.tan(fov / 2.0)
        k = 1.6 / aspectRatio if aspectRatio > 1.6 else 1.0
        dX = k * aspectRatio * self._nearClip * tanFov
        dY = k * self._nearClip * tanFov
        left = -dX + dX * self.centerOffset
        right = dX + dX * self.centerOffset
        top = dY
        bottom = -dY
        self.projectionMatrix.PerspectiveOffCenter(left, right, bottom, top, self._nearClip, self._farClip)

    def UpdateView(self):
        self.viewMatrix.SetLookAtPosition(self.eyePosition, self.atPosition, self._upDirection)

    def OffsetAtPosition(self, atPosition):
        if self._atOffset:
            atPosition = geo2.Vec3AddD(atPosition, self._atOffset)
        if self._eyeAndAtOffset:
            atPosition = geo2.Vec3AddD(atPosition, self._eyeAndAtOffset)
        return atPosition

    def OffsetEyePosition(self, eyePosition):
        if self._eyeOffset:
            eyePosition = geo2.Vec3AddD(eyePosition, self._eyeOffset)
        if self._eyeAndAtOffset:
            eyePosition = geo2.Vec3AddD(eyePosition, self._eyeAndAtOffset)
        return eyePosition

    def _AddToEyeOffset(self, offset):
        if IsInfVector3(offset) or IsNanVector3(offset):
            LogException('Camera: Attempting to assign an invalid eyeOffset value: %s, %s' % (repr(offset), self))
        if not self._eyeOffset:
            self._eyeOffset = offset
        else:
            self._eyeOffset = geo2.Vec3AddD(self._eyeOffset, offset)

    def _AddToAtOffset(self, offset):
        if IsInfVector3(offset) or IsNanVector3(offset):
            LogException('Camera: Attempting to assign an invalid atOffset value: %s, %s' % (repr(offset), self))
        if not self._atOffset:
            self._atOffset = offset
        else:
            self._atOffset = geo2.Vec3AddD(self._atOffset, offset)

    def SetEffectOffset(self, offset):
        self._effectOffset = offset

    def _UpdateEffectOffset(self):
        if self._effectOffset:
            self._AddToEyeAndAtOffset(self._effectOffset)

    def _AddToEyeAndAtOffset(self, offset):
        if IsInfVector3(offset) or IsNanVector3(offset):
            LogException('Camera: Attempting to assign an invalid eyeAndAtOffset value: %s, %s' % (repr(offset), self))
        if not self._eyeAndAtOffset:
            self._eyeAndAtOffset = offset
        else:
            self._eyeAndAtOffset = geo2.Vec3Add(self._eyeAndAtOffset, offset)

    def GetXAxis(self):
        t = self.viewMatrix.transform
        return (t[0][0], t[1][0], t[2][0])

    def GetYAxis(self):
        t = self.viewMatrix.transform
        return (t[0][1], t[1][1], t[2][1])

    def GetZAxis(self):
        t = self.viewMatrix.transform
        return (t[0][2], t[1][2], t[2][2])

    def SetViewVector(self, viewVector):
        self.StopUpdateThreads()
        atPosition = self.GetAtPosition()
        eyePosition = self.GetEyePosition()
        eyePositionLocal = geo2.Subtract(atPosition, eyePosition)
        eyeDistance = geo2.Vec3Length(eyePositionLocal)
        newEyePosition = geo2.Vec3Scale(viewVector, eyeDistance)
        self.eyePosition = geo2.Vec3Add(newEyePosition, atPosition)
        if not self.isActive:
            self.Update()

    def GetViewVector(self):
        return self.GetLookAtDirection()

    def GetYaw(self):
        x, _, z = self.GetLookAtDirection()
        return -(math.atan2(z, x) + math.pi / 2)

    def GetPitch(self):
        x, y, z = self.GetLookAtDirection()
        return math.atan2(math.sqrt(z ** 2 + x ** 2), -y) + math.pi / 2

    def GetRotationQuat(self):
        yaw = self.GetYaw()
        pitch = self.GetPitch()
        return geo2.QuaternionRotationSetYawPitchRoll(yaw, pitch, 0.0)

    def GetLookAtDirection(self):
        return geo2.Vec3Direction(self._eyePosition, self.GetZoomToPoint())

    def GetLookAtDirectionWithOffset(self):
        eyePos = geo2.Vec3AddD(self._eyePosition, self._eyeOffset) if self._eyeOffset else self._eyePosition
        atPos = geo2.Vec3AddD(self._atPosition, self._atOffset) if self._atOffset else self._atPosition
        return geo2.Vec3Direction(eyePos, atPos)

    def Pan(self, dx=0, dy=0, dz=0):
        if self.panTarget is None:
            self.panTarget = geo2.Vector(0, 0, 0)
        if dx:
            self._AddToPanTarget(dx, self.GetXAxis())
        if dy:
            self._AddToPanTarget(dy, self.GetYAxis())
        if dz:
            self._AddToPanTarget(dz, self.GetZAxis())
        if not self.panUpdateThread:
            self.panUpdateThread = uthread.new(self.PanUpdateThread)
        return

    def _AddToPanTarget(self, dx, axis):
        self.panTarget = geo2.Vec3Add(self.panTarget, geo2.Scale(axis, dx))

    def PanTo(self, diff):
        self.panTarget = geo2.Vector(*diff)
        if not self.panUpdateThread:
            self.panUpdateThread = uthread.new(self.PanUpdateThread)

    def PanAxis(self, axis, amount):
        if self.panTarget is None:
            self.panTarget = geo2.Vector(0, 0, 0)
        self._AddToPanTarget(amount, axis)
        if not self.panUpdateThread:
            self.panUpdateThread = uthread.new(self.PanUpdateThread)
        return

    def PanUpdateThread(self):
        try:
            while True:
                if self.panTarget is None:
                    break
                distLeft = geo2.Vec3LengthD(self.panTarget)
                if distLeft == 0:
                    break
                if distLeft < self.kPanStopDist:
                    dist = 1.0
                else:
                    dist = min(1.0, self._GetPanSpeed() / blue.os.fps)
                toMove = geo2.Vec3ScaleD(self.panTarget, dist)
                self.SetEyePosition(geo2.Vec3Add(self._eyePosition, toMove))
                self.SetAtPosition(geo2.Vec3Add(self._atPosition, toMove))
                self.panTarget = geo2.Vec3SubtractD(self.panTarget, toMove)
                if dist == 1.0:
                    break
                blue.synchro.Yield()

        finally:
            self.panUpdateThread = None
            self.panTarget = None

        return

    def IsZoomedOutCompletely(self):
        zoomValue = self.GetZoomValue()
        return zoomValue > 1.0 - self.kZoomStopDist

    def IsZoomedInCompletely(self):
        zoomValue = self.GetZoomValue()
        return zoomValue == 0.0

    def GetZoomValue(self):
        if self.zoomTarget is not None:
            zoomValue = self.zoomTarget
        else:
            zoomValue = self.GetZoomProportion()
        return zoomValue

    def Zoom(self, dz):
        if dz < 0 and self.IsZoomedInCompletely():
            return
        elif dz > 0 and self.IsZoomedOutCompletely():
            return
        else:
            if self.zoomTarget is None:
                self.zoomTarget = self.GetZoomProportion()
            self.zoomTarget += 0.3 * dz
            self.zoomTarget = self._ClampZoomProp(self.zoomTarget)
            if not self.zoomUpdateThread:
                self.zoomUpdateThread = uthread.new(self.ZoomUpdateThread)
            return

    def SetZoomTarget(self, proportion):
        self.zoomTarget = self._ClampZoomProp(proportion)
        if not self.zoomUpdateThread:
            self.zoomUpdateThread = uthread.new(self.ZoomUpdateThread)

    def ZoomUpdateThread(self):
        try:
            zoomProp = self.GetZoomProportion()
            while True:
                if self.zoomTarget is None:
                    break
                distLeft = self.zoomTarget - zoomProp
                if not distLeft:
                    break
                distProp = self.GetZoomDistance() / self.minZoom
                zoomSpeed = self._GetZoomSpeed()
                moveProp = zoomSpeed / blue.os.fps
                if math.fabs(distLeft) < self.kZoomStopDist:
                    moveProp *= self.kZoomStopDist / math.fabs(distLeft)
                moveProp = min(moveProp, 1.0)
                zoomProp += distLeft * moveProp
                self.SetZoom(zoomProp)
                if moveProp == 1.0:
                    break
                blue.synchro.Yield()

        finally:
            self.zoomUpdateThread = None
            self.zoomTarget = None

        return

    def _ClampZoomProp(self, ret):
        minZoomProp = self.GetMinZoomProp()
        return max(minZoomProp, min(ret, 1.0))

    def GetMinZoomProp(self):
        return 0.2 + self.maxZoom / self.minZoom

    def GetZoomDistanceByZoomProportion(self, zoomProp):
        return self.maxZoom + zoomProp ** K_ZOOMPOWER * (self.minZoom - self.maxZoom)

    def GetZoom(self):
        return 1.0 - self.GetZoomProportion()

    def SetZoom(self, proportion):
        proportion = self._ClampZoomProp(proportion)
        direction = self.GetLookAtDirection()
        distance = self.GetZoomDistanceByZoomProportion(proportion)
        zoomVec = geo2.Vec3Scale(direction, distance)
        self.SetEyePosition(geo2.Vec3Add(self.GetZoomToPoint(), zoomVec))

    zoom = property(GetZoom, SetZoom)

    def GetZoomToPoint(self):
        if self._atTransitOffset:
            return geo2.Vec3Add(self._atPosition, self._atTransitOffset)
        return self._atPosition

    def SetZoomDistance(self, distance):
        zoomVec = geo2.Vec3Scale(self.GetLookAtDirection(), distance)
        self.SetEyePosition(geo2.Vec3Add(self._atPosition, zoomVec))

    def FovZoom(self, dz):
        if self.fovTarget is not None:
            self.SetFovTarget(self.fovTarget + dz)
        else:
            self.SetFovTarget(self.fov + dz)
        return

    def SetFovTarget(self, value):
        if self.fov == value:
            return
        if math.fabs(self.fov - value) < 0.001 and not self.fovUpdateThread:
            self.SetFov(value)
        else:
            self.fovTarget = self._EnforceMinMaxFov(value)
            if not self.fovUpdateThread:
                self.fovUpdateThread = uthread.new(self.FovUpdateThread)

    def FovUpdateThread(self):
        try:
            while True:
                if self.fovTarget is None:
                    break
                distLeft = self.fovTarget - self.fov
                if not distLeft:
                    break
                moveProp = self._GetFovSpeed() / blue.os.fps
                if math.fabs(distLeft) < self.kFovStopDist:
                    moveProp *= self.kFovStopDist / math.fabs(distLeft)
                moveProp = min(moveProp, 1.0)
                fov = self.fov + moveProp * distLeft
                self.fov = self._EnforceMinMaxFov(fov)
                if fov != self.fov:
                    break
                if moveProp == 1.0:
                    break
                blue.synchro.Yield()

        finally:
            self.fovUpdateThread = None
            self.fovTarget = None

        return

    def _GetFovSpeed(self):
        multiplier = GetCameraInertiaMultiplier()
        return self.kFovSpeed * multiplier

    def _EnforceMinMaxFov(self, value):
        if value >= self.maxFov:
            return self.maxFov
        if value <= self.minFov:
            return self.minFov
        return value

    def StopUpdateThreads(self):
        self.zoomTarget = None
        self.panTarget = None
        self.orbitTarget = None
        self.fovTarget = None
        return

    def GetZoomDistance(self):
        dist = geo2.Vec3Distance(self._eyePosition, self.GetZoomToPoint())
        if math.isinf(dist):
            LogException('Error: Infinite camera distance:%s, %s' % (repr(dist), self))
            self.ResetCameraPosition()
            return 1.0
        return dist

    def GetZoomProportion(self):
        zoomProp = self.GetZoomProportionUnfiltered()
        return self._ClampZoomProp(zoomProp)

    def GetZoomProportionUnfiltered(self):
        zoomDist = max(self.maxZoom, self.GetZoomDistance())
        zoomProp = self.GetZoomProportionByZoomDistance(zoomDist)
        return zoomProp

    def GetZoomProportionByZoomDistance(self, zoomDist):
        zoomProp = (zoomDist - self.maxZoom) / (self.minZoom - self.maxZoom)
        return zoomProp ** (1.0 / K_ZOOMPOWER)

    def SetMaxZoom(self, value):
        if value >= self.minZoom:
            LogException('Camera: Cannot set maxZoom to a value larger than minZoom: value=%s, %s' % (value, self))
        else:
            self.maxZoom = value

    def SetMinZoom(self, value):
        if value <= self.maxZoom:
            LogException('Camera: Cannot set minZoom to a value smaller than minZoom: value=%s, %s' % (value, self))
        else:
            self.minZoom = value

    def Orbit(self, dx=0, dy=0):
        if not self.orbitTarget:
            self.orbitTarget = (0, self.GetAngleLookAtToUpDirection())
        if gfxsettings.Get(gfxsettings.UI_CAMERA_INVERT_Y):
            dy *= -1
        yaw = self.orbitTarget[0] - dx
        pitch = self.orbitTarget[1] - dy / 2.0
        pitch = max(self.kMinPitch, min(pitch, self.kMaxPitch))
        self.orbitTarget = [yaw, pitch]
        if not self.orbitUpdateThread:
            self.orbitUpdateThread = uthread.new(self.OrbitUpdateThread)

    def OrbitUpdateThread(self):
        try:
            while True:
                if self.orbitTarget is None:
                    break
                vLookAt = self.GetLookAtDirectionWithOffset()
                currPitch = self.GetAngleLookAtToUpDirection()
                offset = self.GetOrbitPoint()
                self.eyePosition = geo2.Subtract(self._eyePosition, offset)
                yawRemaining = self._UpdateYaw()
                pitchRemaining = self._UpdatePitch(currPitch, vLookAt)
                self.SetEyePosition(geo2.Add(self._eyePosition, offset))
                if not pitchRemaining and not yawRemaining:
                    break
                blue.synchro.Yield()

        finally:
            self.orbitUpdateThread = None
            self.orbitTarget = None

        return

    def GetOrbitPoint(self):
        if self._atOffset:
            offset = geo2.Vec3Add(self._atPosition, self._atOffset)
        else:
            offset = self._atPosition
        return offset

    def _UpdatePitch(self, currPitch, vLookAt):
        targetPitch = self.orbitTarget[1]
        pitchRemaining = currPitch - targetPitch
        if pitchRemaining:
            if math.fabs(pitchRemaining) < self.kOrbitStopAngle:
                pitch = pitchRemaining
                pitchRemaining = None
            else:
                pitch = pitchRemaining * self._GetOrbitSpeed()
            axis = geo2.Vec3Cross(vLookAt, self.upDirection)
            rotPitch = geo2.MatrixRotationAxis(axis, pitch)
            self.SetEyePosition(geo2.Vec3Transform(self._eyePosition, rotPitch))
        return pitchRemaining

    def _GetOrbitSpeed(self):
        multiplier = GetCameraInertiaMultiplier()
        speed = self.kOrbitSpeed * multiplier / blue.os.fps
        return min(1.0, speed)

    def _GetZoomSpeed(self):
        multiplier = GetCameraInertiaMultiplier()
        return self.kZoomSpeed * multiplier

    def _GetPanSpeed(self):
        multiplier = GetCameraInertiaMultiplier()
        return self.kPanSpeed * multiplier

    def _UpdateYaw(self):
        yawRemaining = self.orbitTarget[0]
        if yawRemaining:
            if math.fabs(yawRemaining) < self.kOrbitStopAngle:
                yaw = yawRemaining
                yawRemaining = None
            else:
                yaw = yawRemaining * self._GetOrbitSpeed()
            rotYaw = geo2.MatrixRotationAxis(self.upDirection, yaw)
            self.SetEyePosition(geo2.Vec3Transform(self._eyePosition, rotYaw))
            self.orbitTarget[0] -= yaw
        return yawRemaining

    def GetAngleLookAtToUpDirection(self):
        try:
            vLookAt = self.GetLookAtDirectionWithOffset()
            return math.acos(geo2.Vec3Dot(vLookAt, self.upDirection) / (geo2.Vec3Length(vLookAt) * geo2.Vec3Length(self.upDirection)))
        except ValueError:
            return 0.0

    def GetActiveThreads(self):
        return (self.panTarget, self.orbitTarget, self.zoomTarget)

    def Rotate(self, x=0, y=0):
        xAxis = self.GetXAxis()
        yAxis = self.GetYAxis()
        self.atPosition = geo2.Subtract(self._atPosition, self._eyePosition)
        rotY = geo2.MatrixRotationAxis(xAxis, y)
        self.atPosition = geo2.Vec3Transform(self._atPosition, rotY)
        rotX = geo2.MatrixRotationAxis(yAxis, x)
        self.atPosition = geo2.Vec3Transform(self._atPosition, rotX)
        self.atPosition = geo2.Add(self._atPosition, self.eyePosition)

    def GetDistanceFromLookAt(self):
        return geo2.Vec3Distance(self.eyePosition, self.atPosition)

    def LookAt(self, itemID, radius=None):
        ball = GetBall(itemID)
        if not ball:
            return
        if not radius:
            radius = ball.radius * 2
        atPos1 = GetBallPosition(ball)
        direction = self.GetLookAtDirectionWithOffset()
        eyePos1 = geo2.Vec3Add(atPos1, geo2.Vec3Scale(direction, radius))
        duration = GetDurationByDistance(self.eyePosition, eyePos1, 0.3, 0.6)
        self.TransitTo(atPos1, eyePos1, duration=duration)

    def LookAtMaintainDistance(self, itemID):
        self.LookAt(itemID)

    def TransitTo(self, atPosition=None, eyePosition=None, duration=1.0, smoothing=0.1, numPoints=1000, timeOffset=0.0):
        self.Transit(self.atPosition, self.eyePosition, atPosition, eyePosition, duration, smoothing, numPoints, timeOffset)

    def Transit(self, atPos0, eyePos0, atPos1, eyePos1, duration=1.0, smoothing=0.1, numPoints=1000, timeOffset=0.0, callback=None):
        newDir = geo2.Vec3Direction(eyePos1, atPos1)
        self.StopEyeAndAtAnimation()
        if self._atTransitOffset:
            atPos0 = geo2.Vec3Add(atPos0, self._atTransitOffset)
        if self._eyeTransitOffset:
            eyePos0 = geo2.Vec3Add(eyePos0, self._eyeTransitOffset)
        self.SetAtPosition(atPos1)
        self.SetEyePosition(eyePos1)
        self._atTransitOffset = geo2.Vec3Subtract(atPos0, atPos1)
        self._eyeTransitOffset = geo2.Vec3Subtract(eyePos0, eyePos1)
        uicore.animations.MorphVector3(self, '_atTransitOffset', self._atTransitOffset, (0, 0, 0), duration=duration, timeOffset=timeOffset, callback=callback)
        uicore.animations.MorphVector3(self, '_eyeTransitOffset', self._eyeTransitOffset, (0, 0, 0), duration=duration, timeOffset=timeOffset, callback=self.OnTransitEnd)
        self._transitDoneTime = blue.os.GetWallclockTime() + SEC * duration

    def StopEyeAndAtAnimation(self):
        uicore.animations.StopAnimation(self, 'atPosition')
        uicore.animations.StopAnimation(self, 'eyePosition')
        uicore.animations.StopAnimation(self, '_atTransitOffset')
        uicore.animations.StopAnimation(self, '_eyeTransitOffset')
        self.OnTransitEnd()
        self.panTarget = None
        self.orbitTarget = None
        self.zoomTarget = None
        self.fovTarget = None
        return

    def IsInTransit(self):
        return self._transitDoneTime is not None and blue.os.GetWallclockTime() < self._transitDoneTime

    def OnTransitEnd(self):
        self._atTransitOffset = None
        self._eyeTransitOffset = None
        return

    def StopAnimations(self):
        uicore.animations.StopAllAnimations(self)

    def GetFov(self):
        return self._fov

    def SetFov(self, value):
        if math.isnan(value):
            self.ResetCameraPosition()
            raise ValueError('Attempting to assign NaN value')
        self._fov = value

    fov = property(GetFov, SetFov)

    def GetFovOffset(self):
        return self._fovOffset

    def SetFovOffset(self, value):
        if math.isnan(value):
            self.ResetCameraPosition()
            raise ValueError('Attempting to assign NaN value')
        self._fovOffset = value

    fovOffset = property(GetFovOffset, SetFovOffset)

    def GetNearClip(self):
        return self._nearClip

    def SetNearClip(self, value):
        if math.isnan(value):
            self.ResetCameraPosition()
            raise ValueError('Attempting to assign NaN value')
        self._nearClip = value

    nearClip = property(GetNearClip, SetNearClip)

    def GetFarClip(self):
        return self._farClip

    def SetFarClip(self, value):
        if math.isnan(value):
            self.ResetCameraPosition()
            raise ValueError('Attempting to assign NaN value')
        self._farClip = value

    farClip = property(GetFarClip, SetFarClip)

    def GetEyePosition(self):
        return self.OffsetEyePosition(self._eyePosition)

    def SetEyePosition(self, value):
        if IsNanVector3(value) or IsInfVector3(value):
            LogException('Attempting to assign an invalid eyePosition value: %s, %s' % (repr(value), self))
            self.ResetCameraPosition()
        elif value == self._atPosition:
            LogException('Camera: Setting eyePosition to same value as atPosition: %s, %s' % (repr(value), self))
            self.ResetCameraPosition()
        else:
            self._eyePosition = value

    eyePosition = property(GetEyePosition, SetEyePosition)

    def GetAtPosition(self):
        return self.OffsetAtPosition(self._atPosition)

    def SetAtPosition(self, value):
        if IsNanVector3(value) or IsInfVector3(value):
            LogException('Attempting to assign an invalid atPosition value: %s, %s' % (repr(value), self))
            self.ResetCameraPosition()
        elif value == self._eyePosition:
            LogException('Camera: Setting atPosition to same value as eyePosition: %s, %s' % (repr(value), self))
            self.ResetCameraPosition()
        else:
            self._atPosition = value

    atPosition = property(GetAtPosition, SetAtPosition)

    def GetUpDirection(self):
        return self._upDirection

    def SetUpDirection(self, value):

        def IsNanValue(self, value):
            return math.isnan(value[0] or math.isnan(value[1]) or math.isnan(value[2]))

        self._upDirection = geo2.Vec3Normalize(value)

    upDirection = property(GetUpDirection, SetUpDirection)

    def GetTrackItemID(self):
        return None

    def ResetCamera(self, *args):
        pass

    def ResetCameraPosition(self):
        self._atPosition = self.default_atPosition
        self._eyePosition = self.default_eyePosition
        self._fov = self.default_fov
        self.trackTarget = None
        return

    def ProjectWorldToCamera(self, vec):
        return geo2.Vec3Transform(vec, self.viewMatrix.transform)

    def IsInFrontOfCamera(self, vec):
        vec = self.ProjectWorldToCamera(vec)
        return vec[2] < -self.nearClip

    def EnforceMinZoom(self):
        if self.GetZoomDistance() < self.maxZoom:
            self.SetZoom(self.GetMinZoomProp())

    def __repr__(self):
        return '<%s at %s. eyePos=%s, atPos=%s, eyeOffset=%s, atOffset=%s, eyeAndAtOffset=%s, minZoom=%s, maxZoom=%s, isActive=%s, fov=%s>' % (self.__class__.__name__,
         id(self),
         repr(self._eyePosition),
         repr(self._atPosition),
         repr(self._eyeOffset),
         repr(self._atOffset),
         repr(self._eyeAndAtOffset),
         repr(self.minZoom),
         repr(self.maxZoom),
         repr(self.isActive),
         repr(self.fov))