# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\common\script\util\industryCommon.py
import evetypes
import log
import copy
import blue
import localization
import util
import const
import industry
import service
import datetime
import telemetry
import itertools
from UserDict import DictMixin
import inventorycommon.typeHelpers
ATTRIBUTE_MODIFIERS = [(industry.SlotModifier, const.attributeManufactureSlotLimit, industry.MANUFACTURING),
 (industry.SlotModifier, const.attributeMaxLaborotorySlots, industry.RESEARCH_TIME),
 (industry.SlotModifier, const.attributeMaxLaborotorySlots, industry.RESEARCH_MATERIAL),
 (industry.SlotModifier, const.attributeMaxLaborotorySlots, industry.COPYING),
 (industry.SlotModifier, const.attributeMaxLaborotorySlots, industry.INVENTION),
 (industry.TimeModifier, const.attributeManufactureTimeMultiplier, industry.MANUFACTURING),
 (industry.TimeModifier, const.attributeManufacturingTimeResearchSpeed, industry.RESEARCH_TIME),
 (industry.TimeModifier, const.attributeMineralNeedResearchSpeed, industry.RESEARCH_MATERIAL),
 (industry.TimeModifier, const.attributeCopySpeedPercent, industry.COPYING),
 (industry.TimeModifier, const.attributeInventionReverseEngineeringResearchSpeed, industry.INVENTION)]
REQUIRED_SKILL_MODIFIERS = [(industry.TimeModifier, const.attributeManufactureTimePerLevel, industry.MANUFACTURING)]
BLUEPRINT_MODIFIERS = [(industry.CostModifier, const.attributeJobCostMultiplier, None)]
ACCOUNT_ENTRY_TYPES = {industry.MANUFACTURING: const.refManufacturing,
 industry.RESEARCH_TIME: const.refResearchingTimeProductivity,
 industry.RESEARCH_MATERIAL: const.refResearchingMaterialProductivity,
 industry.COPYING: const.refCopying,
 industry.INVENTION: const.refResearchingTechnology}

