# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\marketutil\__init__.py
import collections
from skilllimits import GetSkillLimits
BestByOrder = collections.namedtuple('BestByOrder', ['price',
 'volRemaining',
 'typeID',
 'stationID'])

def ConvertTuplesToBestByOrders(bestOrdersByType):
    return {typeID:BestByOrder(*order) for typeID, order in bestOrdersByType.iteritems()}