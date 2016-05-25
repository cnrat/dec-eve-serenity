# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\chardet\charsetprober.py
from . import constants
import re

class CharSetProber:

    def __init__(self):
        pass

    def reset(self):
        self._mState = constants.eDetecting

    def get_charset_name(self):
        return None

    def feed(self, aBuf):
        pass

    def get_state(self):
        return self._mState

    def get_confidence(self):
        pass

    def filter_high_bit_only(self, aBuf):
        aBuf = re.sub('([\x00-\x7f])+', ' ', aBuf)
        return aBuf

    def filter_without_english_letters(self, aBuf):
        aBuf = re.sub('([A-Za-z])+', ' ', aBuf)
        return aBuf

    def filter_with_english_letters(self, aBuf):
        return aBuf