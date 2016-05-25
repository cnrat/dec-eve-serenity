# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\planetCamera.py
from eve.client.script.ui.camera.cameraOld import CameraOld
import evecamera

class PlanetCamera(CameraOld):
    cameraID = evecamera.CAM_PLANET
    __notifyevents__ = []