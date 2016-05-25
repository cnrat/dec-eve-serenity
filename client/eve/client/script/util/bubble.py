# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\util\bubble.py


def SlimItemFromCharID(charID):
    bp = sm.GetService('michelle').GetBallpark()
    if bp:
        for item in bp.slimItems.values():
            if item.charID == charID:
                return item

    return None


def InBubble(itemID):
    bp = sm.GetService('michelle').GetBallpark()
    if bp:
        return itemID in bp.balls
    else:
        return False


import carbon.common.script.util.autoexport as autoexport
exports = autoexport.AutoExports('util', globals())