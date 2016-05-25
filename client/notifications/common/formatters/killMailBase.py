# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\notifications\common\formatters\killMailBase.py
from notifications.common.formatters.attributeConstants import KILL_MAIL_ID, KILL_MAIL_ID_HASH
from notifications.common.formatters.baseFormatter import BaseNotificationFormatter

class KillMailBaseFormatter(BaseNotificationFormatter):

    def __init__(self):
        pass

    @staticmethod
    def MakeData(killMailID, killMailHash):
        return {KILL_MAIL_ID: killMailID,
         KILL_MAIL_ID_HASH: killMailHash}

    @staticmethod
    def GetKillMailIDandHash(data):
        return (data[KILL_MAIL_ID], data[KILL_MAIL_ID_HASH])