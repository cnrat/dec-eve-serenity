# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\units.py


def _GetDogmaUnits():
    return cfg.dgmunits


def GetUnit(unitID):
    return _GetDogmaUnits().Get(unitID)


def HasUnit(unitID):
    return unitID in _GetDogmaUnits()


def GetDisplayName(unitID):
    return GetUnit(unitID).displayName