# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\maps\starModeHandler.py
import evetypes
import trinity
import uix
import math
import util
import string
import geo2
import mapcommon
from mapcommon import LegendItem, COLORCURVE_SECURITY, COLOR_STANDINGS_GOOD, COLOR_STANDINGS_BAD, COLOR_STANDINGS_NEUTRAL
from collections import defaultdict
import talecommon.const as taleConst
from localization import GetByLabel, GetByMessageID
import inventorycommon.typeHelpers
DEFAULT_MAX_COLOR = trinity.TriColor(0.0, 1.0, 0.0)
COLOR_GREEN = trinity.TriColor(0.0, 1.0, 0.0)
COLOR_YELLOW = trinity.TriColor(1.0, 1.0, 0.0)
COLOR_ORANGE = trinity.TriColor(1.0, 0.4, 0.0)
COLOR_RED = trinity.TriColor(1.0, 0.0, 0.0)
COLOR_WHITE = trinity.TriColor(1.0, 1.0, 1.0)
COLOR_GRAY = trinity.TriColor(0.5, 0.5, 0.5)
COLOR_PURPLE = trinity.TriColor(0.5, 0.25, 0.75)

def ColorStarsByDevIndex(colorInfo, starColorMode, indexID, indexName):
    sovSvc = sm.GetService('sov')
    indexData = sovSvc.GetAllDevelopmentIndicesMapped()
    color = trinity.TriColor(0.4, 0.4, 1.0)
    hintFunc = lambda indexName, level: GetByLabel('UI/Map/StarModeHandler/devIndxLevel', indexName=indexName, level=level)
    for solarSystemID, info in indexData.iteritems():
        levelInfo = sovSvc.GetIndexLevel(info[indexID], indexID)
        if levelInfo.level == 0:
            continue
        size = levelInfo.level * 2.0
        colorInfo.solarSystemDict[solarSystemID] = (size,
         1.0,
         (hintFunc, (indexName, levelInfo.level)),
         color)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/devIndxUndevloped'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/devIndxDevloped'), color, data=None))
    return


def HintMyAssets(stationData):
    c = []
    for stationID, itemCount in stationData:
        shortStationName = uix.EditStationName(cfg.evelocations.Get(stationID).name, usename=1)
        subc = GetByLabel('UI/Map/StarModeHandler/StationNameWithItemCount', shortStationName=shortStationName, numItems=itemCount)
        c.append((subc, ('OnClick', 'OpenAssets', (stationID,))))

    return ([GetByLabel('UI/Map/StarModeHandler/assetsMyAssets')], c)


def ColorStarsByAssets(colorInfo, starColorMode):
    myassets = sm.GetService('assets').GetAll('allitems', blueprintOnly=0, isCorp=0)
    assetColor = trinity.TriColor(0.5, 0.1, 0.0)
    bySystemID = {}
    stuffToPrime = []
    for solarsystemID, station in myassets:
        stuffToPrime.append(station.stationID)
        stuffToPrime.append(solarsystemID)
        if solarsystemID not in bySystemID:
            bySystemID[solarsystemID] = []
        bySystemID[solarsystemID].append(station)

    if stuffToPrime:
        cfg.evelocations.Prime(stuffToPrime)

    def hintFunc(stationData):
        hint = ''
        for stationID, itemCount in stationData:
            shortStationName = uix.EditStationName(cfg.evelocations.Get(stationID).name, usename=1)
            subc = GetByLabel('UI/Map/StarModeHandler/StationNameWithItemCount', shortStationName=shortStationName, numItems=itemCount)
            if hint:
                hint += '<br>'
            hint += '- <url=localsvc:service=assets&method=Show&stationID=%d>%s</url>' % (stationID, subc)

        return hint

    for solarsystemID, stations in bySystemID.iteritems():
        itemCount = sum((station.itemCount for station in stations))
        size = 4.0 + math.log10(itemCount)
        stationData = [ (station.stationID, station.itemCount) for station in stations ]
        colorInfo.solarSystemDict[solarsystemID] = (size,
         1.0,
         (hintFunc, (stationData,)),
         assetColor)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/assetsNoAssets'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/assetsHasAssets'), assetColor, data=None))
    return


def ColorStarsByVisited(colorInfo, starColorMode):
    history = sm.RemoteSvc('map').GetSolarSystemVisits()
    visited = []
    for entry in history:
        visited.append((entry.lastDateTime, entry.solarSystemID, entry.visits))

    if len(visited):
        divisor = 1.0 / float(len(visited))
    visited.sort()
    starmap = sm.GetService('starmap')
    hintFunc = lambda solarSystemID, visits, lastDateTime: GetByLabel('UI/Map/StarModeHandler/visitedLastVisist', system=solarSystemID, count=visits, lastVisit=lastDateTime)
    for i, (lastDateTime, solarSystemID, visits) in enumerate(visited):
        colorInfo.solarSystemDict[solarSystemID] = (3.0 + math.log10(float(visits)) * 4.0,
         float(i) * divisor,
         (hintFunc, (solarSystemID, visits, lastDateTime)),
         None)

    colorInfo.colorList = (trinity.TriColor(0.3, 0.0, 0.0), trinity.TriColor(1.0, 0.0, 0.0), trinity.TriColor(1.0, 1.0, 0.0))
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/visitedNever'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/visitedShortest'), colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/visitedLongest'), colorInfo.colorList[2], data=None))
    return


def ColorStarsBySecurity(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    for solarSystemID, solarSystem in starmap.GetKnownUniverseSolarSystems().iteritems():
        secStatus = starmap.map.GetSecurityStatus(solarSystemID)
        colorInfo.solarSystemDict[solarSystemID] = (2,
         secStatus,
         None,
         None)

    colorInfo.colorList = COLORCURVE_SECURITY
    for i in xrange(0, 11):
        lbl = GetByLabel('UI/Map/StarModeHandler/securityLegendItem', level=1.0 - i * 0.1)
        colorInfo.legend.add(LegendItem(i, lbl, COLORCURVE_SECURITY[10 - i], data=None))

    return


def ColorStarsBySovChanges(colorInfo, starColorMode, changeMode):
    if changeMode in (mapcommon.SOV_CHANGES_OUTPOST_GAIN, mapcommon.SOV_CHANGES_SOV_GAIN):
        color = trinity.TriColor(0.0, 1.0, 0.0)
    elif changeMode in (mapcommon.SOV_CHANGES_OUTPOST_LOST, mapcommon.SOV_CHANGES_SOV_LOST):
        color = trinity.TriColor(1.0, 0.0, 0.0)
    else:
        color = trinity.TriColor(0.9, 0.6, 0.1)
    changes = GetSovChangeList(changeMode)
    hintFunc = lambda comments: '<br><br>'.join(comments)
    for solarSystemID, comments in changes.iteritems():
        colorInfo.solarSystemDict[solarSystemID] = (len(comments) * 2.0,
         1.0,
         (hintFunc, (comments,)),
         color)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/sovereigntyNoSovChanges'), mapcommon.NEUTRAL_COLOR, None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/sovereigntySovChanges'), color, None))
    return