def GetErrorLabel(error, *args):
    if error == industry.Error.INVALID_OWNER:
        return localization.GetByLabel('UI/Industry/Errors/InvalidOwner')
    elif error == industry.Error.INVALID_CHARACTER:
        return localization.GetByLabel('UI/Industry/Errors/InvalidCharacter')
    elif error == industry.Error.INVALID_CORPORATION:
        return localization.GetByLabel('UI/Industry/Errors/InvalidCorporation')
    elif error == industry.Error.INVALID_RUNS:
        return localization.GetByLabel('UI/Industry/Errors/InvalidRuns')
    elif error == industry.Error.INVALID_LICENSED_RUNS:
        return localization.GetByLabel('UI/Industry/Errors/InvalidLicensedRuns')
    elif error == industry.Error.INVALID_INPUT_LOCATION:
        return localization.GetByLabel('UI/Industry/Errors/InvalidInputLocation')
    elif error == industry.Error.INVALID_OUTPUT_LOCATION:
        return localization.GetByLabel('UI/Industry/Errors/InvalidOutputLocation')
    elif error == industry.Error.INVALID_PRODUCT:
        return localization.GetByLabel('UI/Industry/Errors/InvalidProduct')
    elif error == industry.Error.INVALID_COST:
        return localization.GetByLabel('UI/Industry/Errors/InvalidCost')
    elif error == industry.Error.INVALID_ACTIVITY:
        return localization.GetByLabel('UI/Industry/Errors/InvalidActivity')
    elif error == industry.Error.INVALID_FACILITY:
        return localization.GetByLabel('UI/Industry/Errors/InvalidFacility')
    elif error == industry.Error.MISSING_ACTIVITY:
        return localization.GetByLabel('UI/Industry/Errors/MissingActivity')
    elif error == industry.Error.MISSING_ROLE:
        return localization.GetByLabel('UI/Industry/Errors/MissingRole')
    elif error == industry.Error.MISSING_BLUEPRINT:
        return localization.GetByLabel('UI/Industry/Errors/MissingBlueprint')
    elif error == industry.Error.MISSING_FACILITY:
        return localization.GetByLabel('UI/Industry/Errors/MissingFacility')
    elif error == industry.Error.MISSING_MATERIAL:
        return localization.GetByLabel('UI/Industry/Errors/MissingMaterial')
    elif error == industry.Error.MISSING_INPUT_LOCATION:
        return localization.GetByLabel('UI/Industry/Errors/MissingInputLocation')
    elif error == industry.Error.MISSING_OUTPUT_LOCATION:
        return localization.GetByLabel('UI/Industry/Errors/MissingOutputLocation')
    elif error == industry.Error.ACCOUNT_FUNDS:
        return localization.GetByLabel('UI/Industry/Errors/AccountFunds')
    elif error == industry.Error.ACCOUNT_ACCESS:
        return localization.GetByLabel('UI/Industry/Errors/AccountAccess')
    elif error == industry.Error.ACCOUNT_INVALID:
        return localization.GetByLabel('UI/Industry/Errors/AccountInvalid')
    elif error == industry.Error.INCOMPATIBLE_ACTIVITY:
        return localization.GetByLabel('UI/Industry/Errors/IncompatibleActivity')
    elif error == industry.Error.BLUEPRINT_ACCESS:
        return localization.GetByLabel('UI/Industry/Errors/BlueprintAccess')
    elif error == industry.Error.BLUEPRINT_INSTALLED:
        return localization.GetByLabel('UI/Industry/Errors/BlueprintInstalled')
    elif error == industry.Error.BLUEPRINT_WRONG_FACILITY:
        return localization.GetByLabel('UI/Industry/Errors/BlueprintWrongFacility')
    elif error == industry.Error.MISMATCH_COST:
        return localization.GetByLabel('UI/Industry/Errors/MismatchCost')
    elif error == industry.Error.MISMATCH_TAX:
        return localization.GetByLabel('UI/Industry/Errors/MismatchTax')
    elif error == industry.Error.MISMATCH_TIME:
        return localization.GetByLabel('UI/Industry/Errors/MismatchTime')
    elif error == industry.Error.MISMATCH_MATERIAL:
        return localization.GetByLabel('UI/Industry/Errors/MismatchMaterial')
    elif error == industry.Error.INVALID_BLUEPRINT_LOCATION:
        return localization.GetByLabel('UI/Industry/Errors/InvalidBlueprintLocation')
    elif error == industry.Error.MISSING_SKILL:
        return localization.GetByLabel('UI/Industry/Errors/MissingSkill')
    elif error == industry.Error.SLOTS_FULL:
        return localization.GetByLabel('UI/Industry/Errors/SlotsFull')
    elif error == industry.Error.RESEARCH_LIMIT:
        return localization.GetByLabel('UI/Industry/Errors/ResearchLimit')
    elif error == industry.Error.FACILITY_DISTANCE:
        return localization.GetByLabel('UI/Industry/Errors/FacilityDistance')
    elif error == industry.Error.FACILITY_ACTIVITY:
        return localization.GetByLabel('UI/Industry/Errors/FacilityActivity')
    elif error == industry.Error.FACILITY_TYPE:
        return localization.GetByLabel('UI/Industry/Errors/FacilityTypeError')
    elif error == industry.Error.RUN_LENGTH:
        numDays = industry.MAX_RUN_LENGTH * const.SEC / const.DAY
        return localization.GetByLabel('UI/Industry/Errors/RunLength', numDays=numDays)
    elif error == industry.Error.FACILITY_OFFLINE:
        return localization.GetByLabel('UI/Industry/Errors/FacilityOffline')
    elif error == industry.Error.FACILITY_DENIED:
        return localization.GetByLabel('UI/Industry/Errors/FacilityDenied')
    elif error == industry.Error.INPUT_ACCESS:
        return localization.GetByLabel('UI/Industry/Errors/InputAccess')
    elif error == industry.Error.INVALID_MATERIAL_EFFICIENCY:
        return localization.GetByLabel('UI/Industry/Errors/InvalidMaterialEfficiency')
    elif error == industry.Error.INVALID_TIME_EFFICIENCY:
        return localization.GetByLabel('UI/Industry/Errors/InvalidTimeEfficiency')
    else:
        return error.name


def ItemLocationFlag(location):
    if location.typeID == const.typeOffice:
        return location.flagID
    if evetypes.GetCategoryID(location.typeID) == const.categoryStarbase:
        return location.flagID
    if evetypes.GetGroupID(location.typeID) == const.groupStation:
        return location.flagID


