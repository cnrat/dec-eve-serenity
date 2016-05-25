# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\graphs\graphsutil.py
import math

def MovingOp(values, op, n):
    returnValues = []
    for i in xrange(len(values)):
        start = max(i - n, 0)
        end = i + 1
        v = op(values[start:end])
        returnValues.append(v)

    return returnValues


def MovingHigh(values, n=5):
    return MovingOp(values, max, n)


def MovingLow(values, n=5):
    return MovingOp(values, min, n)


def MovingAvg(values, n=5):
    return MovingOp(values, lambda l: sum(l) / len(l), n)


def AdjustMaxValue(height, maxValue, minGridLineHeight):
    magnitude = math.trunc(math.log10(maxValue))
    magnitudeValue = pow(10, magnitude)
    dividerValues = [25.0,
     10.0,
     5.0,
     4.0,
     2.0,
     1.0]
    for divider in dividerValues:
        adjustedMaxValue = math.floor(maxValue / magnitudeValue) * magnitudeValue
        numGridLines = int(math.floor(maxValue / magnitudeValue) * divider)
        while adjustedMaxValue < maxValue:
            adjustedMaxValue += magnitudeValue / divider
            numGridLines += 1

        gridLineHeight = int(height / numGridLines)
        if gridLineHeight > minGridLineHeight:
            break

    return (adjustedMaxValue, numGridLines)