# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\dogma\exceptions\__init__.py
__author__ = 'unnar'
from eveexceptions import UserError

class ItemExpiredError(Exception):
    pass


class EmbarkOnlineError(UserError):
    propagate = True


class EffectFailedButShouldBeStopped(Exception):
    pass