def GetSovChangeList(changeMode):
    data = sm.GetService('sov').GetRecentActivity()
    changes = []
    resultMap = {}
    toPrime = set()
    for item in data:
        if item.stationID is None:
            if bool(changeMode & mapcommon.SOV_CHANGES_SOV_GAIN) and item.ownerID is not None:
                changes.append((item.solarSystemID, 'UI/Map/StarModeHandler/sovereigntySovGained', (None, item.ownerID)))
                toPrime.add(item.ownerID)
            elif bool(changeMode & mapcommon.SOV_CHANGES_SOV_LOST) and item.oldOwnerID is not None:
                changes.append((item.solarSystemID, 'UI/Map/StarModeHandler/sovereigntySovLost', (item.oldOwnerID, None)))
                toPrime.add(item.oldOwnerID)
        elif bool(changeMode & mapcommon.SOV_CHANGES_OUTPOST_GAIN) and item.oldOwnerID is None:
            changes.append((item.solarSystemID, 'UI/Map/StarModeHandler/sovereigntyNewOutpost', (None, item.ownerID)))
            toPrime.add(item.ownerID)
        elif bool(changeMode & mapcommon.SOV_CHANGES_OUTPOST_GAIN) and item.ownerID is not None:
            changes.append((item.solarSystemID, 'UI/Map/StarModeHandler/sovereigntyConqueredOutpost', (item.oldOwnerID, item.ownerID)))
            toPrime.add(item.ownerID)
            toPrime.add(item.oldOwnerID)

    cfg.eveowners.Prime(list(toPrime))
    for solarSystemID, text, owners in changes:
        oldOwner = '' if owners[0] is None else cfg.eveowners.Get(owners[0]).ownerName
        owner = '' if owners[1] is None else cfg.eveowners.Get(owners[1]).ownerName
        if solarSystemID not in resultMap:
            resultMap[solarSystemID] = []
        resultMap[solarSystemID].append(GetByLabel(text, owner=owner, oldOwner=oldOwner))

    return resultMap


def ColorStarsByFactionStandings(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    colorByFaction = {}
    neutral = trinity.TriColor(*COLOR_STANDINGS_NEUTRAL)
    for factionID in starmap.GetAllFactionsAndAlliances():
        colorByFaction[factionID] = trinity.TriColor(*starmap.GetColorByStandings(factionID))

    lbl = GetByLabel('UI/Map/StarModeHandler/factionStandings')
    hintFunc = lambda : lbl
    for solarSystemID, solarSystem in starmap.GetKnownUniverseSolarSystems().iteritems():
        color = colorByFaction.get(solarSystem.factionID, neutral)
        colorInfo.solarSystemDict[solarSystemID] = (2.0,
         1.0,
         (hintFunc, ()),
         color)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/factionGoodStandings'), trinity.TriColor(*COLOR_STANDINGS_GOOD), data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/factionNeutralStandings'), trinity.TriColor(*COLOR_STANDINGS_NEUTRAL), data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/factionBadStandings'), trinity.TriColor(*COLOR_STANDINGS_BAD), data=None))
    return


def ColorStarsByFaction(colorInfo, starColorMode):
    factionID = starColorMode[1]
    starmap = sm.GetService('starmap')
    allianceSolarSystems = starmap.GetAllianceSolarSystems()
    sovBySolarSystemID = {}
    toPrime = set()
    for solarSystemID, solarSystem in starmap.GetKnownUniverseSolarSystems().iteritems():
        if factionID == mapcommon.STARMODE_FILTER_EMPIRE:
            secClass = starmap.map.GetSecurityStatus(solarSystemID)
            if not util.IsFaction(solarSystem.factionID) or secClass == const.securityClassZeroSec:
                continue
        sovHolderID = starmap._GetFactionIDFromSolarSystem(allianceSolarSystems, solarSystemID)
        if sovHolderID is None:
            continue
        if factionID >= 0 and sovHolderID != factionID:
            continue
        sovBySolarSystemID[solarSystemID] = sovHolderID
        toPrime.add(sovHolderID)

    cfg.eveowners.Prime(list(toPrime))
    hintFunc = lambda name: GetByLabel('UI/Map/StarModeHandler/factionSovereignty', name=name)
    for solarSystemID, sovHolderID in sovBySolarSystemID.iteritems():
        name = cfg.eveowners.Get(sovHolderID).name
        col = starmap.GetFactionOrAllianceColor(sovHolderID)
        colorInfo.solarSystemDict[solarSystemID] = (2.0,
         0.0,
         (hintFunc, (name,)),
         col)
        colorInfo.legend.add(LegendItem(None, name, col, data=sovHolderID))

    return


def ColorStarsByMilitia(colorInfo, starColorMode):
    factionID = starColorMode[1]
    if factionID < -1:
        self.LogError('Invalid factionID', factionID)
        return
    else:
        facWar = sm.GetService('facwar')
        starmap = sm.GetService('starmap')
        facWarSolarSystemsOccupiers = facWar.GetFacWarSystemsOccupiers()
        warFactions = facWar.GetWarFactions()
        colByFaction = {fID:starmap.GetFactionOrAllianceColor(fID) for fID in warFactions}
        nameByFaction = {fID:cfg.eveowners.Get(fID).name for fID in warFactions}
        maxPointsByFaction = {fID:1 for fID in warFactions}
        maxThresholdByFaction = {fID:1 for fID in warFactions}
        facWarData = starmap.GetFacWarData()
        occupiedSystems = {}
        for systemID, currentOccupierID in facWarSolarSystemsOccupiers.iteritems():
            if currentOccupierID == factionID or factionID == -1:
                if systemID in facWarData:
                    threshold, points, occupierID = facWarData[systemID]
                    if occupierID is not None and occupierID != currentOccupierID:
                        state = const.contestionStateCaptured
                    elif threshold > points:
                        if points == 0:
                            state = const.contestionStateNone
                        else:
                            state = const.contestionStateContested
                    else:
                        state = const.contestionStateVulnerable
                    maxThresholdByFaction[currentOccupierID] = max(threshold, maxThresholdByFaction[currentOccupierID])
                    maxPointsByFaction[currentOccupierID] = max(points, maxPointsByFaction[currentOccupierID])
                else:
                    points, state = 0, const.contestionStateNone
                occupiedSystems[systemID] = (currentOccupierID, points, state)

        hintFunc = lambda name, status: GetByLabel('UI/Map/StarModeHandler/militiaSystemStatus', name=name, status=status)
        multiplierByFaction = {fID:max(1.0, maxThresholdByFaction[fID] / maxPointsByFaction[fID]) for fID in maxThresholdByFaction.keys()}
        for particleID, solarSystemID in starmap.particleIDToSystemIDMap.iteritems():
            if solarSystemID in occupiedSystems:
                solarsystem = starmap.map.GetItem(solarSystemID)
                if solarsystem is None:
                    continue
                occupierID, points, state = occupiedSystems[solarSystemID]
                age = multiplierByFaction[occupierID] * float(points)
                size = 2.0 + pow(age, 0.35)
                statusText = sm.GetService('infoPanel').GetSolarSystemStatusText(state, True)
                colorInfo.solarSystemDict[solarSystemID] = (size,
                 age,
                 (hintFunc, (nameByFaction[occupierID], statusText)),
                 colByFaction[occupierID])
                colorInfo.legend.add(LegendItem(None, nameByFaction[occupierID], colByFaction[occupierID], data=occupierID))
                colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.0))

        return


