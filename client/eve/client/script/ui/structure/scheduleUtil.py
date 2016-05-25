# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\scheduleUtil.py
from collections import Counter, defaultdict
import structures

def GetUniqueSchedules(schedulesInUse):
    schedulesAndNumUsed = Counter(schedulesInUse)
    schedulesBySetHours = defaultdict(list)
    for eachSchedule, numUsed in schedulesAndNumUsed.iteritems():
        s = structures.Schedule(eachSchedule)
        setHours = sum(s.value)
        s.SetRequiredHours(setHours)
        schedulesBySetHours[setHours].append((numUsed, s))

    return schedulesBySetHours