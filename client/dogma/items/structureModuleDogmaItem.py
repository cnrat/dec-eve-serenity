# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\items\structureModuleDogmaItem.py
from fittableDogmaItem import FittableDogmaItem
import util
import structures

class StructureModuleDogmaItem(FittableDogmaItem):

    def IsOnline(self):
        return const.effectOnline in self.activeEffects

    def IsValidFittingLocation(self, location):
        return location.categoryID == const.categoryStructure

    def GetCharacterID(self):
        return self.GetPilot()

    def GetStructureID(self):
        if self.location:
            return self.location.itemID
        else:
            return None