def ItemOutputFlag(location, itemFlagID=None):
    if location.typeID == const.typeOffice:
        return location.flagID
    if evetypes.GetCategoryID(location.typeID) == const.categoryStarbase:
        return location.flagID
    if evetypes.GetGroupID(location.typeID) == const.groupStation:
        return location.flagID
    if evetypes.GetGroupID(location.typeID) == const.groupAuditLogSecureContainer:
        if itemFlagID == const.flagLocked:
            return const.flagLocked
        else:
            return const.flagUnlocked
    return const.flagNone


def RolesAtLocation(session, locationID):
    if session.role & service.ROLE_SERVICE:
        return 18446744073709551615L
    roles = 0L
    if locationID == session.hqID:
        roles = session.rolesAtAll | session.rolesAtHQ
    elif locationID == session.baseID:
        roles = session.rolesAtAll | session.rolesAtBase
    else:
        roles = session.rolesAtAll | session.rolesAtOther
    return roles


def CanViewItem(session, ownerID, locationID, flagID):
    if session.role & service.ROLE_SERVICE:
        return True
    if ownerID == session.charid:
        return True
    if util.IsCorporation(ownerID):
        required = const.corpHangarQueryRolesByFlag.get(flagID, 0) | const.corpRoleFactoryManager
        if RolesAtLocation(session, locationID) & required == required:
            return True
    return False


def CanTakeItem(session, ownerID, locationID, flagID, container=False):
    if session.role & service.ROLE_SERVICE:
        return True
    if ownerID == session.charid:
        return True
    if util.IsCorporation(ownerID):
        if container:
            required = const.corpContainerTakeRolesByFlag.get(flagID, 0) | const.corpRoleFactoryManager
        else:
            required = const.corpHangarTakeRolesByFlag.get(flagID, 0) | const.corpRoleFactoryManager
        if RolesAtLocation(session, locationID) & required == required:
            return True
    return False


def OwnerAccess(session, ownerID, locationID=None, flagID=None):
    if not session or session.role & service.ROLE_SERVICE:
        return True
    if util.IsCharacter(ownerID):
        if session.charid != ownerID and session.role & service.ROLE_SERVICE == 0:
            return False
    elif util.IsCorporation(ownerID) and not util.IsNPCCorporation(ownerID):
        if not session.corprole & const.corpRoleFactoryManager:
            return False
        if session.corpid != ownerID and session.role & service.ROLE_SERVICE == 0:
            return False
    else:
        return False
    if locationID and flagID and not CanViewItem(session, ownerID, locationID, flagID):
        return False
    return True


def AssertBlueprintAccess(session, ownerID, locationID=None, flagID=None):
    if not OwnerAccess(session, ownerID, locationID, flagID):
        raise UserError('IndustryBlueprintAccessDenied')


def AssertLocationAccess(session, ownerID, locationID=None, flagID=None):
    if not OwnerAccess(session, ownerID, locationID, flagID):
        raise UserError('IndustryLocationAccessDenied')


def AssertFacilityAccess(session, ownerID):
    if not OwnerAccess(session, ownerID):
        raise UserError('IndustryFacilityAccessDenied')


def AssertJobAccess(session, ownerID):
    if not OwnerAccess(session, ownerID):
        raise UserError('IndustryJobAccessDenied')


@telemetry.ZONE_METHOD
def AttachSessionToJob(job, session):
    if job and session:
        job.characterID = session.charid
        job.corporationID = session.corpid
        job.roles = RolesAtLocation(session, job.facilityID)


def JobStatus(data):
    if data.status == industry.STATUS_INSTALLED and data.endDate < blue.os.GetWallclockTime():
        return industry.STATUS_READY
    else:
        return data.status


@util.Memoized
def GetBlueprintsByProductGroup(groupID):
    blueprints = set()
    for typeIDInGroup in evetypes.GetTypeIDsByGroup(groupID):
        for typeID in cfg.blueprints.filter_keys('productTypeID', typeIDInGroup):
            blueprints.add(typeID)

    blueprints.discard(None)
    return blueprints


@util.Memoized
def GetBlueprintsByProductCategory(categoryID):
    blueprints = set()
    for groupID in evetypes.GetGroupIDsByCategory(categoryID):
        for typeIDInGroup in evetypes.GetTypeIDsByGroup(groupID):
            for typeID in cfg.blueprints.filter_keys('productTypeID', typeIDInGroup):
                blueprints.add(typeID)

    blueprints.discard(None)
    return blueprints