def ColorStarsByRegion(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    hintFunc = lambda name: GetByLabel('UI/Map/StarModeHandler/regionNameEntry', name=name)
    for regionID, region in starmap.GetKnownUniverseRegions().iteritems():
        regionName = cfg.evelocations.Get(regionID).name
        col = starmap.GetRegionColor(regionID)
        for solarSystemID in region.solarSystemIDs:
            colorInfo.solarSystemDict[solarSystemID] = (2,
             1.0,
             (hintFunc, (regionName,)),
             col)

        colorInfo.legend.add(LegendItem(None, regionName, col, data=regionID))

    return


def HintCargoIllegality(attackTypeIDs, confiscateTypeIDs):
    systemDescription = ''
    for typeID in attackTypeIDs:
        if systemDescription != '':
            systemDescription += '<br>'
        systemDescription += GetByLabel('UI/Map/StarModeHandler/legalityAttackHint', stuff=evetypes.GetName(typeID))

    for typeID in confiscateTypeIDs:
        if systemDescription != '':
            systemDescription += '<br>'
        systemDescription += GetByLabel('UI/Map/StarModeHandler/legalityConfiscateHint', item=evetypes.GetName(typeID))

    return systemDescription


def ColorStarsByCargoIllegality(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    invCache = sm.GetService('invCache')
    CONFISCATED_COLOR = trinity.TriColor(0.8, 0.4, 0.0)
    ATTACKED_COLOR = trinity.TriColor(1.0, 0.0, 0.0)
    invCache = sm.GetService('invCache')
    activeShipID = util.GetActiveShip()
    if activeShipID is None:
        shipCargo = []
    else:
        inv = invCache.GetInventoryFromId(activeShipID, locationID=session.stationid2)
        shipCargo = inv.List()
    factionIllegality = {}
    while len(shipCargo) > 0:
        item = shipCargo.pop(0)
        if item.groupID in [const.groupCargoContainer,
         const.groupSecureCargoContainer,
         const.groupAuditLogSecureContainer,
         const.groupFreightContainer]:
            shipCargo.extend(invCache.GetInventoryFromId(item.itemID).List())
        itemIllegalities = inventorycommon.typeHelpers.GetIllegality(item.typeID)
        if itemIllegalities:
            for factionID, illegality in itemIllegalities.iteritems():
                if factionID not in factionIllegality:
                    factionIllegality[factionID] = {}
                if item.typeID not in factionIllegality[factionID]:
                    factionIllegality[factionID][item.typeID] = [max(0.0, illegality.confiscateMinSec), max(0.0, illegality.attackMinSec)]

    for solarSystemID, solarSystem in starmap.GetKnownUniverseSolarSystems().iteritems():
        colour = None
        factionID = solarSystem.factionID
        if factionID is None or factionID not in factionIllegality:
            continue
        systemIllegality = False
        attackTypeIDs = []
        confiscateTypeIDs = []
        securityStatus = starmap.map.GetSecurityStatus(solarSystemID)
        for typeID in factionIllegality[factionID]:
            if securityStatus >= factionIllegality[factionID][typeID][1]:
                systemIllegality = True
                if not colour or colour[0] < 2:
                    colour = (2, ATTACKED_COLOR)
                attackTypeIDs.append(typeID)
            elif securityStatus >= factionIllegality[factionID][typeID][0]:
                systemIllegality = True
                if not colour:
                    colour = (1, CONFISCATED_COLOR)
                confiscateTypeIDs.append(typeID)

        if systemIllegality:
            colorInfo.solarSystemDict[solarSystemID] = (3.0,
             0.0,
             (HintCargoIllegality, (attackTypeIDs, confiscateTypeIDs)),
             colour[1])

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/legalityNoConsequences'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/legalityConfiscate'), CONFISCATED_COLOR, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/legalityWillAttack'), ATTACKED_COLOR, data=None))
    return


def ColorStarsByNumPilots(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    sol, sta, statDivisor = sm.ProxySvc('machoNet').GetClusterGameStatistics('EVE', ({}, {}, 0))
    maxCount = 0
    total = 0
    docked = 0
    multiplier = 1.0
    pilotcountDict = {}
    for sfoo in sol.iterkeys():
        solarSystemID = sfoo + 30000000
        amount_docked = sta.get(sfoo, 0) / statDivisor
        amount_inspace = (sol.get(sfoo, 0) - sta.get(sfoo, 0)) / statDivisor
        if starColorMode == mapcommon.STARMODE_PLAYERCOUNT:
            amount = amount_inspace
        else:
            amount = amount_docked
        pilotcountDict[solarSystemID] = amount
        total = total + amount
        if amount > maxCount:
            maxCount = amount

    if maxCount > 0:
        multiplier /= math.sqrt(maxCount)
    sorted = pilotcountDict.values()
    sorted.sort()
    if starColorMode == mapcommon.STARMODE_PLAYERCOUNT:
        hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/StarModeHandler/pilotsInSpace', count=count, solarSystem=solarSystemID)
    else:
        hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/StarModeHandler/pilotsInStation', count=count, solarSystem=solarSystemID)
    for solarSystemID, pilotCount in pilotcountDict.iteritems():
        if pilotCount == 0:
            continue
        size = 2 * math.sqrt(pilotCount)
        colorInfo.solarSystemDict[solarSystemID] = (size,
         math.sqrt(pilotCount) * multiplier,
         (hintFunc, (pilotCount, solarSystemID)),
         None)

    colorInfo.colorList = (trinity.TriColor(0.25, 0.25, 0.0), trinity.TriColor(0.5, 0.0, 0.0))
    colorCurve = starmap.GetColorCurve(colorInfo.colorList)
    startColor = starmap.GetColorCurveValue(colorCurve, multiplier)
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/pilotsNone'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/pilotsOne'), startColor, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/pilotsMany', maxCount=maxCount), colorInfo.colorList[-1], data=None))
    return


def ColorStarsByStationCount(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starmap.stationCountCache is None:
        starmap.stationCountCache = sm.RemoteSvc('map').GetStationCount()
    history = starmap.stationCountCache
    maxCount = 0
    for solarSystemID, amount in history:
        if amount > maxCount:
            maxCount = amount

    multiplier = 0
    if maxCount > 0:
        multiplier = 1.0 / float(maxCount)
    hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/StarModeHandler/stationsCount', count=count, solarSystem=solarSystemID)
    for solarSystemID, amount in history:
        age = multiplier * float(amount)
        size = 2.0 + pow(age, 0.5) * 4.0
        colorInfo.solarSystemDict[solarSystemID] = (size,
         age,
         (hintFunc, (amount, solarSystemID)),
         None)

    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.0))
    colorCurve = starmap.GetColorCurve(colorInfo.colorList)
    startColor = starmap.GetColorCurveValue(colorCurve, multiplier)
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/stationsNone'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/stationsOne'), startColor, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/stationsMany', maxCount=maxCount), colorInfo.colorList[-1], data=None))
    return


