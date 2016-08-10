# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\whitelist.py
import exceptions
import blue
whitelist = '\n    blue.DBRowDescriptor\n    blue.DBRow\n\n    eveexceptions.SQLError\n    eveexceptions.UserError\n    eveexceptions.UnmarshalError\n    eveexceptions.ConnectionError\n    eveexceptions.ServiceNotFound\n\n    dbutil.CRowset\n    dbutil.CIndexedRowset\n    dbutil.CFilterRowset\n\n    carbon.common.script.sys.crowset.CRowset\n    carbon.common.script.sys.crowset.CIndexedRowset\n    carbon.common.script.sys.crowset.CFilterRowset\n\n    exceptions.AttributeError\n    exceptions.IndexError\n    exceptions.ValueError\n    exceptions.KeyError\n    exceptions.WindowsError\n    exceptions.ReferenceError\n    exceptions.RuntimeError\n    exceptions.IOError\n\n    exceptions.GPSException\n    exceptions.GPSTransportClosed\n    exceptions.GPSBadAddress\n    exceptions.GPSAddressOccupied\n\n    carbon.common.script.net.GPS.GPSException\n    carbon.common.script.net.GPS.GPSTransportClosed\n    carbon.common.script.net.GPS.GPSBadAddress\n    carbon.common.script.net.GPS.GPSAddressOccupied\n\n    exceptions.MachoException\n    exceptions.MachoWrappedException\n    exceptions.ProxyRedirect\n    exceptions.UberMachoException\n    exceptions.UnMachoDestination\n    exceptions.UnMachoChannel\n    exceptions.WrongMachoNode\n\n    carbon.common.script.net.machoNetExceptions.MachoException\n    carbon.common.script.net.machoNetExceptions.MachoWrappedException\n    carbon.common.script.net.machoNetExceptions.ProxyRedirect\n    carbon.common.script.net.machoNetExceptions.UberMachoException\n    carbon.common.script.net.machoNetExceptions.UnMachoDestination\n    carbon.common.script.net.machoNetExceptions.UnMachoChannel\n    carbon.common.script.net.machoNetExceptions.WrongMachoNode\n    carbon.common.script.net.crestExceptions.CrestSessionExists\n\n    xmlrpclib.Fault\n\n    macho.CallReq\n    macho.CallRsp\n    macho.ErrorResponse\n    macho.IdentificationReq\n    macho.IdentificationRsp\n    macho.MachoAddress\n    macho.Notification\n    macho.PingReq\n    macho.PingRsp\n    macho.SessionChangeNotification\n    macho.SessionInitialStateNotification\n    macho.TransportClosed\n    macho.MovementNotification\n\n    carbon.common.script.net.machoNetPacket.CallReq\n    carbon.common.script.net.machoNetPacket.CallRsp\n    carbon.common.script.net.machoNetPacket.ErrorResponse\n    carbon.common.script.net.machoNetPacket.IdentificationReq\n    carbon.common.script.net.machoNetPacket.IdentificationRsp\n    carbon.common.script.net.machoNetAddress.MachoAddress\n    carbon.common.script.net.machoNetPacket.Notification\n    carbon.common.script.net.machoNetPacket.PingReq\n    carbon.common.script.net.machoNetPacket.PingRsp\n    carbon.common.script.net.machoNetPacket.SessionChangeNotification\n    carbon.common.script.net.machoNetPacket.SessionInitialStateNotification\n    carbon.common.script.net.machoNetPacket.TransportClosed\n    carbon.common.script.net.machoNetPacket.MovementNotification\n\n\n    objectCaching.CachedMethodCallResult\n    objectCaching.CachedObject\n    objectCaching.CacheOK\n\n    carbon.common.script.net.objectCaching.CacheOK\n    carbon.common.script.net.objectCaching.CachedMethodCallResult\n    carbon.common.script.net.objectCaching.CachedObject\n\n    util.CachedObject\n    util.KeyVal\n    util.Moniker\n    util.PasswordString\n    util.Row\n    util.UpdateMoniker\n\n    carbon.common.script.net.cachedObject.CachedObject\n    eve.common.script.util.utillib_bootstrap.KeyVal\n    carbon.common.script.net.moniker.Moniker\n    carbon.common.script.net.moniker.Moniker\n    carbon.common.script.util.format.PasswordString\n    carbon.common.script.sys.row.Row\n    carbon.common.script.net.moniker.UpdateMoniker\n\n    __builtin__.str\n    __builtin__.unicode\n    __builtin__.set\n\n    collections.OrderedDict\n    collections.defaultdict\n    collections.deque\n\n    localizationUtil.LocalizationSafeString\n    carbon.common.script.localization.localizationUtil.LocalizationSafeString\n\n    paperDoll.SculptingRow\n    paperDoll.ModifierRow\n    paperDoll.ColorSelectionRow\n    paperDoll.AppearanceRow\n\n    eve.common.script.paperDoll.paperDollDefinitions.SculptingRow\n    eve.common.script.paperDoll.paperDollDefinitions.ModifierRow\n    eve.common.script.paperDoll.paperDollDefinitions.ColorSelectionRow\n    eve.common.script.paperDoll.paperDollDefinitions.AppearanceRow\n\n    machonethelpers.argchecker.ValidateArgTypeException\n'
whitelist += '\n        foo.SlimItem\n\n        eve.common.script.util.slimItem.SlimItem\n\n        eve.common.script.sys.eveCfg.Standings\n\n        eveinventory.voucher.Bookmark\n        eveinventory.voucher.PlayerKill\n        eveinventory.voucher.Share\n        eveinventory.voucher.Voucher\n\n        dbutil.RowList\n        dbutil.RowDict\n\n        eve.common.script.sys.rowset.RowDict\n        eve.common.script.sys.rowset.RowList\n\n        util.StackSize\n        util.Singleton\n        util.RamActivityVirtualColumn\n        util.PagedResultSet\n\n        eve.common.script.sys.rowset.Rowset\n        eve.common.script.sys.rowset.FilterRowset\n        eve.common.script.sys.rowset.IndexRowset\n        eve.common.script.sys.rowset.IndexedRows\n        eve.common.script.sys.rowset.SparseRowset\n        eve.common.script.sys.eveCfg.StackSize\n        eve.common.script.sys.eveCfg.Singleton\n        eve.common.script.sys.eveCfg.RamActivityVirtualColumn\n        eve.common.script.util.pagedCollection.PagedResultSet\n\n        dogma.exceptions.EmbarkOnlineError\n\n        warUtil.War\n        eve.common.script.util.warUtil.War\n        eve.common.script.universe.locationWrapper.SolarSystemWrapper\n\n        industry.job.Location\n        industry.const.Error\n        industry.const.Reference\n\n        crimewatch.corp_aggression.settings.AggressionSettings\n\n        shipskins.LicensedSkin\n\n        eve.common.script.dogma.effect.BrainEffect\n        dogma.attributes.attribute.Attribute\n        dogma.attributes.attribute.SkillLevelAttribute\n        dogma.attributes.attribute.ChargedAttribute\n        dogma.attributes.attribute.HeatAttribute\n        dogma.attributes.attribute.StackingNurfedAttribute\n        dogma.attributes.attribute.LiteralAttribute\n        dogma.attributes.attribute.BrainLiteralAttribute\n\n        projectdiscovery.common.exceptions.ClassificationTaskNotTheActiveTaskError\n        projectdiscovery.common.exceptions.NoActiveClassificationTaskError\n        projectdiscovery.common.exceptions.UnexpectedMmosResultError\n        projectdiscovery.common.exceptions.NoConnectionToAPIError\n        projectdiscovery.common.exceptions.MissingKeyError\n\n        marketutil.BestByOrder\n\n        seasons.common.challenge.Challenge\n        seasons.common.exceptions.ChallengeForCharacterNotFoundError\n        seasons.common.exceptions.NotEnoughChallengeTypesAvailableError\n        seasons.common.exceptions.ChallengeTypeNotFoundError\n'
if boot.role == 'server':
    whitelist += '\n        agent.StandardMissionDetails\n        agent.ResearchMissionDetails\n        agent.StorylineMissionDetails\n        agent.EpicArcMissionDetails\n        agent.OfferDetails\n        agent.LoyaltyPoints\n        agent.Agent\n        agent.Credits\n        agent.Item\n        agent.Entity\n        agent.Objective\n        agent.FetchObjective\n        agent.EncounterObjective\n        agent.DungeonObjective\n        agent.TransportObjective\n        agent.AgentObjective\n        agent.Reward\n        agent.TimeBonusReward\n        agent.MissionReferral\n        agent.Location\n        agent.ItemDeclarationError\n        agent.ItemResolutionFailure\n        agent.TransferItemFailure\n\n        eve.server.script.mgt.npc.agents.services.standardMissionDetails.StandardMissionDetails\n        eve.server.script.mgt.npc.agents.services.standardMissionDetails.ResearchMissionDetails\n        eve.server.script.mgt.npc.agents.services.standardMissionDetails.StorylineMissionDetails\n        eve.server.script.mgt.npc.agents.services.standardMissionDetails.EpicArcMissionDetails\n        eve.server.script.mgt.npc.agents.services.standardMissionDetails.OfferDetails\n        eve.server.script.mgt.npc.agents.items.LoyaltyPoints\n        eve.server.script.mgt.npc.agents.items.Agent\n        eve.server.script.mgt.npc.agents.items.Credits\n        eve.server.script.mgt.npc.agents.items.Item\n        eve.server.script.mgt.npc.agents.items.Entity\n        eve.server.script.mgt.npc.agents.items.Objective\n        eve.server.script.mgt.npc.agents.items.FetchObjective\n        eve.server.script.mgt.npc.agents.items.EncounterObjective\n        eve.server.script.mgt.npc.agents.items.DungeonObjective\n        eve.server.script.mgt.npc.agents.items.TransportObjective\n        eve.server.script.mgt.npc.agents.items.AgentObjective\n        eve.server.script.mgt.npc.agents.items.Reward\n        eve.server.script.mgt.npc.agents.items.TimeBonusReward\n        eve.server.script.mgt.npc.agents.items.MissionReferral\n        eve.server.script.mgt.npc.agents.items.Location\n        eve.server.script.mgt.npc.agents.exceptions.ItemDeclarationError\n        eve.server.script.mgt.npc.agents.exceptions.ItemResolutionFailure\n        eve.server.script.mgt.npc.agents.exceptions.TransferItemFailure\n\n        sys.A\n        sys.AgentString\n        sys.AgentUnicode\n\n        eve.common.script.sys.strangeStrings.A\n        eve.common.script.sys.strangeStrings.AgentString\n        eve.common.script.sys.strangeStrings.AgentUnicode\n\n        scriber.hermes.Notification\n        datetime.datetime\n    '

def InitWhitelist():
    wl = whitelist
    res = {}
    for item in wl.split():
        item.strip()
        if item:
            mod, obj = item.rsplit('.', 1)
            mod = __import__(mod, globals(), locals(), [obj], -1)
            obj = getattr(mod, obj)
            res[obj] = None

    for e in dir(exceptions):
        if e.endswith('Error'):
            e = getattr(exceptions, e)
            res[e] = None

    blue.marshal.globalsWhitelist = res
    blue.marshal.collectWhitelist = False
    return


exports = {'util.InitWhitelist': InitWhitelist}