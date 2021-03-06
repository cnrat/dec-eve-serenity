# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\codereload\win32api\pump.py
import ctypes
from ctypes.wintypes import DWORD, HWND, LPARAM, POINT, UINT, WPARAM
PM_REMOVE = 1
WM_QUIT = 18

class MSG(ctypes.Structure):
    _fields_ = [('hwnd', HWND),
     ('message', UINT),
     ('wParam', WPARAM),
     ('lParam', LPARAM),
     ('time', DWORD),
     ('pt', POINT)]


def PumpWindowsMessages():
    msg = MSG()
    while ctypes.windll.user32.PeekMessageW(ctypes.byref(msg), HWND(), 0, 0, PM_REMOVE):
        if msg.message == WM_QUIT:
            return False
        ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
        ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

    return True