# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\environment\effects\Warp.py
from math import cos, pow, sqrt, pi, sin
import random
import blue
import destiny
import evecamera
import trinity
import geo2
import uthread
import carbon.common.script.util.logUtil as log
import carbon.common.script.util.mathCommon as mathCommon
from eve.client.script.environment.effects.GenericEffect import ShipEffect, STOP_REASON_DEFAULT
import eve.client.script.environment.effects.effectConsts as effectconsts
import evecamera.shaker as shaker
import evegraphics.settings as gfxsettings
DYNAMIC_WARP_LIGHT_COLOR = (0.270588219165802, 0.6156862378120422, 1.0, 1.0)
STATIC_WARP_LIGHT_COLOR = (0.5647059082984924, 0.9960784316062927, 1.0, 1.0)

class Warping(ShipEffect):
    __guid__ = 'effects.Warping'

    def Prepare(self):
        shipID = self.GetEffectShipID()
        if shipID != session.shipid:
            self.fxSequencer.OnSpecialFX(shipID, None, None, None, None, 'effects.Warping', 0, 0, 0)
            self.fxSequencer.OnSpecialFX(shipID, None, None, None, None, 'effects.WarpOut', 0, 1, 0)
            return
        else:
            ShipEffect.Prepare(self)
            self.AlignToDirection()
            return

    def ModelChangeNotify(self, newModel):
        if newModel is None:
            return
        else:
            self.shipModel = newModel
            for binding in self.curveSet.bindings:
                binding.sourceObject = self.shipModel.speed

            return

    def Start(self, duration):
        if self.gfx is None:
            return
        else:
            self.gfx.display = False
            self.hasExploded = False
            self.hasWind = False
            self.hasMoreCollisions = True
            self.findNext = True
            ShipEffect.Start(self, duration)
            bp = sm.StartService('michelle').GetBallpark()
            shipID = self.GetEffectShipID()
            shipBall = bp.GetBall(shipID)
            self.shipBall = shipBall
            self.shipModel = getattr(shipBall, 'model', None)
            self.shipBall.RegisterModelChangeNotification(self.ModelChangeNotify)
            slimItem = bp.GetInvItem(shipID)
            self.warpSpeedModifier = sm.StartService('godma').GetTypeAttribute(slimItem.typeID, const.attributeWarpSpeedMultiplier)
            if self.warpSpeedModifier is None:
                self.warpSpeedModifier = 1.0
            space = sm.GetService('space')
            self.SetupTunnelBindings()
            self.nextCollision = None
            self.insideSolid = False
            self.destination = space.warpDestinationCache[3]
            self.collisions = []
            self.collisions = self.GetWarpCollisions(shipBall)
            self.ControlFlow('NextCollision')
            uthread.worker('FxSequencer::WarpEffectLoop', self.WarpLoop, shipBall)
            return

    def AddToScene(self, effect):
        scene = self.fxSequencer.GetScene()
        scene.warpTunnel = effect
        self._SetupLightingCurves(scene)

    def RemoveFromScene(self, effect):
        scene = self.fxSequencer.GetScene()
        scene.warpTunnel = None
        self._RemoveLightingCurves(scene)
        return

    def _SetupLightingCurves(self, scene):
        self.lightingCurveSet = trinity.TriCurveSet()
        self.lights = []
        curve = trinity.Tr2ScalarExprCurve()
        curve.expr = 'input3 - input3 * min(max(input1 - input2, 0), 1)'
        curve.input1 = 1
        curve.input2 = 0
        curve.input3 = gfxsettings.SECONDARY_LIGHTING_INTENSITY
        curve.length = 1
        curve.cycle = True
        self.lightingCurveSet.curves.append(curve)

        def FindBinding(curveSet, binding):
            cs = [ x for x in self.gfx.curveSets if x.name == curveSet ][0]
            return [ x for x in cs.bindings if x.name == binding ][0]

        trinity.CreateBinding(self.lightingCurveSet, FindBinding('FadeInCurveSet', 'FadeInBinding').sourceObject, 'value', curve, 'input1')
        trinity.CreateBinding(self.lightingCurveSet, FindBinding('FadeOutCurveSet', 'FadeOutBindin').sourceObject, 'value', curve, 'input2')
        trinity.CreateBinding(self.lightingCurveSet, curve, 'currentValue', scene.shLightingManager, 'secondaryIntensity')
        if scene.shLightingManager:
            light = self._SetupStaticLight(-1, self.lightingCurveSet)
            self.lights.append((light, None, None))
            scene.shLightingManager.lights.append(light)
            light = self._SetupStaticLight(1, self.lightingCurveSet)
            self.lights.append((light, None, None))
            scene.shLightingManager.lights.append(light)
            curve = trinity.Tr2ScalarExprCurve()
            curve.expr = 'input1 * min(max(input2 + 2 * min(max(min(max(input3, 0), 1) - min(max(input4, 0), 1), 0), 1), 0), 1)'
            curve.input1 = 1
            curve.input2 = 0
            curve.input3 = 0
            curve.input4 = 0
            curve.length = 1
            curve.cycle = True
            self.lightingCurveSet.curves.append(curve)
            trinity.CreateBinding(self.lightingCurveSet, FindBinding('_Setup_', 'brightness_tunnel').sourceObject, 'currentValue', curve, 'input1').scale = gfxsettings.SECONDARY_LIGHTING_INTENSITY
            trinity.CreateBinding(self.lightingCurveSet, FindBinding('SpeedModifier', 'additiveBinding').sourceObject, 'value', curve, 'input2')
            trinity.CreateBinding(self.lightingCurveSet, FindBinding('FadeInCurveSet', 'FadeInBindingAdditive').sourceObject, 'value', curve, 'input3')
            trinity.CreateBinding(self.lightingCurveSet, FindBinding('FadeOutCurveSet', 'FadeOutBindingAdditive').sourceObject, 'value', curve, 'input4')
            trinity.CreateBinding(self.lightingCurveSet, curve, 'currentValue', scene.shLightingManager, 'primaryIntensity').scale = 2
        self.shLightingManager = scene.shLightingManager
        scene.curveSets.append(self.lightingCurveSet)
        self.lightingCurveSet.Play()
        uthread.new(self._AnimateLights, scene)
        return

    def _AnimateLights(self, scene):
        while self.lightingCurveSet and scene.shLightingManager:
            if self.shLightingManager != scene.shLightingManager:
                self._RemoveLightingCurves(scene)
                if scene.shLightingManager:
                    self._SetupLightingCurves(scene)
                return
            light = self._SetupDynamicLight(self.lightingCurveSet)
            self.lights.append(light)
            scene.shLightingManager.lights.append(light[0])
            remove = [ i for i, light in enumerate(self.lights) if light[0].position[2] < -5 ]
            for each in sorted(remove, reverse=True):
                light, curve, binding = self.lights[each]
                self.lightingCurveSet.curves.remove(curve)
                self.lightingCurveSet.bindings.remove(binding)
                try:
                    scene.shLightingManager.lights.remove(light)
                except RuntimeError:
                    pass

                del self.lights[each]

            blue.synchro.SleepSim(random.randint(100, 500))

    def _SetupStaticLight(self, offset, curveSet):
        light = trinity.Tr2PointLight()
        light.color = STATIC_WARP_LIGHT_COLOR
        light.position = (0, 0, offset)
        curve = trinity.TriPerlinCurve()
        curve.offset = 0.2
        curve.scale = 0.2
        curveSet.curves.append(curve)
        trinity.CreateBinding(curveSet, curve, 'value', light, 'radius')
        return light

    def _SetupDynamicLight(self, curveSet):
        angle = random.random() * 2 * pi
        light = trinity.Tr2PointLight()
        light.color = geo2.Vec3Lerp(DYNAMIC_WARP_LIGHT_COLOR, (1, 1, 1, 1), random.random())
        light.radius = 0.7
        light.position = (sin(angle) * 1.5, cos(angle) * 1.5, 2)
        curve = trinity.Tr2ScalarCurve()
        curve.AddKey(0, 2)
        curve.AddKey(8.0 / 20.0, -6)
        curve.Sort()
        curve.timeOffset = curveSet.scaledTime
        curveSet.curves.append(curve)
        binding = trinity.CreateBinding(curveSet, curve, 'currentValue', light, 'position.z')
        return (light, curve, binding)

    def _RemoveLightingCurves(self, scene):
        try:
            scene.curveSets.remove(self.lightingCurveSet)
        except (RuntimeError, ValueError):
            pass

        self.lightingCurveSet = None
        if self.shLightingManager:
            self.shLightingManager.primaryIntensity = gfxsettings.SECONDARY_LIGHTING_INTENSITY
            self.shLightingManager.secondaryIntensity = gfxsettings.SECONDARY_LIGHTING_INTENSITY
            for each, _, _ in self.lights:
                try:
                    self.shLightingManager.lights.remove(each)
                except RuntimeError:
                    pass

        self.lights = []
        return

    def RecycleOrLoad(self, resPath):
        return blue.resMan.LoadObject(resPath)

    def ControlFlow(self, event):
        if event == 'ExitPlanet':
            scene = self.fxSequencer.GetScene()
            for each in scene.lensflares:
                each.display = True

            self.nextCollision[0].display = True
            self.exitPlanetBinding.scale = 0
            self.exitPlanetEventCurve.Stop()
            if self.hasMoreCollisions:
                self.nextPlanetBinding.scale = 1
                self.nextPlanetEventCurve.Play()
                self.nextPlanetBinding.sourceObject.expr = '-input1 / input2'
        elif event == 'NextCollision':
            self.nextPlanetBinding.scale = 0
            self.nextPlanetEventCurve.Stop()
            res = self.SetupNextCollision()
            if res == False:
                self.nextPlanetBinding.scale = 1
                self.nextPlanetEventCurve.Play()
                self.nextPlanetBinding.sourceObject.expr = 'input2 / input1'
            else:
                self.enterPlanetBinding.scale = 1
                self.enterPlanetEventCurve.Play()
        elif event == 'EnterPlanet':
            scene = self.fxSequencer.GetScene()
            for each in scene.lensflares:
                each.display = False

            self.nextCollision[0].display = False
            if self.nextCollision[0].radius < 450000:
                delta = 1
                self.nextCollision = (self.nextCollision[0], delta)
                self.collisionCurve.input1 = 1.1 * delta / 10000.0
            self.enterPlanetBinding.scale = 0
            self.enterPlanetEventCurve.Stop()
            self.exitPlanetBinding.scale = 1
            self.exitPlanetEventCurve.Play()

    def SetupTunnelBindings(self):
        self.curveSet = [ x for x in self.gfx.curveSets if x.name == 'SpeedBinding' ][0]
        for binding in self.curveSet.bindings:
            self.speedBinding = binding
            binding.sourceObject = self.shipModel.speed
            binding.scale *= 1.0 / (3.0 * const.AU * self.warpSpeedModifier)

        self.curveSet.Play()
        setup = [ x for x in self.gfx.curveSets if x.name == '_Setup_' ][0]
        self.setup = setup
        self.collisionCurve = [ x for x in setup.curves if x.name == '_global' ][0]
        self.xout = [ x for x in setup.curves if x.name == '_xPointOut' ][0]
        extra = [ x for x in self.gfx.curveSets if getattr(x, 'name', None) == '_Extra_' ][0]
        first = [ x for x in self.gfx.curveSets if getattr(x, 'name', None) == '_First_' ][0]
        self.distanceTracker = first.curves.Find('trinity.Tr2DistanceTracker')[0]
        self.distanceTraveled = [ x for x in extra.curves if getattr(x, 'name', None) == '_mov' ][0]
        self.fadeInLength = [ x for x in extra.curves if getattr(x, 'name', None) == '_fadeLength' ][0]
        self.eventb = [ x for x in self.gfx.curveSets if x.name == 'EventBindings' ][0]
        eventBindings = [ x for x in self.gfx.curveSets if x.name == 'EventBindings' ][0].bindings
        for binding in eventBindings:
            if binding.name == 'enterPlanetBinding':
                self.enterPlanetBinding = binding
            elif binding.name == 'exitPlanetBinding':
                self.exitPlanetBinding = binding
            elif binding.name == 'nextPlanetBinding':
                self.nextPlanetBinding = binding

        self.enterPlanetEventCurve = [ x for x in self.gfx.curveSets if x.name == 'enterPlanet' ][0]
        self.exitPlanetEventCurve = [ x for x in self.gfx.curveSets if x.name == 'exitPlanet' ][0]
        self.nextPlanetEventCurve = [ x for x in self.gfx.curveSets if x.name == 'nextCollision' ][0]
        self.enterPlanetBinding.scale = 0
        self.exitPlanetBinding.scale = 0
        self.nextPlanetBinding.scale = 0
        self.enterPlanetEventCurve.Stop()
        self.exitPlanetEventCurve.Stop()
        self.nextPlanetEventCurve.Stop()
        self.exitPlanetEventCurve.curves[0].AddKey(0.0, u'Start')
        self.exitPlanetEventCurve.curves[0].AddCallableKey(1.0, self.ControlFlow, ('ExitPlanet',))
        self.enterPlanetEventCurve.curves[0].AddKey(0.0, u'Start')
        self.enterPlanetEventCurve.curves[0].AddCallableKey(1.0, self.ControlFlow, ('EnterPlanet',))
        self.nextPlanetEventCurve.curves[0].AddKey(0.0, u'Start')
        self.nextPlanetEventCurve.curves[0].AddCallableKey(1.0, self.ControlFlow, ('NextCollision',))
        return

    def TeardownTunnelBindings(self):
        if getattr(self, 'speedBinding', None) is not None:
            self.speedBinding.sourceObject = self.shipModel.speed
        if getattr(self, 'distanceTracker', None) is not None:
            self.distanceTracker.targetObject = None
            self.distanceTracker = None
        if getattr(self, 'exitPlanetEventCurve', None) is not None:
            del self.exitPlanetEventCurve.curves[0]
            del self.enterPlanetEventCurve.curves[0]
            del self.nextPlanetEventCurve.curves[0]
        return

    def CalcEffectiveRadius(self, direction, planetPosition, planetRadius):
        distToMiddle = geo2.Vec3DotD(planetPosition, direction)
        if distToMiddle < 0:
            return None
        midPoint = geo2.Vec3ScaleD(direction, distToMiddle)
        distToCenter = geo2.Vec3DistanceD(planetPosition, midPoint)
        if distToCenter > planetRadius:
            return None
        else:
            return sqrt(planetRadius * planetRadius - distToCenter * distToCenter)

    def GetDistanceToTarget(self, direction, planetPosition):
        return geo2.Vec3DotD(planetPosition, direction)

    def GetWarpCollisions(self, ball):
        space = sm.GetService('space')
        planets = space.planetManager.planets
        destination = self.destination
        source = (ball.x, ball.y, ball.z)
        self.direction = geo2.Vec3SubtractD(destination, source)
        direction = self.direction
        warpDistance = geo2.Vec3LengthD(direction)
        normDirection = geo2.Vec3NormalizeD(direction)
        self.normDirection = normDirection
        ballpark = sm.GetService('michelle').GetBallpark()
        collisions = []
        for planet in planets:
            planetBall = ballpark.GetBall(planet.id)
            if planetBall is None:
                log.LogWarn('Warping got a None planet ball.')
                continue
            planetRadius = planetBall.radius
            planetPosition = (planetBall.x, planetBall.y, planetBall.z)
            planetDir = geo2.Vec3SubtractD(planetPosition, source)
            if geo2.Vec3LengthSqD(self.direction) < geo2.Vec3LengthSqD(planetDir):
                continue
            effectiveRadius = self.CalcEffectiveRadius(normDirection, planetDir, planetRadius)
            if effectiveRadius is None:
                continue
            collisions.append((planetBall, effectiveRadius))
            blue.pyos.BeNice()

        return collisions

    def FindNextCollision(self, destination, candidates, popCollision=True):
        minDist = None
        time = blue.os.GetSimTime()
        position = self.shipBall.GetVectorAt(blue.os.GetSimTime())
        position = (position.x, position.y, position.z)
        nextCollision = None
        for each in candidates:
            collisionBall = each[0]
            collisionCenter = collisionBall.GetVectorAt(time)
            collisionCenter = (collisionCenter.x, collisionCenter.y, collisionCenter.z)
            projection = geo2.Vec3DotD(collisionCenter, self.normDirection)
            if minDist is None or projection < minDist:
                minDist = projection
                nextCollision = each

        if nextCollision is not None and popCollision:
            candidates.remove(nextCollision)
        return nextCollision

    def SetupNextCollision(self):
        self.hasMoreCollisions = False
        self.distanceTracker.direction = self.normDirection
        time = blue.os.GetSimTime()
        if self.findNext:
            lastCollision = self.nextCollision
            self.nextCollision = self.FindNextCollision(self.destination, self.collisions)
            if self.nextCollision is None:
                self.nextCollision = lastCollision
            if self.nextCollision is None:
                self.collisionCurve.input1 = 1.0
                self.fadeInLength.input1 = 0.0
                self.collisionCurve.input3 = 100000000
                self.collisionCurve.input3 = 100000000
                self.distanceTracker.targetObject = None
                self.distanceTraveled.input1 = 100000000
                self.distanceTracker.targetPosition = (0, 0, 100000000)
                self.distanceTracker.direction = (0, 0, -1)
                return True
            targetPosition = self.nextCollision[0].GetVectorAt(time)
            targetPosition = (targetPosition.x, targetPosition.y, targetPosition.z)
            furtherCollision = self.FindNextCollision(self.destination, self.collisions, False)
            if furtherCollision is not None:
                self.hasMoreCollisions = True
                furtherPosition = furtherCollision[0].GetVectorAt(time)
                furtherPosition = (furtherPosition.x, furtherPosition.y, furtherPosition.z)
                length = geo2.Vec3DistanceD(targetPosition, furtherPosition)
                self.nextPlanetBinding.sourceObject.input2 = length / 2
        else:
            targetPosition = self.nextCollision[0].GetVectorAt(time)
            targetPosition = (targetPosition.x, targetPosition.y, targetPosition.z)
        distanceToCollision = self.GetDistanceToTarget(self.normDirection, targetPosition)
        returnValue = True
        warpSpeed = self.warpSpeedModifier * const.AU
        if distanceToCollision > warpSpeed:
            self.findNext = False
            returnValue = False
            self.nextPlanetBinding.sourceObject.input2 = warpSpeed
        else:
            self.findNext = True
        planetRadius = self.nextCollision[0].radius
        delta = self.CalcEffectiveRadius(self.normDirection, targetPosition, planetRadius)
        if delta is None:
            delta = planetRadius
        self.nextCollision = (self.nextCollision[0], delta)
        self.collisionCurve.input1 = 1.1 * delta / 10000.0
        self.fadeInLength.input1 = 80000 * self.warpSpeedModifier * 3
        self.collisionCurve.input3 = abs(distanceToCollision) / 10000.0
        self.distanceTracker.targetObject = self.nextCollision[0]
        self.distanceTraveled.input1 = abs(distanceToCollision) / 10000.0
        return returnValue

    def WarpLoop(self, ball):
        space = sm.GetService('space')
        space.StartWarpIndication()
        sm.ScatterEvent('OnWarpStarted')
        self.shipBall = ball
        while ball.mode == destiny.DSTBALL_WARP:
            sm.GetService('space').UpdateHUDActionIndicator()
            self.ShakeCamera(ball)
            if not self.hasExploded or self.hasWind:
                speedFraction = self.shipModel.speed.value * self.curveSet.bindings[0].scale
                if not self.hasExploded and speedFraction > 0.005:
                    sm.StartService('audio').SendUIEvent('wise:/ship_warp_explosion_play')
                    sm.StartService('audio').SendUIEvent('wise:/ship_warp_wind_play')
                    self.hasExploded = True
                    self.hasWind = True
                    sm.ScatterEvent('OnWarpStarted2')
                elif self.hasWind and speedFraction < 1e-06:
                    sm.StartService('audio').SendUIEvent('wise:/ship_warp_wind_end')
                    self.hasWind = False
            blue.synchro.SleepSim(1000)
            if hasattr(self.gfx, 'display'):
                self.gfx.display = True

        self.EndWarpShake()
        sm.StartService('audio').SendUIEvent('wise:/ship_warp_wind_stop')
        sm.StartService('FxSequencer').OnSpecialFX(ball.id, None, None, None, None, 'effects.Warping', 0, 0, 0)
        sm.ScatterEvent('OnWarpFinished')
        sm.StartService('space').StopWarpIndication()
        return

    def Stop(self, reason=STOP_REASON_DEFAULT):
        shipID = self.GetEffectShipID()
        if shipID != session.shipid:
            return
        else:
            self.TeardownTunnelBindings()
            if self.shipBall is not None:
                self.shipBall.UnregisterModelChangeNotification(self.ModelChangeNotify)
            self.shipBall = None
            self.shipModel = None
            ShipEffect.Stop(self)
            return

    def ShakeCamera(self, ball):
        ballpark = sm.GetService('michelle').GetBallpark()
        if ballpark is None:
            return
        else:
            speedVector = trinity.TriVector(ball.vx, ball.vy, ball.vz)
            speed = speedVector.Length()
            maxSpeed = ballpark.warpSpeed * const.AU - ball.maxVelocity
            speed = (speed - ball.maxVelocity) / maxSpeed
            speed = max(0.0, speed)
            rumbleFactor = 0.5 - 0.5 * cos(6.28 * pow(speed, 0.1))
            rumbleFactor = (rumbleFactor - 0.2) / 0.8
            rumbleFactor = max(rumbleFactor, 0.0)
            rumbleFactor = pow(rumbleFactor, 0.8)
            shakeFactor = 0.7 * rumbleFactor
            cam = self.GetCamera()
            noisescaleCurve = trinity.TriScalarCurve()
            noisescaleCurve.extrapolation = trinity.TRIEXT_CONSTANT
            noisescaleCurve.AddKey(0.0, cam.noiseScale, 0.0, 0.0, trinity.TRIINT_LINEAR)
            noisescaleCurve.AddKey(0.5, shakeFactor * 2.0, 0.0, 0.0, trinity.TRIINT_LINEAR)
            noisescaleCurve.AddKey(5.0, 0.0, 0.0, 0.0, trinity.TRIINT_LINEAR)
            noisescaleCurve.Sort()
            behavior = shaker.ShakeBehavior('Warp')
            behavior.scaleCurve = noisescaleCurve
            cam.shakeController.DoCameraShake(behavior)
            return

    def GetCamera(self):
        return sm.GetService('sceneManager').GetActiveSpaceCamera()

    def EndWarpShake(self):
        camera = self.GetCamera()
        camera.shakeController.EndCameraShake('Warp')

    def AlignToDirection(self):
        destination = sm.StartService('space').warpDestinationCache[3]
        ballPark = sm.StartService('michelle').GetBallpark()
        egoball = ballPark.GetBall(ballPark.ego)
        direction = [egoball.x - destination[0], egoball.y - destination[1], egoball.z - destination[2]]
        zaxis = direction
        if geo2.Vec3LengthSqD(zaxis) > 0.0:
            zaxis = geo2.Vec3NormalizeD(zaxis)
            xaxis = geo2.Vec3CrossD((0, 1, 0), zaxis)
            if geo2.Vec3LengthSqD(xaxis) == 0.0:
                zaxis = geo2.Vec3AddD(zaxis, mathCommon.RandomVector(0.0001))
                zaxis = geo2.Vec3NormalizeD(zaxis)
                xaxis = geo2.Vec3CrossD((0, 1, 0), zaxis)
            xaxis = geo2.Vec3NormalizeD(xaxis)
            yaxis = geo2.Vec3CrossD(zaxis, xaxis)
        else:
            self.transformFlags = effectconsts.FX_TF_POSITION_BALL | effectconsts.FX_TF_ROTATION_BALL
            self.Prepare()
            return
        mat = ((xaxis[0],
          xaxis[1],
          xaxis[2],
          0.0),
         (yaxis[0],
          yaxis[1],
          yaxis[2],
          0.0),
         (zaxis[0],
          zaxis[1],
          zaxis[2],
          0.0),
         (0.0, 0.0, 0.0, 1.0))
        quat = geo2.QuaternionRotationMatrix(mat)
        self.gfxModel.rotationCurve = None
        if self.gfxModel and hasattr(self.gfxModel, 'modelRotationCurve'):
            self.gfxModel.modelRotationCurve = trinity.TriRotationCurve(0.0, 0.0, 0.0, 1.0)
            self.gfxModel.modelRotationCurve.value = quat
        self.debugAligned = True
        return

    def Repeat(self, duration):
        if self.gfx is None:
            return
        else:
            effects.ShipEffect.Repeat(self)
            return