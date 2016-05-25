# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\util\guidUtils.py
import zlib
import uuid

def MakeGUID():
    return uuid.uuid4().int


def MakePUID():
    uuidstr = uuid.uuid4().hex
    return zlib.crc32(uuidstr)


exports = {'util.MakeGUID': MakeGUID,
 'util.MakePUID': MakePUID}