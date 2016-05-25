# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\control\divider.py
import blue
import carbonui.const as uiconst
import uthread
from carbonui.primitives.container import Container

class Divider(Container):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self._dragging = False
        self._initCursor = None
        return

    def OnMouseDown(self, *args):
        self.OnChangeStart_(self)
        self._dragging = True
        self._initCursor = (uicore.uilib.x, uicore.uilib.y)
        uthread.new(self.BeginChange)

    def BeginChange(self, *args):
        while self._dragging:
            diffx = uicore.uilib.x - self._initCursor[0]
            diffy = uicore.uilib.y - self._initCursor[1]
            self.OnChange_(self, diffx, diffy)
            blue.pyos.synchro.SleepWallclock(1)

    def OnMouseUp(self, *args):
        self._dragging = False
        self.OnChanged_(self)

    def OnChangeStart_(self, *args):
        pass

    def OnChange_(self, *args, **kw):
        pass

    def OnChanged_(self, *args):
        pass