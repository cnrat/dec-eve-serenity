# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\seasons\common\util.py


def are_seasons_enabled():
    try:
        enable_seasons = bool(int(sm.GetService('machoNet').GetGlobalConfig().get('enableSeasons', False)))
    except ValueError:
        enable_seasons = False

    return enable_seasons