def HintDungeons(dungeons):
    comments = []
    for dungeonID, difficulty, dungeonName in dungeons:
        ded = ''
        if difficulty:
            ded = GetByLabel('UI/Map/StarModeHandler/dungeonDedDiffaculty', count=difficulty)
        comments.append(GetByLabel('UI/Map/StarModeHandler/dungeonDedLegendHint', dungeonName=dungeonName, dedName=ded))

    return '<br>'.join(comments)


def ColorStarsByDungeons(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starColorMode == mapcommon.STARMODE_DUNGEONS:
        dungeons = sm.RemoteSvc('map').GetDeadspaceComplexMap(eve.session.languageID)
    elif starColorMode == mapcommon.STARMODE_DUNGEONSAGENTS:
        dungeons = sm.RemoteSvc('map').GetDeadspaceAgentsMap(eve.session.languageID)
    if dungeons is None:
        return
    else:
        solmap = {}
        for solarSystemID, dungeonID, difficulty, dungeonName in dungeons:
            if solarSystemID in solmap:
                solmap[solarSystemID].append((dungeonID, difficulty, dungeonName))
            else:
                solmap[solarSystemID] = [(dungeonID, difficulty, dungeonName)]

        for solarSystemID, solarSystemDungeons in solmap.iteritems():
            maxDifficulty = 1
            for dungeonID, difficulty, dungeonName in solarSystemDungeons:
                if difficulty:
                    maxDifficulty = max(maxDifficulty, difficulty)

            maxDifficulty = (10 - maxDifficulty) / 9.0
            colorInfo.solarSystemDict[solarSystemID] = (3.0 * len(solarSystemDungeons),
             maxDifficulty,
             (HintDungeons, (solarSystemDungeons,)),
             None)

        colorInfo.colorList = COLORCURVE_SECURITY
        colorCurve = starmap.GetColorCurve(COLORCURVE_SECURITY)
        for i in xrange(0, 10):
            lbl = GetByLabel('UI/Map/StarModeHandler/dungeonDedLegendDiffaculty', difficulty=i + 1)
            colorInfo.legend.add(LegendItem(i, lbl, starmap.GetColorCurveValue(colorCurve, (9 - i) / 9.0), data=None))

        return


def ColorStarsByJumps1Hour(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatJumps, 1)
    history = []
    for entry in historyDB:
        if entry.value1 > 0:
            history.append((entry.solarSystemID, entry.value1))

    maxCount = 0
    for solarSystemID, amount in history:
        if amount > maxCount:
            maxCount = amount

    if maxCount > 1:
        divisor = 1.0 / math.log(pow(float(maxCount), 4.0))
        hintFunc = lambda count, solarSystemID: GetByLabel('UI/Map/StarModeHandler/JumpsLastHour', count=count, solarSystem=solarSystemID)
        for solarSystemID, amount in history:
            age = divisor * math.log(pow(float(amount), 4.0))
            size = 2.0 + pow(age, 0.5) * 2.0
            colorInfo.solarSystemDict[solarSystemID] = (size,
             age,
             (hintFunc, (amount, solarSystemID)),
             None)

    colorInfo.colorList = (trinity.TriColor(0.0, 0.0, 1.0),
     trinity.TriColor(0.0, 1.0, 1.0),
     trinity.TriColor(1.0, 1.0, 0.0),
     trinity.TriColor(1.0, 0.0, 0.0))
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/jumpsNumber', count=0), colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/jumpsNumber', count=maxCount), colorInfo.colorList[-1], data=None))
    return


def ColorStarsByKills(colorInfo, starColorMode, statID, hours):
    starmap = sm.GetService('starmap')
    historyDB = sm.RemoteSvc('map').GetHistory(statID, hours)
    history = []
    for entry in historyDB:
        if entry.value1 - entry.value2 > 0:
            history.append((entry.solarSystemID, entry.value1 - entry.value2))

    maxCount = 0
    for solarSystemID, amount in history:
        if amount > maxCount:
            maxCount = amount

    if maxCount > 0:
        divisor = 1.0 / float(maxCount)
    hintFunc = lambda count, solarSystemID, hours: GetByLabel('UI/Map/StarModeHandler/killsShipsInLast', count=count, solarSystem=solarSystemID, hours=hours)
    for solarSystemID, amount in history:
        age = divisor * float(amount)
        size = 2.0 + pow(amount, 0.5) * 4.0
        colorInfo.solarSystemDict[solarSystemID] = (size,
         age,
         (hintFunc, (amount, solarSystemID, hours)),
         None)

    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.01))
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/killsNumber', count=0), colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/killsNumber', count=maxCount), colorInfo.colorList[-1], data=None))
    return


