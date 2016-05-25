# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\crestclient\errors\serviceUnavailableException.py
from baseException import CrestClientBaseException

class ServiceUnavailableException(CrestClientBaseException):

    def __init__(self, message):
        super(ServiceUnavailableException, self).__init__(message, 503)