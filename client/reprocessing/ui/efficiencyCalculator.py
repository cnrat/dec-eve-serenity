# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\reprocessing\ui\efficiencyCalculator.py
from reprocessing.ui.util import GetSkillFromTypeID

def CalculateTheoreticalEfficiency(typeIDs, efficiency):
    getTypeAttribute = sm.GetService('clientDogmaStaticSvc').GetTypeAttribute
    getSkillLevel = sm.GetService('skills').MySkillLevel
    bonuses = []
    for typeID in typeIDs:
        skillBonuses = GetSkillFromTypeID(typeID, getTypeAttribute, getSkillLevel)
        totalSkillBonus = 1.0
        for _, bonus in skillBonuses:
            totalSkillBonus *= 1 + bonus / 100

        bonuses.append(100 * (totalSkillBonus - 1))

    avgSkillBonus = sum(bonuses) / len(typeIDs)
    return min(1.0, efficiency * (100 + avgSkillBonus) / 100)