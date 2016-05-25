# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveSpaceObject\spaceobjanimation.py
import shipmode.data as stancedata
STATE_MACHINE_SHIP_STANDARD = 'shipStandard'
STATE_MACHINE_SHIP_STANCE = 'shipStance'
STATE_MACHINE_SHIP_LOOP = 'shipLoop'
stanceAnimations = {stancedata.shipStanceSpeed: 'speed',
 stancedata.shipStanceSniper: 'sniper',
 stancedata.shipStanceDefense: 'defense'}

def GetStateMachine(model, name):
    if model.animationSequencer is None:
        return
    else:
        for stateMachine in model.animationSequencer.stateMachines:
            if stateMachine.name == name:
                return stateMachine

        return


def SetShipAnimationStance(ship, stanceID):
    if stanceID not in stanceAnimations:
        return False
    elif ship is None or ship.animationSequencer is None:
        return False
    else:
        state = stanceAnimations[stanceID]
        ship.animationSequencer.GoToState(state)
        return True


def GetAnimationStateFromStance(stanceID):
    if stanceID in stanceAnimations:
        return stanceAnimations[stanceID]


def SetUpAnimation(model, stateMachinePath, trinity):
    if model.animationSequencer is None:
        model.animationSequencer = trinity.EveAnimationSequencer()
    stateMachine = trinity.Load(stateMachinePath)
    model.animationSequencer.stateMachines.append(stateMachine)
    return


def LoadAnimationStates(animationStateList, graphicStatesData, model, trinity):
    for sid in animationStateList:
        path = graphicStatesData[sid].file
        SetUpAnimation(model, path, trinity)


def LoadAnimationStatesFromFiles(animationStateFiles, model, trinity):
    for path in animationStateFiles:
        SetUpAnimation(model, path, trinity)


def TriggerDefaultStates(model):
    if not hasattr(model, 'animationSequencer'):
        return
    for stateMachine in model.animationSequencer.stateMachines:
        if len(stateMachine.defaultState) > 1:
            model.animationSequencer.GoToState(stateMachine.defaultState)