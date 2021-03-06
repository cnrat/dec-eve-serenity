# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\sensorsuite\overlay\sitetype.py
ANOMALY = 1
SIGNATURE = 2
STATIC_SITE = 3
BOOKMARK = 4
CORP_BOOKMARK = 5
MISSION = 6
STRUCTURE = 7
PERSONAL_SITE_TYPES = (BOOKMARK, CORP_BOOKMARK, MISSION)
ALL_SITE_TYPES = {ANOMALY,
 SIGNATURE,
 STATIC_SITE,
 BOOKMARK,
 CORP_BOOKMARK,
 MISSION,
 STRUCTURE}
STRUCTURE_SITE_TYPES = {STRUCTURE}
NON_STRUCTURE_SITE_TYPES = ALL_SITE_TYPES - STRUCTURE_SITE_TYPES

def IsSiteInstantlyAccessible(siteData):
    return siteData.siteType in PERSONAL_SITE_TYPES