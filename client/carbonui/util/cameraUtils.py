# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\util\cameraUtils.py
import geo2
import mathCommon
import math

def GetEntityYaw(entity):
    entityRot = entity.GetComponent('position').rotation
    yaw, pitch, roll = geo2.QuaternionRotationGetYawPitchRoll(entityRot)
    yaw += math.pi / 2
    if yaw > 2.0 * math.pi:
        yaw = yaw - 2.0 * math.pi
    elif yaw < 0.0:
        yaw = yaw + 2.0 * math.pi
    if yaw <= math.pi:
        return math.pi - yaw
    else:
        return -(yaw - math.pi)


def ReverseCameraYaw(yaw):
    if yaw <= 0:
        yaw = math.pi - abs(yaw)
    else:
        yaw = -(math.pi - yaw)
    return yaw


def GetAngleFromEntityToCamera(entity, overrideYaw=None, offset=None):
    activeCamera = sm.GetService('cameraClient').GetActiveCamera()
    cameraYaw = -activeCamera.yaw
    if overrideYaw:
        cameraYaw = overrideYaw
    if offset:
        cameraYaw = offset + cameraYaw
    playerYaw = GetEntityYaw(entity)
    retval = 0.0
    if playerYaw != None and cameraYaw != None:
        lesserYaw = mathCommon.GetLesserAngleBetweenYaws(playerYaw, cameraYaw)
        retval = lesserYaw
    return retval


def CalcDesiredPlayerHeading(heading):
    headingYaw = mathCommon.GetYawAngleFromDirectionVector(heading)
    activeCamera = sm.GetService('cameraClient').GetActiveCamera()
    cameraYaw = -activeCamera.yaw
    desiredYaw = cameraYaw + headingYaw
    return desiredYaw


def GetAngleFromEntityToYaw(entity, yaw):
    lesserYaw = mathCommon.GetLesserAngleBetweenYaws(GetEntityYaw(entity), yaw)
    return lesserYaw


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('cameraUtils', globals())