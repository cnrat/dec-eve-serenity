# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\fsd\diffMerge\sharedFunctions.py
PRIMITIVES = ['str',
 'unicode',
 'float',
 'int',
 'bool']

def IsPrimitive(item):
    return type(item).__name__ in PRIMITIVES


def ListIsSortedAscending(l):
    if len(l) > 0:
        last = l[0]
        for item in l:
            if item < last:
                return False

    return True


def ListIsSortedDescending(l):
    if len(l) > 0:
        last = l[0]
        for item in l:
            if item > last:
                return False

    return True


def ListsAreOrderedTheSameWay(a, b):
    if ListIsSortedAscending(a):
        return ListIsSortedAscending(b) and True
    elif ListIsSortedDescending(a) and ListIsSortedDescending(b):
        return True
    else:
        return False


def ListIsLikelyToBeVector(l):
    if len(l) < 5:
        for item in l:
            if type(item) is float:
                return True

        if not ListIsSortedDescending(l) and not ListIsSortedAscending(l):
            return True
    return False