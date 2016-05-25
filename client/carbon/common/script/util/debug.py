# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\script\util\debug.py
import sys, pdb

def startDebugging():
    pdb.post_mortem(sys.exc_info()[2])


exports = {'debug.startDebugging': startDebugging}