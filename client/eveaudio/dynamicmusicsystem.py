# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\eveaudio\dynamicmusicsystem.py
import eveaudio
import eve.common.lib.appConst as const

class DynamicMusicSystem(object):

    def __init__(self, sendEvent):
        self.sendEvent = sendEvent
        self.loginMusicPaused = False
        self.musicPlaying = False
        self._musicEnabled = True
        self.musicLocation = None
        self.lastLocationPlayed = None
        self.oldJukeboxOverride = False
        return

    def UpdateDynamicMusic(self, uicore, solarsystemid2, securityStatus):
        if not self._musicEnabled:
            return
        else:
            self.musicLocation = GetMusicLocation(uicore, solarsystemid2)
            if self.musicLocation is eveaudio.MUSIC_LOCATION_CHARACTER_CREATION:
                self.SetCharacterCreationMusicState(uicore)
            elif self.musicLocation is eveaudio.MUSIC_LOCATION_SPACE:
                self.SetSpaceMusicState(solarsystemid2, securityStatus)
            if self.musicLocation is None or self.lastLocationPlayed == self.musicLocation:
                return
            self.PlayLocationMusic(self.musicLocation)
            return

    def PlayLocationMusic(self, location):
        if location is self.lastLocationPlayed and self.musicPlaying:
            return
        else:
            if self.lastLocationPlayed is not None:
                self.StopLocationMusic(self.lastLocationPlayed)
            if location == eveaudio.MUSIC_LOCATION_LOGIN and self.loginMusicPaused:
                self.ResumeLocationMusic(location)
                return
            if not self.musicPlaying:
                self.musicPlaying = True
                self.lastLocationPlayed = location
                self.sendEvent(location + '_play')
            if location == eveaudio.MUSIC_LOCATION_SPACE and self.loginMusicPaused:
                self.sendEvent(eveaudio.MUSIC_LOCATION_LOGIN + '_stop')
                self.loginMusicPaused = False
            return

    def StopLocationMusic(self, location):
        if location == eveaudio.MUSIC_LOCATION_LOGIN and self.musicLocation != eveaudio.MUSIC_LOCATION_SPACE:
            self.PauseLocationMusic(location)
            return
        else:
            self.sendEvent(location + '_stop')
            self.lastLocationPlayed = None
            self.musicPlaying = False
            return

    def PauseLocationMusic(self, location):
        self.sendEvent(location + '_pause')
        self.musicPlaying = False
        self.lastLocationPlayed = None
        if location == eveaudio.MUSIC_LOCATION_LOGIN:
            self.loginMusicPaused = True
        return

    def ResumeLocationMusic(self, location):
        self.sendEvent(location + '_resume')
        self.musicPlaying = True
        self.lastLocationPlayed = location
        if location == eveaudio.MUSIC_LOCATION_LOGIN:
            self.loginMusicPaused = False

    def EnableMusic(self):
        self._musicEnabled = True

    def DisableMusic(self):
        if self.lastLocationPlayed:
            self.StopLocationMusic(self.lastLocationPlayed)
        self.lastLocationPlayed = None
        self.loginMusicPaused = False
        self.musicPlaying = False
        self._musicEnabled = False
        return

    def IsMusicEnabled(self):
        return self._musicEnabled

    def SetCharacterCreationMusicState(self, uicore, ccConstRaceStep=1):
        raceID = uicore.layer.charactercreation.raceID
        stepID = uicore.layer.charactercreation.stepID
        if not raceID:
            self.sendEvent(eveaudio.MUSIC_STATE_FULL)
            self.sendEvent(eveaudio.MUSIC_STATE_RACE_NORACE)
        elif stepID == ccConstRaceStep:
            raceState = eveaudio.RACIALMUSICDICT.get(raceID)
            self.sendEvent(raceState)
            self.sendEvent(eveaudio.MUSIC_STATE_FULL)
        else:
            raceState = eveaudio.RACIALMUSICDICT.get(raceID)
            self.sendEvent(raceState)
            self.sendEvent(eveaudio.MUSIC_STATE_AMBIENT)

    def SetSpaceMusicState(self, solarsystemid2, securityStatus):
        if self.oldJukeboxOverride:
            musicState = eveaudio.MUSIC_STATE_OLD_JUKEBOX
        else:
            musicState = GetSpaceMusicState(solarsystemid2, securityStatus)
        if musicState:
            self.sendEvent(musicState)

    def SetDynamicMusicSwitchPopularity(self, pilotsInChannel, securityStatus):
        state = GetDynamicMusicSwitchPopularity(pilotsInChannel, securityStatus)
        if state is not None:
            self.sendEvent(state)
        return


def GetDynamicMusicSwitchPopularity(pilotsInChannel, securityStatus):
    if securityStatus != const.securityClassHighSec:
        return
    elif pilotsInChannel > eveaudio.PILOTS_IN_SPACE_TO_CHANGE_MUSIC:
        return eveaudio.MUSIC_STATE_EMPIRE_POPULATED
    else:
        return eveaudio.MUSIC_STATE_EMPIRE


def GetSpaceMusicState(solarsystemid, securityStatus):
    incursionMusicState = sm.GetService('incursion').GetMusicState(solarsystemid)
    if incursionMusicState is not None:
        return incursionMusicState
    else:
        if securityStatus == const.securityClassZeroSec:
            if solarsystemid > eveaudio.WORMHOLE_SYSTEM_ID_STARTS:
                if solarsystemid in eveaudio.MUSIC_STATE_NULLSEC_SPECIAL_SYSTEMS:
                    return eveaudio.MUSIC_STATE_NULLSEC_SPECIAL
                return eveaudio.MUSIC_STATE_NULLSEC_WORMHOLE
            else:
                return eveaudio.MUSIC_STATE_NULLSEC
        else:
            if securityStatus == const.securityClassLowSec:
                return eveaudio.MUSIC_STATE_LOWSEC
            if securityStatus == const.securityClassHighSec:
                return eveaudio.MUSIC_STATE_EMPIRE
        return


def GetMusicLocation(uicore, solarsystemid2):
    if getattr(uicore.layer.login, 'isopen', None) or getattr(uicore.layer.charsel, 'isopen', None) or getattr(uicore.layer.charsel, 'isopening', None):
        return eveaudio.MUSIC_LOCATION_LOGIN
    elif getattr(uicore.layer.charactercreation, 'isopen', None) or getattr(uicore.layer.charactercreation, 'isopening', None):
        return eveaudio.MUSIC_LOCATION_CHARACTER_CREATION
    elif solarsystemid2:
        return eveaudio.MUSIC_LOCATION_SPACE
    else:
        return