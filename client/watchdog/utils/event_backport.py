# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\watchdog\utils\event_backport.py
from threading import Condition, Lock

class Event(object):

    def __init__(self):
        self.__cond = Condition(Lock())
        self.__flag = False

    def isSet(self):
        return self.__flag

    is_set = isSet

    def set(self):
        self.__cond.acquire()
        try:
            self.__flag = True
            self.__cond.notify_all()
        finally:
            self.__cond.release()

    def clear(self):
        self.__cond.acquire()
        try:
            self.__flag = False
        finally:
            self.__cond.release()

    def wait(self, timeout=None):
        self.__cond.acquire()
        try:
            if not self.__flag:
                self.__cond.wait(timeout)
            return self.__flag
        finally:
            self.__cond.release()