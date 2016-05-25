# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\audio.py
import world
if world.WORLD_SPACE_SCHEMA == 'zworld':
    AUDIO_SCHEMA = world.WORLD_SPACE_SCHEMA
    _AUDIO_PREFIX = AUDIO_SCHEMA + '.'
    AUDIO_SPAWN_POINTS_TABLE_NAME = 'staticAudioLocations'
    AUDIO_SPAWN_POINTS_MAIN_TABLE = _AUDIO_PREFIX + AUDIO_SPAWN_POINTS_TABLE_NAME
else:
    AUDIO_SCHEMA = 'audio'
    _AUDIO_PREFIX = AUDIO_SCHEMA + '.'
    AUDIO_SPAWN_POINTS_TABLE_NAME = 'staticSpawnPoints'
    AUDIO_SPAWN_POINTS_MAIN_TABLE = _AUDIO_PREFIX + AUDIO_SPAWN_POINTS_TABLE_NAME
TRINITY_DRAG_WORLD_SPACE_AUDIO = 'WorldSpaceAudio'
TRINITY_DRAG_WORLD_SPACE_NEW_AUDIO = 'WorldSpaceNewAudio'
AUDIO_SCHEMA = 'audio'
_AUDIO_PREFIX = AUDIO_SCHEMA + '.'
AUDIO_SPAWN_POINTS_TABLE_NAME = 'staticSpawnPoints'
AUDIO_SPAWN_POINTS_MAIN_TABLE = _AUDIO_PREFIX + AUDIO_SPAWN_POINTS_TABLE_NAME
SELECT_AUDIO_EVENT = 'SelectAudioEvent'