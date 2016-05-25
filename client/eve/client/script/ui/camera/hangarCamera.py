# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\hangarCamera.py
import geo2
import math
import evecamera
from eve.client.script.ui.camera.baseSpaceCamera import BaseSpaceCamera

class HangarCamera(BaseSpaceCamera):
    cameraID = evecamera.CAM_HANGAR
    isBobbingCamera = True

    def __init__(self):
        BaseSpaceCamera.__init__(self)
        self.cameraTransformCurveSet = None
        self.fixed = False
        return

    def SetDefaultHangarCamera(self):
        self.kMinPitch = math.pi / 30.0
        self.kMaxPitch = math.pi / 2.0 + math.pi / 50.0
        self.atPosition = (0.0, 0.0, 0.0)
        self.eyePosition = (-0.68, 0.35, 0.64)
        self.fixed = False

    def SetSuperCapitalHangarCamera(self, defaultEyePosition):
        self.kMinPitch = math.pi / 30.0
        self.kMaxPitch = 2.0 * math.pi
        self.atPosition = (0.0, 0.0, 0.0)
        self.eyePosition = defaultEyePosition
        self.MoveTo(self.eyePosition, self.atPosition, 0.0)
        self.fixed = True

    def MoveTo(self, eyePos, atPos, duration):
        duration = max(duration, 0.0001)
        self.Transit(self.atPosition, self.eyePosition, atPos, eyePos, duration, 0.1, 1000, 0.0)