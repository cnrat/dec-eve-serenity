# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\clienteffects\__init__.py
EFFECT_METHOD = 'OnSpecialFX'

def SetEffect(sourceID, targetID, effectName, start, duration, repeat):
    sm.ScatterEvent(EFFECT_METHOD, sourceID, None, None, targetID, None, effectName, 0, start, 0, duration, repeat)
    return


def StartShipEffect(sourceID, effectName, duration, repeat):
    SetEffect(sourceID, None, effectName, True, duration, repeat)
    return


def StopShipEffect(sourceID, effectName):
    SetEffect(sourceID, None, effectName, False, None, None)
    return


def StartStretchEffect(sourceID, targetID, effectName, duration, repeat):
    SetEffect(sourceID, targetID, effectName, True, duration, repeat)


def StopStretchEffect(sourceID, targetID, effectName):
    SetEffect(sourceID, targetID, effectName, False, None, None)
    return