def ColorStarsByPodKills(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    if starColorMode == mapcommon.STARMODE_PODKILLS24HR:
        hours = 24
        historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, 24)
    else:
        hours = 1
        historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, 1)
    history = []
    for entry in historyDB:
        if entry.value3 > 0:
            history.append((entry.solarSystemID, entry.value3))

    maxCount = 0
    for solarSystemID, amount in history:
        if amount > maxCount:
            maxCount = amount

    divisor = 0.0
    if maxCount > 0:
        divisor = 1.0 / float(maxCount)
    hintFunc = lambda solarSystemID, hours, count: GetByLabel('UI/Map/StarModeHandler/killsPodInLast', solarSystem=solarSystemID, hours=hours, count=count)
    for solarSystemID, amount in history:
        age = divisor * float(amount)
        size = 2.0 + pow(amount, 0.5) * 4.0
        colorInfo.solarSystemDict[solarSystemID] = (size,
         age,
         (hintFunc, (solarSystemID, hours, amount)),
         None)

    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.01))
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/killsPodNumber', count=0), colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/killsPodNumber', count=maxCount), colorInfo.colorList[-1], data=None))
    return


def ColorStarsByFactionKills(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    hours = 24
    historyDB = sm.RemoteSvc('map').GetHistory(const.mapHistoryStatKills, hours)
    history = []
    for entry in historyDB:
        if entry.value2 > 0:
            history.append((entry.solarSystemID, entry.value2))

    maxCount = 0
    for solarSystemID, amount in history:
        if amount > maxCount:
            maxCount = amount

    divisor = 0.0
    if maxCount > 0:
        divisor = 1.0 / float(maxCount)
    hintFunc = lambda solarSystemID, hours, count: GetByLabel('UI/Map/StarModeHandler/killsFactionInLast', solarSystem=solarSystemID, hours=hours, count=count)
    for solarSystemID, amount in history:
        age = divisor * float(amount)
        size = 1.0 + math.log(amount) * 2.0
        colorInfo.solarSystemDict[solarSystemID] = (size,
         age,
         (hintFunc, (solarSystemID, hours, amount)),
         None)

    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.01))
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/killsNumber', count=0), colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/killsNumber', count=maxCount), colorInfo.colorList[-1], data=None))
    return


def ColorStarsByBookmarks(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    bms = sm.GetService('bookmarkSvc').GetAllBookmarks()
    highlightSystems = {}
    for bookmark in bms.itervalues():
        item = starmap.map.GetItem(bookmark.locationID)
        if item is not None and item.typeID == const.typeSolarSystem:
            solarSystemID = bookmark.locationID
        else:
            solarSystemID = bookmark.itemID
        memo = bookmark.memo
        if len(memo):
            tabindex = string.find(memo, '\t')
            if tabindex != -1:
                comment = memo[:tabindex]
        else:
            comment = None
        if not highlightSystems.has_key(solarSystemID):
            highlightSystems[solarSystemID] = [comment]
        else:
            highlightSystems[solarSystemID].append(comment)

    for system, comments in highlightSystems.iteritems():
        colorInfo.solarSystemDict[system] = (4,
         1.0,
         (lambda comments: '<br>'.join(comments), (comments,)),
         None)

    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.01))
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/bookmarksNoneHere'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/bookmarksSomeHere'), colorInfo.colorList[-1], data=None))
    return


def ColorStarsByCynosuralFields(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    fields = sm.RemoteSvc('map').GetBeaconCount()
    highlightSystems = {}
    orange = trinity.TriColor(1.0, 0.4, 0.0, 1.0)
    green = trinity.TriColor(0.2, 1.0, 1.0, 1.0)
    red = trinity.TriColor(1.0, 0.0, 0.0, 1.0)
    hintFuncTotal = lambda count: GetByLabel('UI/Map/StarModeHandler/cynoActiveFieldsGeneratorsNumber', count=count)
    hintFuncModule = lambda count: GetByLabel('UI/Map/StarModeHandler/cynoActiveFieldsNumber', count=count)
    hintFuncStructure = lambda count: GetByLabel('UI/Map/StarModeHandler/cynoActiveGeneratorNumber', count=count)
    for solarSystemID, cnt in fields.iteritems():
        moduleCnt, structureCnt = cnt
        if moduleCnt > 0 and structureCnt > 0:
            ttlcnt = moduleCnt + structureCnt
            colorInfo.solarSystemDict[solarSystemID] = (4 * ttlcnt,
             1.0,
             (hintFuncTotal, (ttlcnt,)),
             red)
        elif moduleCnt:
            colorInfo.solarSystemDict[solarSystemID] = (4 * moduleCnt,
             1.0,
             (hintFuncModule, (moduleCnt,)),
             green)
        elif structureCnt:
            colorInfo.solarSystemDict[solarSystemID] = (4 * structureCnt,
             1.0,
             (hintFuncStructure, (structureCnt,)),
             orange)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/cynoNoFieldsGenerators'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/cynoActiveFields'), green, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/cynoActiveGenerators'), orange, data=None))
    colorInfo.legend.add(LegendItem(3, GetByLabel('UI/Map/StarModeHandler/cynoActiveFieldsGenerators'), red, data=None))
    return


def ColorStarsByCorpAssets(colorInfo, starColorMode, assetKey, legendName):
    rows = sm.RemoteSvc('corpmgr').GetAssetInventory(eve.session.corpid, assetKey)
    solarsystems = {}
    stuffToPrime = []
    for row in rows:
        stationID = row.locationID
        try:
            solarsystemID = sm.GetService('ui').GetStation(row.locationID).solarSystemID
        except:
            solarsystemID = row.locationID

        if solarsystemID not in solarsystems:
            solarsystems[solarsystemID] = {}
            stuffToPrime.append(solarsystemID)
        if stationID not in solarsystems[solarsystemID]:
            solarsystems[solarsystemID][stationID] = []
            stuffToPrime.append(stationID)
        solarsystems[solarsystemID][stationID].append(row)

    cfg.evelocations.Prime(stuffToPrime)
    hintFunc = lambda stationIDs: '<br>'.join([ cfg.evelocations.Get(stationID).name for stationID in stationIDs ])
    for solarsystemID, stations in solarsystems.iteritems():
        total = 100000
        color = trinity.TriColor(1.0, 0.8, 0.0, 1.0)
        size = 4.0 + math.log10(total)
        colorInfo.solarSystemDict[solarsystemID] = (size,
         1.0,
         (hintFunc, (stations.keys(),)),
         color)

    colorInfo.colorList = (trinity.TriColor(0.25, 0.25, 0.0), trinity.TriColor(0.5, 0.1, 0.0))
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/corpNoAssets'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, legendName, colorInfo.colorList[-1], data=None))
    return


