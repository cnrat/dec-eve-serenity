# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\camera\sceneContainerCamera.py
from eve.client.script.ui.camera.baseCamera import Camera

class SceneContainerCamera(Camera):
    default_isActive = True

    def __init__(self):
        Camera.__init__(self)
        self._aspectRatio = 1.0

    def UpdateViewportSize(self, width, height):
        self._aspectRatio = float(width) / height

    def GetAspectRatio(self):
        return self._aspectRatio