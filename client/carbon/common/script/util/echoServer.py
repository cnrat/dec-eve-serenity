# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\util\echoServer.py
import service

class EchoServer(service.Service):
    __guid__ = 'svc.echo'
    __exportedcalls__ = {'Echo': [service.ROLEMASK_ELEVATEDPLAYER]}

    def Echo(self, arg):
        return arg