def BlueprintInstance(data):
    blueprint = cfg.blueprints[data.typeID].copy()
    blueprint.blueprintID = data.itemID
    blueprint.timeEfficiency = data.timeEfficiency
    blueprint.materialEfficiency = data.materialEfficiency
    blueprint.runsRemaining = data.runs
    blueprint.quantity = max(data.quantity, 1)
    blueprint.original = data.quantity != -2 and evetypes.GetCategoryID(data.typeID) != const.categoryAncientRelic
    blueprint.locationID = data.locationID
    blueprint.locationTypeID = data.locationTypeID
    blueprint.locationFlagID = data.locationFlagID
    blueprint.flagID = data.flagID
    blueprint.facilityID = data.facilityID
    blueprint.ownerID = data.ownerID
    blueprint.jobID = data.jobID
    return blueprint


def JobData(data, blueprint):
    job = industry.JobData(blueprint, data.activityID)
    job.data = data
    job.jobID = data.jobID
    job.blueprintID = data.blueprintID
    job.blueprintTypeID = data.blueprintTypeID
    job.blueprintLocationID = data.blueprintLocationID
    job.blueprintLocationFlagID = data.blueprintLocationFlagID
    job.facilityID = data.facilityID
    job.ownerID = data.ownerID
    job.status = JobStatus(data)
    job.installerID = data.installerID
    job.completedCharacterID = data.completedCharacterID
    job.solarSystemID = data.solarSystemID
    job.stationID = data.stationID
    job.startDate = util.BlueToDate(data.startDate)
    job.endDate = util.BlueToDate(data.endDate)
    job.pauseDate = util.BlueToDate(data.pauseDate) if data.pauseDate else None
    job.runs = data.runs
    job.licensedRuns = data.licensedRuns
    job.successfulRuns = data.successfulRuns
    job.cost = data.cost
    job.time = datetime.timedelta(seconds=data.timeInSeconds)
    job.probability = data.probability if data.probability is not None else 1
    job.productTypeID = data.productTypeID
    job.optionalTypeID = data.optionalTypeID
    job.optionalTypeID2 = data.optionalTypeID2
    job.outputLocationID = data.outputLocationID
    job.outputFlagID = data.outputFlagID
    return job


def Facility(data):
    facility = industry.Facility(facilityID=data['facilityID'], typeID=data['typeID'], ownerID=data['ownerID'], tax=data['tax'], solarSystemID=data['solarSystemID'], online=data['online'])
    blue.pyos.BeNice()
    for activityID, (timeModifiers, materialModifiers, costModifiers, categories, groups) in data['activities'].iteritems():
        blueprints = set()
        for categoryID in categories:
            blueprints.update(GetBlueprintsByProductCategory(categoryID))

        for groupID in groups:
            blueprints.update(GetBlueprintsByProductGroup(groupID))

        facility.update_activity(activityID, blueprints, categories, groups)
        mapping = [(timeModifiers, industry.TimeModifier), (materialModifiers, industry.MaterialModifier), (costModifiers, industry.CostModifier)]
        for modifiers, cls in mapping:
            for amount, categoryID, groupID, reference in modifiers:
                if categoryID:
                    blueprints = GetBlueprintsByProductCategory(categoryID) | set([0])
                elif groupID:
                    blueprints = GetBlueprintsByProductGroup(groupID) | set([0])
                else:
                    blueprints = None
                facility.modifiers.append(cls(amount=amount, reference=industry.Reference(reference or industry.Reference.FACILITY), activity=activityID, blueprints=blueprints, categoryID=categoryID, groupID=groupID))

    return facility


@telemetry.ZONE_METHOD
def MatchLocation(job, locationID=None, flagID=None):
    for location in job.locations:
        if location.flagID == flagID and location.itemID == locationID:
            return copy.copy(location)

    for location in job.locations:
        if location.flagID == flagID and location.ownerID == job.ownerID:
            return copy.copy(location)

    if locationID and util.IsCorporation(job.ownerID) and util.IsStation(job.facility.facilityID):
        return industry.Location(itemID=job.facility.facilityID, ownerID=job.ownerID, flagID=const.flagHangar, typeID=cfg.stations.Get(job.facility.facilityID).stationTypeID)
    else:
        try:
            return copy.copy(job.locations[0])
        except IndexError:
            return None

        return None


