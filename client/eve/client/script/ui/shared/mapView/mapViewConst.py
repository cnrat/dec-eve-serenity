# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\mapView\mapViewConst.py
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_SECURITY
UNIVERSE_SCALE = 1.5e-13
SOLARSYSTEM_SCALE = 1e-10
STAR_SIZE = 60.0
MAX_MARKER_DISTANCE = 220000.0
MIN_CAMERA_DISTANCE = 10.0
MAX_CAMERA_DISTANCE = 200000.0
MIN_CAMERA_DISTANCE_SOLARSYSTEMVIEW = 1.0
MAX_CAMERA_DISTANCE_SOLARSYSTEMVIEW = 2500.0
JUMPLINE_BASE_WIDTH = 2.5
AUTOPILOT_LINE_TICKSIZE = const.AU * 10000 * UNIVERSE_SCALE
AUTOPILOT_LINE_ANIM_SPEED = 3.0
AUTOPILOT_LINE_WIDTH = JUMPLINE_BASE_WIDTH * 2
CONSTELLATION_LINE_TICKSIZE = const.AU * 5000 * UNIVERSE_SCALE
REGION_LINE_TICKSIZE = const.AU * 10000 * UNIVERSE_SCALE
AUDIO_SOLARSYSTEM_DISTANCE = 10.0
AUDIO_CONSTELLATION_DISTANCE = 50.0
SETTING_PREFIX = 'mapview1'
VIEWMODE_LAYOUT_SETTINGS = SETTING_PREFIX + '_majorlayout'
VIEWMODE_LAYOUT_SOLARSYSTEM = 0
VIEWMODE_LAYOUT_CONSTELLATIONS = 1
VIEWMODE_LAYOUT_REGIONS = 2
VIEWMODE_LAYOUT_DEFAULT = VIEWMODE_LAYOUT_SOLARSYSTEM
VIEWMODE_LINES_SETTINGS = SETTING_PREFIX + '_lines'
VIEWMODE_LINES_NONE = 3
VIEWMODE_LINES_ALL = 4
VIEWMODE_LINES_SELECTION = 5
VIEWMODE_LINES_SELECTION_REGION = 6
VIEWMODE_LINES_SELECTION_REGION_NEIGHBOURS = 7
VIEWMODE_LINES_DEFAULT = VIEWMODE_LINES_ALL
VIEWMODE_LINES_SHOW_ALLIANCE_SETTINGS = SETTING_PREFIX + '_show_alliance_lines'
VIEWMODE_LINES_SHOW_ALLIANCE_DEFAULT = True
VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS = SETTING_PREFIX + '_layout'
VIEWMODE_LAYOUT_SHOW_ABSTRACT_DEFAULT = False
VIEWMODE_COLOR_SETTINGS = SETTING_PREFIX + '_colormode'
VIEWMODE_COLOR_DEFAULT = STARMODE_SECURITY
VIEWMODE_COLOR_RECENT = SETTING_PREFIX + '_recent_colormode'
VIEWMODE_COLOR_RECENT_DEFAULT = [VIEWMODE_COLOR_DEFAULT]
VIEWMODE_COLOR_RECENT_MAX = 5
VIEWMODE_MARKERS_SETTINGS = SETTING_PREFIX + '_systemmap_markers'
MARKERS_OPTION_PERSONAL_LOCATION = 'personal_location'
MARKERS_OPTION_CORPORATION_LOCATION = 'corporation_location'
VIEWMODE_MARKERS_OPTIONS_CUSTOM = [MARKERS_OPTION_PERSONAL_LOCATION, MARKERS_OPTION_CORPORATION_LOCATION]
VIEWMODE_MARKERS_CUSTOM_LABELS = {MARKERS_OPTION_PERSONAL_LOCATION: 'UI/PeopleAndPlaces/PersonalLocations',
 MARKERS_OPTION_CORPORATION_LOCATION: 'UI/PeopleAndPlaces/CorporationLocations'}
VIEWMODE_MARKERS_OPTIONS = [const.groupScannerProbe,
 const.groupPlanet,
 const.groupMoon,
 const.groupStation,
 const.groupAsteroidBelt,
 const.groupBeacon,
 const.groupSatellite,
 const.groupStargate,
 const.groupSovereigntyClaimMarkers,
 const.groupSun]
VIEWMODE_MARKERS_DEFAULT = VIEWMODE_MARKERS_OPTIONS + VIEWMODE_MARKERS_OPTIONS_CUSTOM
VIEWMODE_MARKERS_OVERLAP_SORT_ORDER = [const.groupStargate,
 const.groupAsteroidBelt,
 const.groupStation,
 const.groupScannerProbe,
 const.groupPlanet,
 const.groupMoon,
 const.groupBeacon,
 const.groupSatellite,
 const.groupSovereigntyClaimMarkers,
 const.groupSun]
DEFAULT_MAPVIEW_SETTINGS = {VIEWMODE_LAYOUT_SETTINGS: VIEWMODE_LAYOUT_DEFAULT,
 VIEWMODE_COLOR_SETTINGS: VIEWMODE_COLOR_DEFAULT,
 VIEWMODE_COLOR_RECENT: VIEWMODE_COLOR_RECENT_DEFAULT,
 VIEWMODE_LAYOUT_SHOW_ABSTRACT_SETTINGS: VIEWMODE_LAYOUT_SHOW_ABSTRACT_DEFAULT,
 VIEWMODE_LINES_SETTINGS: VIEWMODE_LINES_DEFAULT,
 VIEWMODE_LINES_SHOW_ALLIANCE_SETTINGS: VIEWMODE_LINES_SHOW_ALLIANCE_DEFAULT,
 VIEWMODE_MARKERS_SETTINGS: VIEWMODE_MARKERS_DEFAULT}
VIEWMODE_FOCUS_SELF = 'focus_self'
MARKERID_MYPOS = 1
MARKERID_MYHOME = 2
MARKERID_BOOKMARK = 3
MARKERID_ROUTE = 4
MARKERID_SCANRESULT = 5
MARKERID_SOLARSYSTEM_CELESTIAL = 6
MARKERID_PROBE = 7
MARKERID_SCANRESULT_OVERLAP_SORT_ORDER = 0
MARKERID_MYPOS_OVERLAP_SORT_ORDER = 1
MARKERID_MYHOME_OVERLAP_SORT_ORDER = 2
MARKER_TYPES = (MARKERID_MYPOS,
 MARKERID_BOOKMARK,
 MARKERID_ROUTE,
 MARKERID_SOLARSYSTEM_CELESTIAL,
 MARKERID_MYHOME,
 MARKERID_PROBE,
 MARKERID_SCANRESULT)
MARKER_POINT_LEFT = 0
MARKER_POINT_TOP = 1
MARKER_POINT_RIGHT = 2
MARKER_POINT_BOTTOM = 3
JUMPBRIDGE_COLOR = (0.0, 1.0, 0.0, 1.0)
JUMPBRIDGE_CURVE_SCALE = 0.5
JUMPBRIDGE_TYPE = 4
MAPVIEW_CAMERA_SETTINGS = SETTING_PREFIX + '_camera'
MAPVIEW_PRIMARY_ID = 'primary'
MAPVIEW_PRIMARY_OVERLAY_ID = 'primary_overlay'
MAPVIEW_SOLARSYSTEM_ID = 'solarsystem'