def ColorStarsByServices(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    serviceTypeID = starColorMode[1]
    stations, opservices, services = sm.RemoteSvc('map').GetStationExtraInfo()
    opservDict = {}
    stationIDs = []
    solarsystems = {}
    for each in opservices:
        if each.operationID not in opservDict:
            opservDict[each.operationID] = []
        opservDict[each.operationID].append(each.serviceID)

    if starmap.warFactionByOwner is None and serviceTypeID == const.stationServiceNavyOffices:
        starmap.warFactionByOwner = {}
        factions = sm.GetService('facwar').GetWarFactions().keys()
        for stationRow in stations:
            ownerID = stationRow.ownerID
            if ownerID not in starmap.warFactionByOwner:
                faction = sm.GetService('faction').GetFaction(ownerID)
                if faction and faction in factions:
                    starmap.warFactionByOwner[ownerID] = faction

    if serviceTypeID == const.stationServiceSecurityOffice:
        secOfficeSvc = sm.GetService('securityOfficeSvc')
    for stationRow in stations:
        solarSystemID = stationRow.solarSystemID
        if stationRow.operationID == None:
            continue
        if serviceTypeID not in opservDict[stationRow.operationID]:
            continue
        if serviceTypeID == const.stationServiceNavyOffices and stationRow.ownerID not in starmap.warFactionByOwner:
            continue
        if serviceTypeID == const.stationServiceSecurityOffice and not secOfficeSvc.CanAccessServiceInStation(stationRow.stationID):
            continue
        if solarSystemID not in solarsystems:
            solarsystems[solarSystemID] = []
        solarsystems[solarSystemID].append(stationRow.stationID)
        stationIDs.append(stationRow.stationID)

    cfg.evelocations.Prime(stationIDs)
    red = trinity.TriColor(1.0, 0.0, 0.0, 1.0)
    hintFunc = lambda stationIDs: '<br>'.join([ cfg.evelocations.Get(stationID).name for stationID in stationIDs ])

    def hintFunc2(stationIDs):
        hint = ''
        for stationID in stationIDs:
            station = sm.StartService('ui').GetStation(stationID)
            stationName = cfg.evelocations.Get(stationID).name
            stationTypeID = station.stationTypeID
            if hint:
                hint += '<br>'
            hint += '- <url=showinfo:%d//%d>%s</url>' % (stationTypeID, stationID, stationName)

        return hint

    for solarsystemID, stationIDs in solarsystems.iteritems():
        colorInfo.solarSystemDict[solarsystemID] = (4.0,
         1.0,
         (hintFunc2, (stationIDs,)),
         red)

    colorInfo.colorList = (trinity.TriColor(0.25, 0.25, 0.0), trinity.TriColor(0.5, 0.1, 0.0))
    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/serviceNoneHere'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/serviceHasServices'), red, data=None))
    return


def ColorStarsByFleetMembers(colorInfo, starColorMode):
    fleetComposition = sm.GetService('fleet').GetFleetComposition()
    if fleetComposition is not None:
        solarsystems = {}
        for each in fleetComposition:
            if each.solarSystemID not in solarsystems:
                solarsystems[each.solarSystemID] = []
            solarsystems[each.solarSystemID].append(each.characterID)

        hintFunc = lambda characterIDs: '<br>'.join([ cfg.eveowners.Get(characterID).name for characterID in characterIDs ])
        for locationID, charIDs in solarsystems.iteritems():
            colorInfo.solarSystemDict[locationID] = (4.0,
             1.0,
             (hintFunc, (charIDs,)),
             DEFAULT_MAX_COLOR)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/fleetNoMembers'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/fleetHasMembers'), DEFAULT_MAX_COLOR, data=None))
    return


def ColorStarsByCorpMembers(colorInfo, starColorMode):
    corp = sm.RemoteSvc('map').GetMyExtraMapInfo()
    if corp is not None:
        solarsystems = {}
        for each in corp:
            if each.locationID not in solarsystems:
                solarsystems[each.locationID] = []
            solarsystems[each.locationID].append(each.characterID)

        hintFunc = lambda characterIDs: '<br>'.join([ cfg.eveowners.Get(characterID).name for characterID in characterIDs ])
        for locationID, charIDs in solarsystems.iteritems():
            colorInfo.solarSystemDict[locationID] = (4,
             1.0,
             (hintFunc, (charIDs,)),
             DEFAULT_MAX_COLOR)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/corpNoMembers'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/corpHasMembers'), DEFAULT_MAX_COLOR, data=None))
    return


def HintMyAgents(stations, npcDivisions):
    caption = ''
    for stationID, agents in stations.iteritems():
        caption += GetByLabel('UI/Map/StarModeHandler/agentBoldStationName', stationName=uix.EditStationName(cfg.evelocations.Get(stationID).name, 1)) + '<br>'
        for agent in agents:
            caption += GetByLabel('UI/Map/StarModeHandler/agentCaptionDetails', divisionName=npcDivisions[agent.divisionID].divisionName, agentName=cfg.eveowners.Get(agent.agentID).name, level=agent.level)
            caption += '<br>'

        caption += '<br>'

    return caption


def HintMyAgents2(stations, npcDivisions):
    caption = ''
    for stationID, agents in stations.iteritems():
        for agent in agents:
            agentOwner = cfg.eveowners.Get(agent.agentID)
            agentString = GetByLabel('UI/Map/StarModeHandler/agentCaptionDetails', divisionName=npcDivisions[agent.divisionID].divisionName, agentName=agentOwner.name, level=agent.level)
            if caption:
                caption += '<br>'
            caption += '- <url=showinfo:%d//%d>%s</url>' % (agentOwner.typeID, agent.agentID, agentString)

    return caption


def ColorStarsByMyAgents(colorInfo, starColorMode):
    standingInfo = sm.RemoteSvc('map').GetMyExtraMapInfoAgents().Index('fromID')
    solarsystems = {}
    valid = (const.agentTypeBasicAgent, const.agentTypeResearchAgent, const.agentTypeFactionalWarfareAgent)
    agentsByID = sm.GetService('agents').GetAgentsByID()
    facWarService = sm.GetService('facwar')
    skills = {}
    for agentID in agentsByID:
        agent = agentsByID[agentID]
        fa = standingInfo.get(agent.factionID, 0.0)
        if fa:
            fa = fa.rank * 10.0
        co = standingInfo.get(agent.corporationID, 0.0)
        if co:
            co = co.rank * 10.0
        ca = standingInfo.get(agent.agentID, 0.0)
        if ca:
            ca = ca.rank * 10.0
        isLimitedToFacWar = False
        if agent.agentTypeID == const.agentTypeFactionalWarfareAgent and facWarService.GetCorporationWarFactionID(agent.corporationID) != session.warfactionid:
            isLimitedToFacWar = True
        if agent.agentTypeID in valid and util.CanUseAgent(agent.level, agent.agentTypeID, fa, co, ca, agent.corporationID, agent.factionID, skills) and isLimitedToFacWar == False:
            if agent.stationID:
                if agent.solarsystemID not in solarsystems:
                    solarsystems[agent.solarsystemID] = {}
                if agent.stationID not in solarsystems[agent.solarsystemID]:
                    solarsystems[agent.solarsystemID][agent.stationID] = []
                solarsystems[agent.solarsystemID][agent.stationID].append(agent)

    hintFunc = HintMyAgents2
    npcDivisions = sm.GetService('agents').GetDivisions()
    for solarsystemID, stations in solarsystems.iteritems():
        totalAgents = sum((len(agents) for agents in stations.itervalues()))
        colorInfo.solarSystemDict[solarsystemID] = (int(totalAgents),
         1.0,
         (hintFunc, (stations, npcDivisions)),
         DEFAULT_MAX_COLOR)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/agentNoneHere'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/agentSomeHere'), DEFAULT_MAX_COLOR, data=None))
    return


