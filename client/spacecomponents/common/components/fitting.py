# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\spacecomponents\common\components\fitting.py
from ..componentConst import FITTING_CLASS
from spacecomponents.common.helper import HasFittingComponent
from spacecomponents.common.helper import IsActiveComponent
from spacecomponents.common.helper import IsReinforcedComponent

def IsShipWithinFittingRange(spaceComponentStaticData, shipSlimItem, componentSlimItem, ballPark):
    if shipSlimItem is None:
        return False
    elif not hasattr(componentSlimItem, 'typeID'):
        return False
    else:
        ball = ballPark.GetBall(componentSlimItem.itemID)
        itemIsDead = not ball or ball.isMoribund
        componentTypeID = componentSlimItem.typeID
        if shipSlimItem.ownerID != componentSlimItem.ownerID:
            return False
        elif itemIsDead:
            return False
        elif not HasFittingComponent(componentTypeID):
            return False
        elif not IsActiveComponent(ballPark.componentRegistry, componentTypeID, componentSlimItem.itemID):
            return False
        elif IsReinforcedComponent(ballPark.componentRegistry, componentTypeID, componentSlimItem.itemID):
            return False
        fittingRange = spaceComponentStaticData.GetAttributes(componentTypeID, FITTING_CLASS).range
        shipDistanceFromComponent = ballPark.GetSurfaceDist(shipSlimItem.itemID, componentSlimItem.itemID)
        return shipDistanceFromComponent <= fittingRange