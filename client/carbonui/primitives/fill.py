# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\carbonui\primitives\fill.py
from .sprite import Sprite
import carbonui.const as uiconst
import trinity

class Fill(Sprite):
    __guid__ = 'uiprimitives.Fill'
    default_name = 'fill'
    default_color = (1.0, 1.0, 1.0, 0.25)
    default_align = uiconst.TOALL
    default_state = uiconst.UI_DISABLED
    default_left = 0
    default_top = 0
    default_width = 0
    default_height = 0
    default_filter = False
    default_spriteEffect = trinity.TR2_SFX_FILL