def ColorStarsByAvoidedSystems(colorInfo, starColorMode):
    avoidanceSolarSystemIDs = sm.GetService('clientPathfinderService').GetExpandedAvoidanceItems()
    red = trinity.TriColor(1.0, 0.0, 0.0)
    hintFunc = lambda : GetByLabel('UI/Map/StarModeHandler/advoidSystemOnList')
    for solarSystemID in avoidanceSolarSystemIDs:
        colorInfo.solarSystemDict[solarSystemID] = (1,
         1.0,
         (hintFunc, ()),
         red)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/advoidNotAdvoided'), mapcommon.NEUTRAL_COLOR, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/advoidAdvoided'), red, data=None))
    return


def ColorStarsByRealSunColor(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    for solarSystemID, solarSystem in starmap.GetKnownUniverseSolarSystems().iteritems():
        colorInfo.solarSystemDict[solarSystemID] = (1,
         0.0,
         None,
         trinity.TriColor(*solarSystem.star.color))

    colorInfo.overglowFactor = mapcommon.ACTUAL_COLOR_OVERGLOWFACTOR
    for typeID, sunType in mapcommon.SUN_DATA.iteritems():
        name = evetypes.GetName(typeID)
        colorInfo.legend.add(LegendItem(name, name, trinity.TriColor(*sunType.color), data=None))

    return


def ColorStarsByPIScanRange(colorInfo, starColorMode):
    starmap = sm.GetService('starmap')
    highlightSystems = {}
    playerLoc = cfg.evelocations.Get(session.solarsystemid2)
    playerPos = (playerLoc.x, playerLoc.y, playerLoc.z)
    skills = sm.GetService('skills').MySkillLevelsByID()
    remoteSensing = skills.get(const.typeRemoteSensing, 0)
    hintFunc = lambda range: GetByLabel('UI/Map/StarModeHandler/scanHintDistance', range=range)
    for particleID, solarSystemID in starmap.particleIDToSystemIDMap.iteritems():
        systemLoc = cfg.evelocations.Get(solarSystemID)
        systemPos = (systemLoc.x, systemLoc.y, systemLoc.z)
        dist = geo2.Vec3Distance(playerPos, systemPos) / const.LIGHTYEAR
        proximity = None
        for i, each in enumerate(const.planetResourceScanningRanges):
            if not i >= 5 - remoteSensing:
                continue
            if each >= dist:
                proximity = i

        if proximity is not None:
            colorInfo.solarSystemDict[solarSystemID] = (max(1, proximity),
             1.0 / 5.0 * proximity,
             (hintFunc, (dist,)),
             None)

    colorCurve = starmap.GetColorCurve(COLORCURVE_SECURITY)
    for i, each in enumerate(const.planetResourceScanningRanges):
        if not i >= 5 - remoteSensing:
            continue
        lbl = GetByLabel('UI/Map/StarModeHandler/scanLegendDistance', range=const.planetResourceScanningRanges[i])
        colorInfo.legend.add(LegendItem(i, lbl, starmap.GetColorCurveValue(colorCurve, 1.0 / 5.0 * i), data=None))

    return


def ColorStarsByPlanetType(colorInfo, starColorMode):
    planetTypeID = starColorMode[1]
    starmap = sm.GetService('starmap')
    systems = defaultdict(int)
    maxCount = 0
    for solarSystemID, d in starmap.GetKnownUniverseSolarSystems().iteritems():
        if planetTypeID in d.planetCountByType:
            systems[solarSystemID] = v = d.planetCountByType[planetTypeID]
            maxCount = max(maxCount, v)
        else:
            systems[solarSystemID] = 0

    if maxCount > 1:
        divisor = 1.0 / (maxCount - 1)
    else:
        divisor = 1.0
    planetTypeName = evetypes.GetName(planetTypeID)
    caption = planetTypeName + ': %d'
    hintFunc = lambda count: caption % count
    for solarSystemID, count in systems.iteritems():
        age = divisor * float(count)
        size = 2.0 + pow(count, 0.5) * 2.0
        colorInfo.solarSystemDict[solarSystemID] = (size,
         age,
         (hintFunc, (count,)),
         None)

    colorInfo.colorList = (trinity.TriColor(0.46, 0.34, 0.1), trinity.TriColor(0.3, 1.0, 0.3))
    if maxCount > 1:
        colorInfo.legend.add(LegendItem(0, caption % 1, colorInfo.colorList[0], data=None))
    colorInfo.legend.add(LegendItem(1, caption % maxCount, colorInfo.colorList[-1], data=None))
    return


def ColorStarsByMyColonies(colorInfo, starColorMode):
    planetSvc = sm.GetService('planetSvc')
    planetRows = planetSvc.GetMyPlanets()
    if len(planetRows):
        mapSvc = sm.GetService('map')
        systems = defaultdict(int)
        for row in planetRows:
            systems[row.solarSystemID] += 1

        maxCount = max(systems.itervalues())
        divisor = 1.0 if maxCount == 1 else 1.0 / (maxCount - 1)
        hintFunc = lambda count: GetByLabel('UI/Map/StarModeHandler/planetsColoniesCount', count=count)
        for solarSystemID, count in systems.iteritems():
            if maxCount > 1:
                age = divisor * float(count - 1)
            else:
                age = 1.0
            size = 2.0 + pow(count, 0.5) * 4.0
            colorInfo.solarSystemDict[solarSystemID] = (size,
             age,
             (hintFunc, (count,)),
             None)

        colorInfo.colorList = (trinity.TriColor(0.0, 0.22, 0.55), trinity.TriColor(0.2, 0.5, 1.0))
        if maxCount > 1:
            colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/planetsColoniesCount', count=1), colorInfo.colorList[0], data=None))
        colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/planetsColoniesCount', count=maxCount), colorInfo.colorList[-1], data=None))
    return


def ColorStarsByIncursions(colorInfo, starColorMode):
    ms = session.ConnectToRemoteService('map')
    participatingSystems = ms.GetSystemsInIncursions()
    for solarSystem in participatingSystems:
        colorInfo.solarSystemDict[solarSystem.locationID] = GetColorAndHintForIncursionSystem(solarSystem.sceneType, solarSystem.templateNameID)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/incursionStageing'), COLOR_YELLOW, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/incursionPraticipant'), COLOR_ORANGE, data=None))
    return


