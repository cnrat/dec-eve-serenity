# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\entosis\ui\__init__.py


def IsSameCaptureTeam(allianceID, teamID):
    if teamID is None or allianceID is None:
        return False
    elif teamID > 0 and teamID == allianceID:
        return True
    elif teamID < 0 and -teamID != allianceID:
        return True
    else:
        return False