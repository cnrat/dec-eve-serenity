# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\crestclient\errors\forbiddenException.py
from baseException import CrestClientBaseException

class ForbiddenException(CrestClientBaseException):

    def __init__(self, message):
        super(ForbiddenException, self).__init__(message, 403)