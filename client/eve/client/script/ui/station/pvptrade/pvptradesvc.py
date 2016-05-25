# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\pvptrade\pvptradesvc.py
import service
import form
import uicontrols
import uicls

class PVPTradeService(service.Service):
    __guid__ = 'svc.pvptrade'
    __exportedcalls__ = {'StartTradeSession': []}
    __notifyevents__ = ['OnTrade']

    def StartTradeSession(self, charID, tradeItems=None):
        tradeSession = sm.RemoteSvc('trademgr').InitiateTrade(charID)
        windowID = self.GetWindowIDForTradeSession(tradeSession)
        checkWnd = uicontrols.Window.GetIfOpen(windowID=windowID)
        if checkWnd and not checkWnd.destroyed:
            checkWnd.Maximize()
        else:
            self.OnInitiate(charID, tradeSession, tradeItems)

    def GetWindowIDForTradeSession(self, tradeSession):
        tradeContainerID = tradeSession.List().tradeContainerID
        return self.GetWindowID(tradeContainerID)

    def GetWindowID(self, tradeContainerID=None):
        windowID = ('tradeWnd', tradeContainerID)
        return windowID

    def OnTrade(self, what, *args):
        self.LogInfo('OnTrade', what, args)
        getattr(self, 'On' + what)(*args)

    def OnInitiate(self, charID, tradeSession, tradeItems=None):
        self.LogInfo('OnInitiate', charID, tradeSession)
        windowID = self.GetWindowIDForTradeSession(tradeSession)
        checkWnd = uicontrols.Window.GetIfOpen(windowID=windowID)
        if checkWnd:
            return
        form.PVPTrade.Open(windowID=windowID, tradeSession=tradeSession, tradeItems=tradeItems)

    def OnCancel(self, containerID):
        windowID = self.GetWindowID(containerID)
        w = uicontrols.Window.GetIfOpen(windowID=windowID)
        if w:
            w.OnCancel()

    def OnStateToggle(self, containerID, state):
        windowID = self.GetWindowID(containerID)
        w = uicontrols.Window.GetIfOpen(windowID=windowID)
        if w:
            w.OnStateToggle(state)

    def OnMoneyOffer(self, containerID, money):
        windowID = self.GetWindowID(containerID)
        w = uicontrols.Window.GetIfOpen(windowID=windowID)
        if w:
            w.OnMoneyOffer(money)

    def OnTradeComplete(self, containerID):
        windowID = self.GetWindowID(containerID)
        w = uicontrols.Window.GetIfOpen(windowID=windowID)
        if w:
            w.OnTradeComplete()