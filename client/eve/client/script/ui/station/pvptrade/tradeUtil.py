# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\station\pvptrade\tradeUtil.py
from eve.client.script.ui.services.menuSvcExtras.invItemFunctions import DeliverToStructure
from eve.common.script.sys.eveCfg import IsEvePlayerCharacter

def TryInitiateTrade(charID, nodes):
    if charID == session.charid:
        return
    if not IsEvePlayerCharacter(charID):
        return
    if session.stationid:
        return TryInitiateStationTrade(charID, nodes)
    if session.structureid:
        return TryInitiateStructureDelivery(charID, nodes)


def TryInitiateStationTrade(charID, nodes):
    if session.stationid and sm.StartService('station').IsGuest(charID):
        sm.StartService('pvptrade').StartTradeSession(charID, tradeItems=nodes)


def TryInitiateStructureDelivery(charID, nodes):
    if session.structureid:
        invItems = filter(None, [ getattr(n, 'item', None) for n in nodes ])
        DeliverToStructure(invItems, charID)
    return