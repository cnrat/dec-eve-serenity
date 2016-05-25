# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\market\__init__.py
from eve.client.script.ui.util.linkUtil import GetTypeIDFromTextLink

def GetTypeIDFromDragItem(node):
    try:
        typeID = node.typeID
        if typeID:
            return typeID
    except AttributeError:
        pass

    nodeGuid = getattr(node, '__guid__', None)
    if nodeGuid in INVENTORY_GUIDS:
        return node.item.typeID
    else:
        typeID = GetTypeIDFromTextLink(node)
        return typeID


INVENTORY_GUIDS = ('xtriui.InvItem', 'listentry.InvItem')