# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\requests\packages\chardet\__init__.py
__version__ = '2.2.1'
from sys import version_info

def detect(aBuf):
    if version_info < (3, 0) and isinstance(aBuf, unicode) or version_info >= (3, 0) and not isinstance(aBuf, bytes):
        raise ValueError('Expected a bytes object, not a unicode object')
    from . import universaldetector
    u = universaldetector.UniversalDetector()
    u.reset()
    u.feed(aBuf)
    u.close()
    return u.result