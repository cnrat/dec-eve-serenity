# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\inflight\actions.py
import carbonui.const as uiconst
import uiprimitives
from eve.client.script.ui.control.eveWindow import Window
import uicontrols

class ActionPanel(Window):
    __guid__ = 'form.ActionPanel'
    default_width = 256
    default_height = 160

    def ApplyAttributes(self, attributes):
        uicontrols.Window.ApplyAttributes(self, attributes)
        showActions = attributes.get('showActions', True)
        panelName = attributes.panelName
        self.lastActionSerial = None
        self.sr.actions = None
        self.sr.actionsTimer = None
        self.sr.blink = None
        self.panelname = ''
        self.scope = 'inflight'
        self.panelname = panelName
        main = self.sr.main
        self.SetTopparentHeight(0)
        self.SetWndIcon()
        if panelName:
            self.SetCaption(panelName)
        self.MakeUnKillable()
        main.padding = const.defaultPadding
        main.clipChildren = 1
        if showActions:
            self.sr.actions = uiprimitives.Container(name='actions', align=uiconst.TOBOTTOM, parent=self.sr.main, height=32)
        self.PostStartup()
        self.UpdateAll()
        return

    def Blink(self, on_off=1):
        if on_off and self.sr.blink is None:
            self.sr.blink = uiprimitives.Fill(parent=self.sr.topParent, padding=(1, 1, 1, 1), color=(1.0, 1.0, 1.0, 0.25))
        if on_off:
            sm.GetService('ui').BlinkSpriteA(self.sr.blink, 0.25, 500, None, passColor=0)
        elif self.sr.blink:
            sm.GetService('ui').StopBlink(self.sr.blink)
            b = self.sr.blink
            self.sr.blink = None
            b.Close()
        return

    def _OnClose(self, *args):
        self.sr.actionsTimer = None
        self.Closing()
        return

    def PostStartup(self):
        pass

    def Closing(self):
        pass

    def GetActions(self):
        return []

    def UpdateAll(self):
        if self.sr.main.state != uiconst.UI_PICKCHILDREN:
            self.sr.actionsTimer = None
            return
        else:
            return