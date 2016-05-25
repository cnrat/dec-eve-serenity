# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\eve\client\script\ui\shared\infoPanels\infoPanelConst.py
from eve.client.script.ui.view.viewStateConst import ViewState
PANEL_LOCATION_INFO = 1
PANEL_ROUTE = 2
PANEL_MISSIONS = 3
PANEL_INCURSIONS = 4
PANEL_FACTIONAL_WARFARE = 5
PANEL_PLANETARY_INTERACTION = 6
PANEL_SHIP_TREE = 7
PANEL_ACHIEVEMENTS = 8
PANEL_QUESTS = 9
PANELTYPES = (PANEL_LOCATION_INFO,
 PANEL_ROUTE,
 PANEL_MISSIONS,
 PANEL_INCURSIONS,
 PANEL_FACTIONAL_WARFARE,
 PANEL_PLANETARY_INTERACTION,
 PANEL_SHIP_TREE,
 PANEL_ACHIEVEMENTS,
 PANEL_QUESTS)
MODE_NORMAL = 1
MODE_COMPACT = 2
MODE_COLLAPSED = 3
PANELWIDTH = 312
LEFTPAD = 42
PANEL_DEFAULT_SETTINGS = {ViewState.Planet: [[PANEL_LOCATION_INFO, MODE_COMPACT], [PANEL_PLANETARY_INTERACTION, MODE_NORMAL]],
 ViewState.StarMap: [[PANEL_LOCATION_INFO, MODE_NORMAL], [PANEL_ROUTE, MODE_NORMAL]],
 ViewState.SystemMap: [[PANEL_LOCATION_INFO, MODE_NORMAL], [PANEL_ROUTE, MODE_NORMAL]],
 ViewState.ShipTree: [[PANEL_SHIP_TREE, MODE_NORMAL]],
 ViewState.Hangar: [[PANEL_LOCATION_INFO, MODE_NORMAL],
                    [PANEL_ROUTE, MODE_NORMAL],
                    [PANEL_INCURSIONS, MODE_NORMAL],
                    [PANEL_MISSIONS, MODE_NORMAL],
                    [PANEL_FACTIONAL_WARFARE, MODE_NORMAL],
                    [PANEL_ACHIEVEMENTS, MODE_NORMAL],
                    [PANEL_QUESTS, MODE_NORMAL]],
 ViewState.Structure: [[PANEL_LOCATION_INFO, MODE_NORMAL],
                       [PANEL_ROUTE, MODE_NORMAL],
                       [PANEL_INCURSIONS, MODE_NORMAL],
                       [PANEL_MISSIONS, MODE_NORMAL],
                       [PANEL_FACTIONAL_WARFARE, MODE_NORMAL],
                       [PANEL_ACHIEVEMENTS, MODE_NORMAL],
                       [PANEL_QUESTS, MODE_NORMAL]],
 ViewState.Space: [[PANEL_LOCATION_INFO, MODE_NORMAL],
                   [PANEL_ROUTE, MODE_NORMAL],
                   [PANEL_INCURSIONS, MODE_NORMAL],
                   [PANEL_MISSIONS, MODE_NORMAL],
                   [PANEL_FACTIONAL_WARFARE, MODE_NORMAL],
                   [PANEL_ACHIEVEMENTS, MODE_NORMAL],
                   [PANEL_QUESTS, MODE_NORMAL]],
 ViewState.VirtualGoodsStore: [],
 ViewState.DockPanel: []}