@telemetry.ZONE_METHOD
def GetDecryptors(job):
    if job.activityID == industry.INVENTION:
        if boot.role == 'client':
            dogma = sm.GetService('godma')
        else:
            dogma = sm.GetService('dogmaStaticMgr')
        options = [industry.Material(mutable=True)]
        for typeID in evetypes.GetTypeIDsByGroup(const.groupDecryptors):
            options.append(industry.Material(mutable=True, typeID=typeID, quantity=1, modifiers=[industry.MaxRunsModifier(dogma.GetTypeAttribute(typeID, const.attributeInventionMaxRunModifier), output=True, activity=industry.INVENTION, reference=industry.Reference.DECRYPTOR),
             industry.MaterialModifier(dogma.GetTypeAttribute(typeID, const.attributeInventionMEModifier) / 100.0, output=True, activity=industry.INVENTION, reference=industry.Reference.DECRYPTOR),
             industry.TimeModifier(dogma.GetTypeAttribute(typeID, const.attributeInventionPEModifier) / 100.0, output=True, activity=industry.INVENTION, reference=industry.Reference.DECRYPTOR),
             industry.ProbabilityModifier(dogma.GetTypeAttribute(typeID, const.attributeInventionPropabilityMultiplier), activity=industry.INVENTION, reference=industry.Reference.DECRYPTOR)]))

        decryptor = industry.Material(mutable=True, options=options)
        if job.request:
            allTypes = decryptor.all_types()
            for typeID in job.request['materials']:
                if typeID in allTypes:
                    decryptor.select(typeID)

        if getattr(job, 'optionalTypeID', None) in decryptor.all_types():
            decryptor.select(job.optionalTypeID)
        if getattr(job, 'optionalTypeID2', None) in decryptor.all_types():
            decryptor.select(job.optionalTypeID2)
        return [decryptor]
    else:
        return []


def GetJobModifiers(job):
    if boot.role == 'client':
        dogma = sm.GetService('godma')
    else:
        dogma = sm.GetService('dogmaStaticMgr')
    modifiers = []
    for modifier, attribute, activity in BLUEPRINT_MODIFIERS:
        amount = dogma.GetTypeAttribute(job.blueprint.blueprintTypeID, attribute)
        if amount is not None:
            modifiers.append(modifier(amount, reference=industry.Reference.BLUEPRINT, activity=activity))

    for modifier, attribute, activity in REQUIRED_SKILL_MODIFIERS:
        for skill in job.required_skills:
            amount = dogma.GetTypeAttribute(skill.typeID, attribute)
            if amount is not None:
                amount = 1.0 + amount * job.skills[skill.typeID] / 100.0
                modifiers.append(modifier(amount, reference=industry.Reference.SKILLS, activity=activity))

    return modifiers


def GetOptionalMaterials(job):
    return GetDecryptors(job)


@util.Memoized
def GetBlueprintPrice(typeID):
    try:
        if boot.role == 'client':
            blueprint = sm.GetService('blueprintSvc').GetBlueprintType(typeID)
        else:
            blueprint = sm.GetService('blueprintManager').GetBlueprintType(typeID)
        materials = blueprint.activities[industry.MANUFACTURING].materials
        return sum([ GetBlueprintPrice(material.typeID) * material.quantity for material in materials ])
    except (KeyError, UserError):
        pass

    try:
        if typeID is not None:
            adjustedAveragePrice = inventorycommon.typeHelpers.GetAdjustedAveragePrice(typeID)
            if adjustedAveragePrice:
                return adjustedAveragePrice
    except KeyError:
        pass

    log.LogError('industryCommon.GetBlueprintPrice missing adjustedAveragePrice for type: ', typeID)
    return 0


class JobPrices(DictMixin):

    def __getitem__(self, key):
        return GetBlueprintPrice(key)

    def __setitem__(self, key, item):
        raise RuntimeError('Job pricing is immutable')

    def __delitem__(self, key):
        raise RuntimeError('Job pricing is immutable')

    def keys(self):
        return evetypes.GetAllTypeIDs()


def IsBlueprintCategory(categoryID):
    return categoryID in (const.categoryBlueprint, const.categoryAncientRelic)