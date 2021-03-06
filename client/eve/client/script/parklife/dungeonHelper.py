# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\parklife\dungeonHelper.py
import blue
import dungeonEditorTools
import math
from eve.common.script.util.eveCommonUtils import ComputeRadiusFromQuantity, ComputeQuantityFromRadius
import trinity
import geo2

def IsJessicaOpen():
    return '/jessica' in blue.pyos.GetArg()


def BatchStart():
    if IsJessicaOpen():
        sm.StartService('BSD').TransactionStart()


def BatchEnd():
    if IsJessicaOpen():
        sm.StartService('BSD').TransactionEnd()


def IsObjectLocked(objectID):
    if IsJessicaOpen():
        import dungeon
        dunObject = dungeon.Object.Get(objectID, _getDeleted=True)
        if dunObject is None:
            return (True, [])
        return dunObject.IsLocked()
    else:
        return sm.RemoteSvc('dungeon').IsObjectLocked(objectID)


def SetObjectPosition(objectID, x=None, y=None, z=None):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    dX = 0
    if x is not None:
        dX = x - slimItem.dunX
        slimItem.dunX = x
    dY = 0
    if y is not None:
        dY = y - slimItem.dunY
        slimItem.dunY = y
    dZ = 0
    if z is not None:
        dZ = z - slimItem.dunZ
        slimItem.dunZ = z
    targetModel = getattr(targetBall, 'model', None)
    if targetModel:
        targetModel.translationCurve.x += dX
        targetModel.translationCurve.y += dY
        targetModel.translationCurve.z += dZ
    scenario.UpdateUnsavedObjectChanges(slimItem.itemID, dungeonEditorTools.CHANGE_TRANSLATION)
    return


def SetObjectRotation(objectID, yaw=None, pitch=None, roll=None):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    targetModel = getattr(targetBall, 'model', None)
    if not targetModel:
        return
    else:
        try:
            mYaw, mPitch, mRoll = geo2.QuaternionRotationGetYawPitchRoll(targetModel.rotationCurve.value)
        except:
            mYaw, mPitch, mRoll = targetBall.yaw, targetBall.pitch, targetBall.roll

        if yaw is None:
            yaw = mYaw
        if pitch is None:
            pitch = mPitch
        if roll is None:
            roll = mRoll
        targetBall.typeData['dunRotation'] = (yaw, pitch, roll)
        targetBall.SetStaticRotation()
        scenario.UpdateUnsavedObjectChanges(slimItem.itemID, dungeonEditorTools.CHANGE_ROTATION)
        return


def SetObjectRadius(objectID, radius):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    if slimItem.categoryID == const.categoryAsteroid or slimItem.groupID in (const.groupHarvestableCloud, const.groupCloud):
        godma = sm.GetService('godma')
        computedQuantity = ComputeQuantityFromRadius(slimItem.categoryID, slimItem.groupID, slimItem.typeID, radius, godma)
        SetObjectQuantity(objectID, computedQuantity)
    return


def SetObjectQuantity(objectID, quantity):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    targetModel = getattr(targetBall, 'model', None)
    if not targetModel:
        return
    else:
        if slimItem.categoryID == const.categoryAsteroid or slimItem.groupID in (const.groupHarvestableCloud, const.groupCloud):
            godma = sm.GetService('godma')
            computedRadius = ComputeRadiusFromQuantity(slimItem.categoryID, slimItem.groupID, slimItem.typeID, quantity, godma)
            if hasattr(targetModel, 'modelScale'):
                targetModel.modelScale = computedRadius
            elif hasattr(targetModel, 'scaling'):
                scaleVector = trinity.TriVector(computedRadius, computedRadius, computedRadius)
                targetModel.scaling = scaleVector
            else:
                raise RuntimeError('Model has neither modelScale nor scaling')
            slimItem.dunRadius = quantity
            scenario.UpdateUnsavedObjectChanges(slimItem.itemID, dungeonEditorTools.CHANGE_SCALE)
        else:
            raise RuntimeError("Can't scale type %d" % slimItem.categoryID)
        return


def SaveObjectPosition(objectID, x=None, y=None, z=None):
    if IsJessicaOpen():
        import dungeon
        dunObject = dungeon.Object.Get(objectID)
        dunObject.SetPosition(x=x, y=y, z=z)
    else:
        sm.RemoteSvc('dungeon').EditObjectXYZ(objectID=objectID, x=x, y=y, z=z)


