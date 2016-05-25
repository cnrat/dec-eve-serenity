# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\iocp.py
import blue
settingsCache = {}

def CheckForSetting(settingName):
    result = settingsCache.get(settingName, None)
    if result is None:
        result = '/' + settingName in blue.pyos.GetArg() or prefs.GetValue(settingName, 0) == 1 or boot.GetValue(settingName, 0) == 1
        settingsCache[settingName] = result
    return result


def UsingIOCP():
    result = settingsCache.get('iocp', None)
    if result is None:
        result = '/iocp' in blue.pyos.GetArg()
        if not result:
            result = prefs.GetValue('socketIO', None)
            if result is not None:
                result = result.lower() == 'iocp'
            else:
                result = boot.GetValue('socketIO', 'stacklessio').lower() == 'iocp'
        settingsCache['iocp'] = result
    return result


def UsingCompression():
    return UsingIOCP() and CheckForSetting('iocpCompress')


def UsingHTTPS():
    return UsingIOCP() and UsingSSL() and CheckForSetting('https')


def UsingSSL():
    return UsingIOCP() and CheckForSetting('ssl')


def LoggingCarbonIO():
    return UsingIOCP() and CheckForSetting('logCarbonIO')