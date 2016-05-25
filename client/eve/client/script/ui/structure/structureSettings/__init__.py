# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\structure\structureSettings\__init__.py
from eve.client.script.ui.util.linkUtil import GetValueFromTextLink
import structures

def AreGroupNodes(dragData):
    if not dragData:
        return False
    firstNode = dragData[0]
    if firstNode.get('nodeType', None) == 'AccessGroupEntry':
        return True
    elif firstNode.Get('__guid__', None) != 'TextLink':
        return False
    url = firstNode.Get('url', '')
    if url.startswith('accessGroup:'):
        return True
    else:
        return False


def GetGroupIDFromNode(node):
    if not AreGroupNodes([node]):
        return
    elif node.get('nodeType', None) == 'AccessGroupEntry':
        return node.groupID
    elif node.Get('__guid__', None) == 'TextLink':
        return GetValueFromTextLink(node, linkType='accessGroup:')
    else:
        return


def CanHaveGroups(settingID):
    return settingID in structures.SETTINGS_VALUE_HAS_GROUPS