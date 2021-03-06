# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveaudio\__init__.py
import evetypes
try:
    const
except NameError:
    import devenv.libconst as const

import logging
logger = logging.getLogger(__name__)
SHIPS_DESTROYED_TO_CHANGE_MUSIC = 10
PILOTS_IN_SPACE_TO_CHANGE_MUSIC = 100
WORMHOLE_SYSTEM_ID_STARTS = 31000000
SENTINEL_SOLARSYSTEM_ID = 31000001
BARBICAN_SOLARSYSTEM_ID = 31000002
VIDETTE_SOLARSYSTEM_ID = 31000003
CONFLUX_SOLARSYSTEM_ID = 31000004
THERA_SOLARSYSTEM_ID = 31000005
REDOUBT_SOLARSYSTEM_ID = 31000006
HANGAR_STATE_GALLENTE = 'set_hangar_rtpc_gallente'
HANGAR_STATE_THERA = 'set_hangar_rtpc_thera'
SPECIAL_HANGAR_STATES_SWITCHES = {THERA_SOLARSYSTEM_ID: HANGAR_STATE_THERA}
MUSIC_STATE_NULLSEC_SPECIAL_SYSTEMS = [SENTINEL_SOLARSYSTEM_ID,
 BARBICAN_SOLARSYSTEM_ID,
 VIDETTE_SOLARSYSTEM_ID,
 CONFLUX_SOLARSYSTEM_ID,
 REDOUBT_SOLARSYSTEM_ID]
THERA_SYSTEM_ENTRY_EVENT = 'thera_system_entry_play'
SPECIAL_SYSTEM_ENTRY_EVENT = 'special_system_entry_play'
SPECIAL_SYSTEM_ENTRY_SOUND = {THERA_SOLARSYSTEM_ID: THERA_SYSTEM_ENTRY_EVENT,
 SENTINEL_SOLARSYSTEM_ID: SPECIAL_SYSTEM_ENTRY_EVENT,
 BARBICAN_SOLARSYSTEM_ID: SPECIAL_SYSTEM_ENTRY_EVENT,
 VIDETTE_SOLARSYSTEM_ID: SPECIAL_SYSTEM_ENTRY_EVENT,
 CONFLUX_SOLARSYSTEM_ID: SPECIAL_SYSTEM_ENTRY_EVENT,
 REDOUBT_SOLARSYSTEM_ID: SPECIAL_SYSTEM_ENTRY_EVENT}
MUSIC_LOCATION_SPACE = 'music_eve_dynamic'
MUSIC_LOCATION_LOGIN = 'music_login'
MUSIC_LOCATION_CHARACTER_CREATION = 'music_character_creation'
MUSIC_STATE_EMPIRE = 'music_switch_empire'
MUSIC_STATE_EMPIRE_POPULATED = 'music_switch_famous'
MUSIC_STATE_LOWSEC = 'music_switch_danger'
MUSIC_STATE_NULLSEC = 'music_switch_zero'
MUSIC_STATE_NULLSEC_DEATHS = 'music_switch_zero_danger'
MUSIC_STATE_NULLSEC_WORMHOLE = 'music_switch_zero_wormhole'
MUSIC_STATE_NULLSEC_SPECIAL = 'music_switch_zero_special'
MUSIC_STATE_OLD_JUKEBOX = 'music_switch_old_jukebox'
MUSIC_LOCATION_DUNGEON = 'music_switch_dungeon'
MUSIC_STATE_RACE_AMARR = 'music_switch_race_amarr'
MUSIC_STATE_RACE_CALDARI = 'music_switch_race_caldari'
MUSIC_STATE_RACE_GALLENTE = 'music_switch_race_gallente'
MUSIC_STATE_RACE_MINMATAR = 'music_switch_race_minmatar'
MUSIC_STATE_RACE_NORACE = 'music_switch_race_norace'
MUSIC_STATE_FULL = 'music_switch_full'
MUSIC_STATE_AMBIENT = 'music_switch_ambient'
MUSIC_STATE_DUNGEON_LEVEL_1 = 'music_switch_dungeon_level_01'
MUSIC_STATE_DUNGEON_LEVEL_2 = 'music_switch_dungeon_level_02'
MUSIC_STATE_DUNGEON_LEVEL_3 = 'music_switch_dungeon_level_03'
MUSIC_STATE_DUNGEON_LEVEL_4 = 'music_switch_dungeon_level_04'
HANGAR_STATE_POPULATION_FEW = 'hangar_population_state_few'
HANGAR_STATE_POPULATION_SOME = 'hangar_population_state_some'
HANGAR_STATE_POPULATION_MANY = 'hangar_population_state_many'
RACIALMUSICDICT = {const.raceCaldari: MUSIC_STATE_RACE_CALDARI,
 const.raceMinmatar: MUSIC_STATE_RACE_MINMATAR,
 const.raceAmarr: MUSIC_STATE_RACE_AMARR,
 const.raceGallente: MUSIC_STATE_RACE_GALLENTE,
 None: MUSIC_STATE_RACE_NORACE}

