# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\control\eveFrame.py
from carbonui.primitives.frame import Frame as FrameCore

class Frame(FrameCore):
    __guid__ = 'uicontrols.Frame'
    default_color = (1.0, 1.0, 1.0, 0.5)


from carbonui.primitives.frame import FrameCoreOverride
FrameCoreOverride.__bases__ = (Frame,)