# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\comtool\focus.py
import service
import carbonui.const as uiconst
import weakref

class Focus(service.Service):
    __guid__ = 'svc.focus'
    __servicename__ = 'focus'
    __displayname__ = 'Focus Tool'
    __dependencies__ = []

    def Run(self, memStream=None):
        self.focusChannelWindow = None
        return

    def SetChannelFocus(self, char=None):
        channel = self.GetFocusChannel()
        if channel is not None:
            channel.Maximize()
            stack = getattr(channel.sr, 'stack', None)
            if stack and stack.state == uiconst.UI_HIDDEN:
                return
            channel.SetCharFocus(char)
        return

    def SetFocusChannel(self, channel=None):
        if channel is not None:
            self.focusChannelWindow = weakref.ref(channel)
        else:
            self.focusChannelWindow = None
        return

    def GetFocusChannel(self):
        if self.focusChannelWindow:
            ch = self.focusChannelWindow()
            if ch and not ch.destroyed:
                return ch
        return None