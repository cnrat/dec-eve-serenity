# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\effects\util.py
from dogma.effects.modifiereffect import ModifierEffect
import modifiers
import sideeffect

def CreateEffect(effectInfo, modifierInfo):
    mods = []
    side_effects = []
    for effectDict in modifierInfo:
        funcType = effectDict['func']
        modifierClass = modifiers.GetModifierClassByTypeString(funcType)
        sideeffectClass = sideeffect.GetSideEffectClassByTypeString(funcType)
        if modifierClass is not None:
            mods.append(modifierClass(effectDict))
        elif sideeffectClass is not None:
            side_effects.append(sideeffectClass(effectDict))
        else:
            raise RuntimeError("Can't create effect from modifierInfo. Unknown funcType type '%s'." % funcType)

    return ModifierEffect(effectInfo, mods, side_effects)