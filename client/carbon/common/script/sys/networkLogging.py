# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\sys\networkLogging.py
import service
import blue

class NetworkLogging(service.Service):
    __guid__ = 'svc.networkLogging'
    __displayname__ = 'Network Logging'
    __exportedcalls__ = {'StartNetworkLogging': [service.ROLE_SERVICE],
     'StopNetworkLogging': [service.ROLE_SERVICE],
     'GetLoggingState': [service.ROLE_SERVICE]}

    def StartNetworkLogging(self, server, port, threshold):
        if server and port:
            return blue.EnableNetworkLogging(server, int(port), boot.role, int(threshold))

    def StopNetworkLogging(self):
        return blue.DisableNetworkLogging()

    def GetLoggingState(self):
        return blue.GetNetworkLoggingState()