def ColorStarsByIncursionsGM(colorInfo, starColorMode):
    ms = session.ConnectToRemoteService('map')
    participatingSystems = ms.GetSystemsInIncursionsGM()
    for solarSystem in participatingSystems:
        colorInfo.solarSystemDict[solarSystem.locationID] = GetColorAndHintForIncursionSystemGm(solarSystem.sceneType, solarSystem.templateNameID)

    colorInfo.legend.add(LegendItem(0, GetByLabel('UI/Map/StarModeHandler/incursionStageing'), COLOR_GREEN, data=None))
    colorInfo.legend.add(LegendItem(1, GetByLabel('UI/Map/StarModeHandler/incursionVanguard'), COLOR_PURPLE, data=None))
    colorInfo.legend.add(LegendItem(2, GetByLabel('UI/Map/StarModeHandler/incursionAssault'), COLOR_ORANGE, data=None))
    colorInfo.legend.add(LegendItem(3, GetByLabel('UI/Map/StarModeHandler/incursionHQ'), COLOR_RED, data=None))
    colorInfo.legend.add(LegendItem(4, 'Incursion Staging', COLOR_WHITE, data=None))
    colorInfo.legend.add(LegendItem(5, 'Incursion Spread', COLOR_GRAY, data=None))
    colorInfo.legend.add(LegendItem(6, 'Incursion Final Encounter', COLOR_PURPLE, data=None))
    return


def GetColorAndHintForIncursionSystem(sceneType, templateNameID):
    distributionName = GetByMessageID(templateNameID)
    if distributionName:
        distributionName += '\n'
    if sceneType == taleConst.scenesTypes.staging:
        incursionHint = lambda : distributionName + GetByLabel('UI/Map/StarModeHandler/incursionStageing')
        return (5,
         0,
         (incursionHint, ()),
         COLOR_YELLOW)
    if sceneType == taleConst.scenesTypes.vanguard:
        incursionHint = lambda : distributionName + GetByLabel('UI/Map/StarModeHandler/incursionPraticipant')
        return (2.5,
         1,
         (incursionHint, ()),
         COLOR_ORANGE)
    if sceneType == taleConst.scenesTypes.incursionStaging:
        incursionHint = lambda : distributionName + GetByLabel('UI/Map/StarModeHandler/incursionStageing')
        return (3.75,
         2,
         (incursionHint, ()),
         COLOR_YELLOW)


def GetColorAndHintForIncursionSystemGm(sceneType, templateNameID):
    distributionName = GetByMessageID(templateNameID)
    if distributionName:
        distributionName += '\n'
    if sceneType == taleConst.scenesTypes.staging:
        return (5,
         0,
         (lambda : distributionName + 'Staging', ()),
         COLOR_GREEN)
    if sceneType == taleConst.scenesTypes.vanguard:
        return (2.5,
         1,
         (lambda : distributionName + 'Vanguard', ()),
         COLOR_PURPLE)
    if sceneType == taleConst.scenesTypes.assault:
        return (2.5,
         2,
         (lambda : distributionName + 'Assault', ()),
         COLOR_ORANGE)
    if sceneType == taleConst.scenesTypes.headquarters:
        return (2.5,
         3,
         (lambda : distributionName + 'HeadQuarters', ()),
         COLOR_RED)
    if sceneType in (taleConst.scenesTypes.incursionStaging, taleConst.scenesTypes.incursionLightInfestation):
        return (3.75,
         4,
         (lambda : distributionName + 'Staging', ()),
         COLOR_WHITE)
    if sceneType in (taleConst.scenesTypes.incursionMediumInfestation, taleConst.scenesTypes.incursionHeavyInfestation):
        return (2.5,
         5,
         (lambda : distributionName + 'Incursion Spread', ()),
         COLOR_GRAY)
    if sceneType == taleConst.scenesTypes.incursionFinalEncounter:
        return (2.5,
         6,
         (lambda : distributionName + 'Incursion Final Encounter', ()),
         COLOR_PURPLE)


def ColorStarsByJobs24Hours(colorInfo, starColorMode, activityID):
    systemRows = sm.RemoteSvc('map').GetIndustryJobsOverLast24Hours(activityID)
    if systemRows:
        maxJobs = max((r.noOfJobs for r in systemRows))
        intensityFunc = lambda value: 50 * value / maxJobs
        colorScalarFunc = lambda value: value / maxJobs
        hintFunc = lambda solarSystemID, value: (lambda : GetByLabel('UI/Map/StarModeHandler/jobsStartedLast24Hours', noOfJobs=value), ())
        jobsBySystem = {row.solarSystemID:row.noOfJobs for row in systemRows}
        colorInfo.solarSystemDict.update(_GetColorDict(jobsBySystem, intensityFunc, colorScalarFunc, hintFunc))
        colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.01))


def ColorStarsByIndustryCostModifier(colorInfo, starColorMode, activityID):
    systemRows = sm.RemoteSvc('map').GetIndustryCostModifier(activityID)
    minValue = min(systemRows.values())
    maxValue = max(systemRows.values())
    colorScalarFunc = lambda value: (value - minValue) / (maxValue - minValue)
    intensityFunc = lambda value: colorScalarFunc(value) * 20
    hintFunc = lambda solarSystemID, value: (lambda : GetByLabel('UI/Map/StarModeHandler/industryCostModifier', index=value * 100.0), ())
    colorInfo.solarSystemDict.update(_GetColorDict(systemRows, intensityFunc, colorScalarFunc, hintFunc))
    colorInfo.colorList = (trinity.TriColor(0.5, 0.32, 0.0), trinity.TriColor(0.7, 0.0, 0.01))


def _GetColorDict(valueBySolarSystem, intensityFunc, colorScalarFunc, hintFunc):
    colorInfoBySolarSystemID = {}
    for solarSystemID, value in valueBySolarSystem.iteritems():
        colorInfoBySolarSystemID[solarSystemID] = (intensityFunc(value),
         colorScalarFunc(value),
         hintFunc(solarSystemID, value),
         None)

    return colorInfoBySolarSystemID