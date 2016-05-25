# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\carbon\common\lib\session.py
SESSION_TYPE_INVALID = 0
SESSION_TYPE_EXECUTIONCONTEXT = 1
SESSION_TYPE_SERVICE = 2
SESSION_TYPE_CREST = 3
SESSION_TYPE_ESP = 4
SESSION_TYPE_GAME = 5
VALID_SESSION_TYPES = (SESSION_TYPE_EXECUTIONCONTEXT,
 SESSION_TYPE_SERVICE,
 SESSION_TYPE_CREST,
 SESSION_TYPE_ESP,
 SESSION_TYPE_GAME)
SESSION_TYPE_TO_NAME = {SESSION_TYPE_INVALID: 'Invalid',
 SESSION_TYPE_GAME: 'Game',
 SESSION_TYPE_CREST: 'Crest',
 SESSION_TYPE_ESP: 'ESP',
 SESSION_TYPE_EXECUTIONCONTEXT: 'Context',
 SESSION_TYPE_SERVICE: 'Service'}
SESSION_NAME_TO_TYPE = {'Invalid': SESSION_TYPE_INVALID,
 'Game': SESSION_TYPE_GAME,
 'Crest': SESSION_TYPE_CREST,
 'ESP': SESSION_TYPE_ESP,
 'Context': SESSION_TYPE_EXECUTIONCONTEXT,
 'Service': SESSION_TYPE_SERVICE}
GAME_SESSION_CLIENT_IDENTIFIERS = {'dust', 'eveclient', 'internal'}