def SaveObjectRotation(objectID, yaw=None, pitch=None, roll=None):
    if IsJessicaOpen():
        import dungeon
        dunObject = dungeon.Object.Get(objectID)
        dunObject.SetRotation(yaw=yaw, pitch=pitch, roll=roll)
    else:
        sm.RemoteSvc('dungeon').EditObjectYawPitchRoll(objectID=objectID, yaw=yaw, pitch=pitch, roll=roll)


def SaveObjectRadius(objectID, radius):
    if IsJessicaOpen():
        import dungeon
        dunObject = dungeon.Object.Get(objectID)
        dunObject.SetRadius(radius)
    else:
        sm.RemoteSvc('dungeon').EditObjectRadius(objectID=objectID, radius=radius)


def CopyObject(objectID, roomID, offsetX=0.0, offsetY=0.0, offsetZ=0.0):
    if IsJessicaOpen():
        import dungeon
        dunObject = dungeon.Object.Get(objectID)
        newObjectID = dunObject.Copy(roomID, offsetX, offsetY, offsetZ).objectID
    else:
        newObjectID = sm.RemoteSvc('dungeon').CopyObject(objectID, roomID, offsetX, offsetY, offsetZ)
    return newObjectID


def GetObjectPosition(objectID):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    return (slimItem.dunX, slimItem.dunY, slimItem.dunZ)


def GetObjectRotation(objectID):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    targetModel = getattr(targetBall, 'model', None)
    if not targetModel or not targetModel.rotationCurve or not hasattr(targetModel.rotationCurve, 'value'):
        return (None, None, None)
    else:
        return (x * 180.0 / math.pi for x in geo2.QuaternionRotationGetYawPitchRoll(targetModel.rotationCurve.value))


def GetObjectQuantity(objectID):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    targetModel = getattr(targetBall, 'model', None)
    if not targetModel:
        return
    else:
        if hasattr(targetModel, 'scaling') or hasattr(targetModel, 'modelScale'):
            if not getattr(slimItem, 'dunRadius', None):
                slimItem.dunRadius = targetBall.radius
            if slimItem.categoryID == const.categoryAsteroid:
                return slimItem.dunRadius
            if slimItem.groupID in (const.groupHarvestableCloud, const.groupCloud):
                return slimItem.dunRadius
        return


def GetObjectRadius(objectID):
    scenario = sm.StartService('scenario')
    targetBall, slimItem = scenario.GetBallAndSlimItemFromObjectID(objectID)
    if slimItem is None:
        raise RuntimeError('No slim item?')
    targetModel = getattr(targetBall, 'model', None)
    if not targetModel:
        return
    else:
        if hasattr(targetModel, 'scaling') or hasattr(targetModel, 'modelScale'):
            godma = sm.GetService('godma')
            if not getattr(slimItem, 'dunRadius', None):
                slimItem.dunRadius = ComputeQuantityFromRadius(slimItem.categoryID, slimItem.groupID, slimItem.typeID, targetBall.radius, godma)
            if slimItem.categoryID == const.categoryAsteroid:
                return ComputeRadiusFromQuantity(slimItem.categoryID, slimItem.groupID, slimItem.typeID, slimItem.dunRadius, godma)
            if slimItem.groupID in (const.groupHarvestableCloud, const.groupCloud):
                return ComputeRadiusFromQuantity(slimItem.categoryID, slimItem.groupID, slimItem.typeID, slimItem.dunRadius, godma)
        return


def CreateObject(roomID, typeID, objectName, x, y, z, yaw, pitch, roll, radius):
    if IsJessicaOpen():
        import dungeon
        newObject = dungeon.Object.Create(roomID=roomID, typeID=typeID, objectName=objectName, x=x, y=y, z=z, yaw=yaw, pitch=pitch, roll=roll, radius=radius)
        newObjectID = newObject.objectID
    else:
        newObjectID, revisionID = sm.RemoteSvc('dungeon').AddObject(roomID, typeID, x, y, z, yaw, pitch, roll, radius)
        if objectName:
            sm.RemoteSvc('dungeon').EditObjectName(newObjectID, objectName)
    return newObjectID


def DeleteObject(objectID):
    if IsJessicaOpen():
        import dungeon
        dungeon.Object.Get(objectID).Delete()
    else:
        sm.RemoteSvc('dungeon').RemoveObject(objectID)


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('dungeonHelper', locals())