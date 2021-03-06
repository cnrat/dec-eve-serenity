# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\gaugeCircular.py
import math
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.transform import Transform
from carbonui.primitives.vectorlinetrace import VectorLineTrace
from math import pi, cos, sin, atan2
from carbonui.util.color import Color
import geo2
import uthread
import blue

class GaugeCircular(Container):
    __notifyevents__ = ['OnUIScalingChange']
    default_name = 'GaugeCircular'
    default_radius = 20
    default_lineWidth = 3.0
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_colorStart = (1.0, 1.0, 1.0, 1.0)
    default_colorEnd = (0.8, 0.8, 0.8, 1.0)
    default_colorBg = None
    default_colorMarker = None
    default_startAngle = -pi / 2
    default_value = 0.0
    default_callback = None
    default_hoverMarkerEnabled = False
    default_clockwise = True
    default_bgPortion = 1.0
    default_showMarker = True
    default_autoUpdate = True
    default_moveMarker = False
    default_animateInRealTime = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.radius = attributes.Get('radius', self.default_radius)
        self.lineWidth = attributes.Get('lineWidth', self.default_lineWidth)
        self.startAngle = attributes.Get('startAngle', self.default_startAngle)
        self.value = attributes.Get('value', self.default_value)
        self.colorStart = attributes.Get('colorStart', self.default_colorStart)
        self.colorEnd = attributes.Get('colorEnd', self.default_colorEnd)
        self.colorBg = attributes.Get('colorBg', self.default_colorBg)
        colorMarker = attributes.Get('colorMarker', self.default_colorMarker)
        self.callback = attributes.Get('callback', self.default_callback)
        self.isHoverMarkerEnabled = attributes.Get('hoverMarkerEnabled', self.default_hoverMarkerEnabled)
        self.isClockwise = attributes.Get('clockwise', self.default_clockwise)
        self.bgPortion = attributes.Get('bgPortion', self.default_bgPortion)
        self.showMarker = attributes.get('showMarker', self.default_showMarker)
        self.autoUpdate = attributes.get('autoUpdate', self.default_autoUpdate)
        self.moveMarker = attributes.get('moveMarker', self.default_moveMarker)
        self.useRealTime = attributes.get('useRealTime', self.default_animateInRealTime)
        if colorMarker is None:
            colorMarker = self.colorStart
        self.width = self.height = self.radius * 2
        self.pickRadius = self.radius + self.lineWidth
        self._angle = 0.0
        hoverMarkerSize = self.lineWidth * 1.7
        self.hoverMarker = Sprite(name='hoverMarker', parent=self, color=colorMarker, width=hoverMarkerSize, height=hoverMarkerSize, state=uiconst.UI_DISABLED, opacity=0.0, texturePath='res:/UI/Texture/Classes/Gauge/circle.png')
        if self.isClockwise:
            rotation = -self.startAngle - pi / 2
        else:
            rotation = self.startAngle + pi / 2
        state = uiconst.UI_DISABLED if self.showMarker else uiconst.UI_HIDDEN
        self.markerTransform = Transform(name='markerTransform', parent=self, align=uiconst.TOALL, rotationCenter=(0.5, 0.5), rotation=rotation, state=state)
        height = self.lineWidth + 5
        self.marker = Fill(name='marker', parent=self.markerTransform, color=colorMarker, align=uiconst.CENTERTOP, pos=(0,
         -(height - self.lineWidth),
         2,
         height))
        self.gauge = None
        self.bgGauge = None
        self.Reconstruct()
        if self.autoUpdate:
            uthread.new(self.UpdateThread)
        return

    def UpdateThread(self):
        while not self.destroyed:
            diff = self.gauge.end - self.value
            diff = 3.0 * diff / blue.os.fps
            self.gauge.end -= diff
            blue.synchro.Yield()

    def Reconstruct(self):
        if self.gauge:
            self.gauge.Close()
        self.gauge = self.ConstructLine(self.colorStart, self.colorEnd)
        self.gauge.end = self.value
        self.gauge.name = 'gaugeLine'
        if self.colorBg is None:
            self.colorBg = Color(*self.colorStart).SetBrightness(0.2).GetRGBA()
        if self.bgGauge:
            self.bgGauge.Close()
        self.bgGauge = self.ConstructLine(self.colorBg, self.colorBg)
        self.bgGauge.end = self.bgPortion
        self.bgGauge.name = 'backgroundLine'
        return

    def GetLinePoint(self, t, w):
        if not self.isClockwise:
            t = -t
        r = self.radius - w
        if not self.isClockwise:
            t = t - pi
        xPoint = w + r * (1.0 + cos(t))
        yPoint = w + r * (1.0 + sin(t))
        return (xPoint, yPoint)

    def ConstructLine(self, colorStart, colorEnd):
        numPoints = max(30, self.radius)
        line = VectorLineTrace(parent=self, lineWidth=self.lineWidth, width=1, height=1, end=0.0)
        w = self.lineWidth / 2.0
        stepSize = 2 * pi / numPoints
        for i in xrange(numPoints + 1):
            if i == 0:
                t = self.startAngle - 0.1 * stepSize
                point = self.GetLinePoint(t, w)
                line.AddPoint(point, color=(1, 1, 1, 0))
            t = self.startAngle + float(i) * stepSize
            point = self.GetLinePoint(t, w)
            color = geo2.Vec4Lerp(colorStart, colorEnd, i / float(numPoints))
            line.AddPoint(point, color)

        return line

    def SetValue(self, value, animate=True):
        if value == self.value:
            return
        if not animate:
            self.gauge.end = value
        self.value = value

    def SetMarkerValue(self, value):
        self.markerTransform.rotation = self.GetOffsetMarkerValue(value)

    def SetValueAndMarker(self, value, animated=True):
        self.SetValue(value, animated)
        self.SetMarkerValue(value)

    def SetValueAndMarkerTimed(self, value, duration):
        self.SetMarkerValueTimed(value, duration)
        self.SetValueTimed(value, duration)

    def SetValueTimed(self, value, duration):
        uicore.animations.MorphScalar(self.gauge, 'end', self.gauge.end, value, duration=duration, curveType=uiconst.ANIM_LINEAR, curveSet=self._GetCorrectCurveSet())
        self.value = value

    def _GetCorrectCurveSet(self):
        simTimeCurveSet = uicore.animations.CreateCurveSet(useRealTime=self.useRealTime)
        simTimeCurveSet.name = 'gaugeCircularCurveSet'
        return simTimeCurveSet

    def SetMarkerValueTimed(self, value, duration):
        newRotation = self.GetOffsetMarkerValue(value)
        uicore.animations.MorphScalar(self.markerTransform, 'rotation', self.markerTransform.rotation, newRotation, duration=duration, curveType=uiconst.ANIM_LINEAR, curveSet=self._GetCorrectCurveSet())

    def StopGaugeAnimations(self):
        self.gauge.StopAnimations()
        self.markerTransform.StopAnimations()

    def GetOffsetMarkerValue(self, value):
        offSet = math.pi * 2 * (1.0 - value)
        newRotation = math.pi * 1.5 - self.startAngle + offSet
        return newRotation

    def SetColor(self, colorStart, colorEnd=None):
        self.gauge.Close()
        self.gauge = self.ConstructLine(colorStart, colorEnd)
        self.gauge.end = self.value

    def SetColorMarker(self, colorMarker):
        self.marker.SetRGBA(*colorMarker)

    def SetColorBg(self, colorBg):
        self.bgGauge.Close()
        self.bgGauge = self.ConstructLine(colorBg, colorBg)
        self.bgGauge.name = 'backgroundLine'

    def GetMousePositionAngle(self):
        x, y = self.GetAbsolutePosition()
        x = uicore.uilib.x - x - self.radius
        y = uicore.uilib.y - y - self.radius
        v1 = (x, y)
        if geo2.Vec2Length(v1) < 5:
            return self._angle
        v2 = (0.0, 1.0)
        dot = geo2.Vec2Dot(v1, v2)
        cross = v1[0] * v2[1] - v1[1] * v2[0]
        angle = atan2(dot, cross)
        angle -= self.startAngle
        if angle < 0:
            angle += 2 * pi
        self._angle = angle
        return angle

    def TriggerCallback(self):
        if not self.callback:
            return
        angle = self.GetMousePositionAngle()
        value = angle / (2.0 * pi)
        self.callback(value)

    def OnMouseDown(self, *args):
        if not uicore.uilib.leftbtn:
            return
        self.TriggerCallback()

    def OnMouseEnter(self, *args):
        if not self.callback:
            return
        for obj in (self.gauge, self.bgGauge, self.marker):
            uicore.animations.FadeTo(obj, obj.opacity, 1.5, duration=0.3)

        if self.isHoverMarkerEnabled:
            uicore.animations.FadeIn(self.hoverMarker, 1.0, duration=0.3)

    def OnMouseExit(self, *args):
        if not self.callback:
            return
        for obj in (self.gauge, self.bgGauge, self.marker):
            uicore.animations.FadeTo(obj, obj.opacity, 1.0, duration=0.6)

        if self.isHoverMarkerEnabled:
            uicore.animations.FadeOut(self.hoverMarker, duration=0.3)
            currAngle = self.hoverMarkerAngle
            endAngle = 2 * pi if currAngle > pi else 0.0
            uicore.animations.MorphScalar(self, 'hoverMarkerAngle', currAngle, endAngle, duration=0.3)

    def OnMouseMove(self, *args):
        if uicore.uilib.leftbtn:
            self.TriggerCallback()
        if not self.isHoverMarkerEnabled:
            return
        self.hoverMarkerAngle = self.GetMousePositionAngle()

    def GetHoverMarkerAngle(self):
        if not self.isHoverMarkerEnabled:
            return 0.0
        return self.GetMousePositionAngle()

    def SetHoverMarkerAngle(self, angle):
        angle += self.startAngle
        w = self.hoverMarker.height / 2.0
        r = self.radius + self.lineWidth
        x = (r + w) * cos(angle)
        y = (r + w) * sin(angle)
        offset = r - w - self.lineWidth / 2.0
        self.hoverMarker.left = x + offset
        self.hoverMarker.top = y + offset

    hoverMarkerAngle = property(GetHoverMarkerAngle, SetHoverMarkerAngle)

    def EnableHoverMarker(self):
        self.isHoverMarkerEnabled = True

    def DisableHoverMarker(self):
        self.isHoverMarkerEnabled = False

    def OnUIScalingChange(self, *args):
        self.Reconstruct()