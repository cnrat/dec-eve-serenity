# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\dogma\fitting.py
from dogma.effects import Effect

class LauncherFittedEffect(Effect):
    __guid__ = 'dogmaXP.LauncherFittedEffect'
    __effectIDs__ = ['effectLauncherFitted']

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.AddModifier(const.dgmAssModSub, shipID, const.attributeLauncherSlotsLeft, itemID, const.attributeSlots)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModSub, shipID, const.attributeLauncherSlotsLeft, itemID, const.attributeSlots)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModSub, shipID, const.attributeLauncherSlotsLeft, itemID, const.attributeSlots)


class TurretFittedEffect(Effect):
    __guid__ = 'dogmaXP.TurretFittedEffect'
    __effectIDs__ = ['effectTurretFitted']

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.AddModifier(const.dgmAssModSub, shipID, const.attributeTurretSlotsLeft, itemID, const.attributeSlots)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModSub, shipID, const.attributeTurretSlotsLeft, itemID, const.attributeSlots)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModSub, shipID, const.attributeTurretSlotsLeft, itemID, const.attributeSlots)


class UpgradeFittedEffect(Effect):
    __guid__ = 'dogmaXP.UpgradeFittedEffect'
    __effectIDs__ = ['effectRigSlot']

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.AddModifier(const.dgmAssModSub, shipID, const.attributeUpgradeSlotsLeft, itemID, const.attributeSlots)
        dogmaLM.AddModifier(const.dgmAssModAdd, shipID, const.attributeUpgradeLoad, itemID, const.attributeUpgradeCost)

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModSub, shipID, const.attributeUpgradeSlotsLeft, itemID, const.attributeSlots)
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeUpgradeLoad, itemID, const.attributeUpgradeCost)

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        dogmaLM.RemoveModifier(const.dgmAssModSub, shipID, const.attributeUpgradeSlotsLeft, itemID, const.attributeSlots)
        dogmaLM.RemoveModifier(const.dgmAssModAdd, shipID, const.attributeUpgradeLoad, itemID, const.attributeUpgradeCost)


class SubSystemFittedEffect(Effect):
    __guid__ = 'dogmaXP.SubSystemFittedEffect'
    __effectIDs__ = ['effectSubSystem']

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass


class ServiceSlotFittedEffect(Effect):
    __guid__ = 'dogmaXP.ServiceSlotFittedEffect'
    __effectIDs__ = ['effectServiceSlot']

    def Start(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def Stop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass

    def RestrictedStop(self, env, dogmaLM, itemID, shipID, charID, otherID, targetID):
        pass