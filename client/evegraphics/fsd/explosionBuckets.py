# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\evegraphics\fsd\explosionBuckets.py
import itertools
import random
import evetypes
from evegraphics.fsd.base import BuiltDataLoader
from evegraphics.fsd.graphicIDs import GetExplosionBucketID
import logging
log = logging.getLogger(__file__)

class ExplosionBucketsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/explosionBuckets.static'
    __autobuildBuiltFile__ = 'eve/autobuild/staticdata/client/explosionBuckets.static'


def GetExplosionBuckets():
    return ExplosionBucketsLoader.GetData()


def GetExplosionBucketByTypeID(typeID):
    explosionBucketIdByGraphicID = GetExplosionBucketID(evetypes.GetGraphicID(typeID))
    explosionBucketIdByGroup = evetypes.GetExplosionBucketIDByGroup(evetypes.GetGroupID(typeID))
    return GetExplosionBucket(explosionBucketIdByGraphicID or explosionBucketIdByGroup)


def GetExplosionBucket(explosionBucketID):
    return GetExplosionBuckets().get(explosionBucketID, None)


def GetExplosionAttribute(explosionBucketID, attributeName, default=None):
    if isinstance(explosionBucketID, (int, long)):
        return getattr(GetExplosionBucket(explosionBucketID), attributeName, default)
    return getattr(explosionBucketID, attributeName, default)


def GetRandomExplosion(explosionBucketID, raceName=None, preferredIndex=-1):
    explosions = GetExplosionAttribute(explosionBucketID, 'explosions', None)
    if explosions is None:
        log.error("ExplosionBucket '%s' has no explosions" % explosionBucketID)
        return
    else:
        listOfExplosionsToPick = explosions.get(raceName, explosions.get('default', None))
        if listOfExplosionsToPick is None:
            listOfExplosionsToPick = list(itertools.chain(*[ explosionList for race, explosionList in explosions.iteritems() ]))
        if -1 < preferredIndex < len(listOfExplosionsToPick):
            return listOfExplosionsToPick[preferredIndex]
        if preferredIndex != -1:
            log.warning('ExplosionBucket.GetRandomExplosion(%s, raceName=%s, preferredIndex=%s) Got invalid preferredIndex, returning random explosion' % (explosionBucketID, raceName, preferredIndex))
        return random.choice(listOfExplosionsToPick)