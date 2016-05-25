# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\cherrypy\test\__init__.py
import sys

def newexit():
    raise SystemExit('Exit called')


def setup():
    newexit._old = sys.exit
    sys.exit = newexit


def teardown():
    try:
        sys.exit = sys.exit._old
    except AttributeError:
        sys.exit = sys._exit