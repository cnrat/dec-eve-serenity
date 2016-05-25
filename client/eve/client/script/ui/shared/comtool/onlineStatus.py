# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\comtool\onlineStatus.py
import service
import util
import blue
import uthread

class OnlineStatus(service.Service):
    __guid__ = 'svc.onlineStatus'
    __displayname__ = 'Online Status Service'
    __exportedcalls__ = {'GetOnlineStatus': [],
     'Prime': []}
    __notifyevents__ = ['OnContactLoggedOn',
     'OnContactLoggedOff',
     'OnSessionChanged',
     'OnClientContactChange']

    def Run(self, memStream=None):
        self.semaphore = uthread.Semaphore()
        self.onlineStatus = None
        return

    def OnContactLoggedOn(self, charID):
        self.Prime()
        self.onlineStatus[charID] = blue.DBRow(self.onlineStatus.header, [charID, True])

    def OnContactLoggedOff(self, charID):
        self.Prime()
        self.onlineStatus[charID] = blue.DBRow(self.onlineStatus.header, [charID, False])

    def OnClientContactChange(self, charID, online):
        if online:
            self.OnContactLoggedOn(charID)
        else:
            self.OnContactLoggedOff(charID)

    def OnSessionChanged(self, isRemote, sess, change):
        if 'charid' in change and change['charid'][1]:
            self.Prime()

    def GetOnlineStatus(self, charID, fetch=True):
        if util.IsNPC(charID):
            return False
        else:
            if fetch:
                self.Prime()
            if charID not in (self.onlineStatus or {}):
                if fetch:
                    self.onlineStatus[charID] = blue.DBRow(self.onlineStatus.header, [charID, sm.RemoteSvc('onlineStatus').GetOnlineStatus(charID)])
                else:
                    raise IndexError('GetOnlineStatus', charID)
            if charID in self.onlineStatus:
                return self.onlineStatus[charID].online
            return None
            return None

    def ClearOnlineStatus(self, charID):
        if charID in self.onlineStatus:
            del self.onlineStatus[charID]
            sm.ScatterEvent('OnContactNoLongerContact', charID)

    def Prime(self):
        if self.onlineStatus is None:
            self.semaphore.acquire()
            try:
                if self.onlineStatus is None:
                    self.onlineStatus = sm.RemoteSvc('onlineStatus').GetInitialState().Index('contactID')
            finally:
                self.semaphore.release()

        return