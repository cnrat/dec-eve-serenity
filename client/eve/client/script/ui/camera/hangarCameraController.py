# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\hangarCameraController.py
import evecamera
import math
from eve.client.script.ui.camera.baseCameraController import BaseCameraController
from eve.client.script.ui.camera.cameraUtil import CheckInvertZoom, GetPowerOfWithSign

class HangarCameraController(BaseCameraController):
    cameraID = evecamera.CAM_HANGAR

    def OnMouseMove(self, *args):
        camera = self.GetCamera()
        if camera.fixed:
            return
        kOrbit = evecamera.ORBIT_MOVE_DIST
        if uicore.uilib.leftbtn and uicore.uilib.rightbtn:
            kZoom = 0.005
            self._Zoom(-uicore.uilib.dy, kZoom)
            if math.fabs(uicore.uilib.dx) > 1:
                camera.Orbit(0.01 * uicore.uilib.dx, 0.0)
        elif uicore.uilib.leftbtn:
            camera.Orbit(kOrbit * uicore.uilib.dx, kOrbit * uicore.uilib.dy)

    def OnMouseWheel(self, *args):
        k = 0.0005
        self._Zoom(uicore.uilib.dz, k)

    def _Zoom(self, dz, k):
        camera = self.GetCamera()
        if camera.fixed:
            return
        dz = CheckInvertZoom(dz)
        dz = GetPowerOfWithSign(dz)
        camera.Zoom(k * dz)