def GetSoundUrlForType(slimItem):
    soundUrl = sm.GetService('incursion').GetSoundUrlByKey(slimItem.groupID)
    if soundUrl is None:
        soundID = evetypes.GetSoundID(slimItem.typeID)
        if soundID is not None:
            soundUrl = cfg.sounds.Get(soundID).soundFile
    return soundUrl


def GetPilotsInSystem():
    channelID = (('solarsystemid2', session.solarsystemid2),)
    result = None
    try:
        result = sm.GetService('LSC').GetMemberCount(channelID)
    except Exception:
        logger.exception('Error ignored, returning None')

    return result


def GetHangarPopulationSwitch(pilotsInChannel):
    if pilotsInChannel < 20:
        return HANGAR_STATE_POPULATION_FEW
    if pilotsInChannel < 80:
        return HANGAR_STATE_POPULATION_SOME
    return HANGAR_STATE_POPULATION_MANY


def PlayFootfallForEntity(entity):
    import materialTypes
    namesByID = {}
    for name, ID in materialTypes.MATERIAL_NAMES.iteritems():
        namesByID[ID] = name

    if not entity:
        return
    positionComponent = entity.GetComponent('position')
    audioEmitterComponent = entity.GetComponent('audioEmitter')
    if not positionComponent or not audioEmitterComponent:
        return
    gameWorld = sm.GetService('gameWorldClient').GetGameWorld(session.worldspaceid)
    if not gameWorld:
        return
    topPosition = (positionComponent.position[0], positionComponent.position[1] + 0.1, positionComponent.position[2])
    bottomPosition = (positionComponent.position[0], positionComponent.position[1] - 0.2, positionComponent.position[2])
    hitResult = gameWorld.MultiHitLineTestWithMaterials(topPosition, bottomPosition)
    if hitResult:
        audioEmitterComponent.emitter.SetSwitch(u'Materials', namesByID[hitResult[0][2]])
        audioEmitterComponent.emitter.SendEvent(u'footfall_loud_play')
    else:
        audioEmitterComponent.emitter.SetSwitch(u'Materials', u'Invalid')
        audioEmitterComponent.emitter.SendEvent(u'footfall_loud_play')


def SetTheraSystemHangarSwitch(solarsystemid2, eventPlayer):
    event = SPECIAL_HANGAR_STATES_SWITCHES.get(solarsystemid2, HANGAR_STATE_GALLENTE)
    if eventPlayer:
        eventPlayer.SendEvent(event)


def PlaySystemSpecificEntrySound(lastSystemID, currentSystemID, eventPlayer):
    if lastSystemID != currentSystemID:
        event = SPECIAL_SYSTEM_ENTRY_SOUND.get(currentSystemID)
        if event and eventPlayer:
            eventPlayer.SendEvent(event)
    return currentSystemID


LANGUAGE_ID_TO_BANK = {'DE': u'German/',
 'RU': u'Russian/',
 'JA': u'Japanese/',
 'ZH': u'Chinese(PRC)/',
 'FR': u'French(France)/'}
EVE_COMMON_BANKS = (u'Init.bnk', u'Interface.bnk', u'Music.bnk', u'Voice.bnk', u'Planets.bnk', u'ShipEffects.bnk', u'Common.bnk')
EVE_INCARNA_BANKS = (u'CharacterCreation.bnk', u'Incarna.bnk', u'Hangar.bnk')
EVE_SPACE_BANKS = (u'Effects.bnk', u'Modules.bnk', u'Turrets.bnk', u'Atmos.bnk', u'Boosters.bnk', u'Placeables.bnk', u'Dungeons.bnk')