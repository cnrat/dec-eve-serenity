# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\trinity\TriCameraBehaviorBase.py


class TriCameraBehaviorBase(object):

    def __init__(self):
        self.m_pCamera = None
        return

    def SetCamera(self, pCam):
        self.__oCamera__ = pCam

    def GetName():
        pass

    GetName = staticmethod(GetName)

    def Update(self, fDeltaT):
        pass

    def onMovementStickInputLR(self, fX):
        pass

    def onMovementStickInputIO(self, fY):
        pass

    def onMovementStickInputFB(self, fZ):
        pass

    def onMovementStickRaw(self, fX, fY, fZ):
        pass

    def onCameraStickInputLR(self, fX):
        pass

    def onCameraStickInputIO(self, fY):
        pass

    def onCameraStickInputFB(self, fZ):
        pass

    def onCameraStickRaw(self, fX, fY, fZ):
        pass

    def onDolly(self, fDelta):
        pass

    def DoCustomAction(self, nID, tData):
        pass

    def UpdateTaransientData(self, Data):
        pass

    def SetTransientData(self, Data):
        pass