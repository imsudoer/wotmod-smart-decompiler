# -*- coding: utf-8 -*-
"""
mod_StatsPRO_0103_LE.py - World of Warplanes In-Battle HUD Statistics Mod
Deobfuscated and reconstructed from PJOrion bytecode.
Target Environment: BigWorld Engine, Python 2.7
"""

import StringIO
import socket
import struct
import datetime
import json
from threading import Timer

import BigWorld
import Keys
import GlobalEvents
import ResMgr
import GUI
import GameEnvironment
import EntityStates
from EntityHelpers import isAvatar

import gui.hud
import clientEconomics
import ClientArena
import TeamObject
import ACSector
from gui.HUD2.features.CombatLog.CombatLogSource import CombatLogSource, LOG_DEATH_REASON
from gui.HUD2.features.Entities.EntitySource import EntitySource
import gui.HUD2.features.Sectors
import gui.HUD2.features.Player.PlayerSource
import gui.Scaleform.GameOptions.preservers.GraphicSettingsPreserver
import Camera
import Helpers

# ==============================================================================
# Configuration Constants & File Paths
# ==============================================================================

CONFIG_PATH_DEFAULT = 'scripts/client/mods/configs/StatsPRO.xml'
CONFIG_PATHS_BY_RES = {
    1280: 'scripts/client/mods/configs/StatsPROconfigs/for different resolutions/1280/StatsPRO.xml',
    1360: 'scripts/client/mods/configs/StatsPROconfigs/for different resolutions/1360/StatsPRO.xml',
    1366: 'scripts/client/mods/configs/StatsPROconfigs/for different resolutions/1366/StatsPRO.xml',
    1440: 'scripts/client/mods/configs/StatsPROconfigs/for different resolutions/1440/StatsPRO.xml',
    1600: 'scripts/client/mods/configs/StatsPROconfigs/for different resolutions/1600/StatsPRO.xml',
    1632: 'scripts/client/mods/configs/StatsPROconfigs/for different resolutions/1632/StatsPRO.xml',
    1680: 'scripts/client/mods/configs/StatsPROconfigs/for different resolutions/1680/StatsPRO.xml',
    1920: 'scripts/client/mods/configs/StatsPROconfigs/for different resolutions/1920/StatsPRO.xml',
    2560: 'scripts/client/mods/configs/StatsPROconfigs/for different resolutions/2560/StatsPRO.xml',
}

NTP_SERVERS = (
    'time.windows.com',
    'ntp.iitb.ac.in',
    'time.nist.gov',
    'pool.ntp.org'
)

# Multipliers defining character reservation widths for HUD fields
FIELD_WIDTH_MULTIPLIERS = {
    'points': 9,
    'fragsdeaths': 7,
    'frags': 2,
    'deaths': 2,
    'fragsP': 2,
    'fragsD': 2,
    'fragsB': 2,
    'frags_RAMMING': 2,
    'frags_FIRING': 2,
    'frags_ROCKET': 2,
    'frags_BOMB': 2,
    'frags_GUNNER': 2,
    'frags_f': 2,
    'frags_m': 2,
    'frags_h': 2,
    'frags_a': 2,
    'frags_b': 2,
    'frags_df': 2,
    'frags_dh': 2,
    'assists_air': 2,
    'assists_ground': 2,
    'in_atk': 2,
    'in_def': 2,
    'objects': 2,
    'small_object': 2,
    'medium_object': 2,
    'hevy_object': 2,
    'special_object': 2,
    'parts': 2,
    'part': 2,
    'armored_part': 2,
    'aagun': 2,
    'captured': 4,
    'points_cap': 4,
    'points_cap_attack': 4,
    'points_cap_defend': 3,
    'points_air': 3,
    'points_ground': 7,
    'sector': 7,
    'damage_air': 7,
    'damage_ally': 8,
    'damage_ground': 9,
    'dmg_log': 1
}

# ==============================================================================
# Global HUD State & Battle Statistics
# ==============================================================================

g_active_config_path = CONFIG_PATH_DEFAULT
g_res_mods_dir = ''
g_hud_window = None
g_hud_elements = {}
g_hud_icons = {}
g_part_states_cache = {}
g_damage_log_timer = None
g_tab_pressed = 0
g_in_attack_sector = 'False'

# Primary battle stats tracking dictionary
g_battle_stats = {
    'points': 0,
    'fragsdeaths': '00 : 00',
    'frags': 0,
    'deaths': 0,
    'fragsP': 0,
    'fragsD': 0,
    'fragsB': 0,
    'frags_RAMMING': 0,
    'frags_FIRING': 0,
    'frags_ROCKET': 0,
    'frags_BOMB': 0,
    'frags_GUNNER': 0,
    'frags_f': 0,
    'frags_m': 0,
    'frags_h': 0,
    'frags_a': 0,
    'frags_b': 0,
    'frags_df': 0,
    'frags_dh': 0,
    'assists_air': 0,
    'assists_ground': 0,
    'in_atk': 0,
    'in_def': 0,
    'objects': 0,
    'small_object': 0,
    'medium_object': 0,
    'hevy_object': 0,
    'special_object': 0,
    'parts': 0,
    'part': 0,
    'armored_part': 0,
    'aagun': 0,
    'captured': 0,
    'points_cap': 0,
    'points_cap_attack': 0,
    'points_cap_defend': 0,
    'points_air': 0,
    'points_ground': 0,
    'sector': 'start',
    'damage_air': 0.0,
    'damage_ally': 0.0,
    'damage_ground': 0.0,
    'dmg_log': u'',
    'medals_Akamatsu': 0,
    'medals_Doolitlle': 0,
    'medals_Efimov': 0,
    'medals_Gabreski': 0,
    'medals_Golubev': 0,
    'medals_Groehler': 0,
    'medals_Horikoshi': 0,
    'medals_Johnson': 0,
    'medals_Lambert': 0,
    'medals_Lang': 0,
    'medals_Marseille': 0,
    'medals_McCampbell': 0,
    'medals_McGuire': 0,
    'medals_Kozhedub': 0,
    'medalhunter': 0
}

# ==============================================================================
# Dynamic Configuration Settings (Populated by load_config)
# ==============================================================================

g_detect_resolution = 'False'
g_txt_offset_yc = -4
g_txt_color_r = 255
g_txt_color_g = 255
g_txt_color_b = 255
g_txt_alpha = 255
g_txt_font = 'modDefault_14.font'
g_txt_h_anchor = 'LEFT'
g_shadow_enabled = 'True'
g_shadow_offset = 1
g_shadow_color = ['64', '64', '64', '32']
g_total_modes = 0
g_mode_key = 'KEY_F1'
g_mod_mode = 0

g_display_0 = []
g_display_1 = []
g_display_2 = []
g_display_3 = []
g_display_4 = []
g_display_5 = []
g_display_6 = []

g_display_always_0 = 'True'
g_display_always_1 = 'True'
g_display_always_2 = 'True'
g_display_always_3 = 'True'
g_display_always_4 = 'True'
g_display_always_5 = 'True'
g_display_always_6 = 'True'

g_main_block_size_h = 1.09
g_main_block_size_w = 1.09
g_spectator_block_size_h = 1.09
g_spectator_block_size_w = 1.09
g_block_size_w1 = 0.83
g_block_size_w = 1.56
g_main_block_y = 0.0
g_spectator_block_y = 0.27
g_icons_path = 'icons\\0\\'
g_icons_size = ['24', '24']
g_icons_v_pos = 'BOTTOM'
g_right_icons = ('frags_m', 'frags_h', 'frags_a', 'frags_b', 'fragsB')

g_newline_b = {}
g_newline_e = {}
g_offset_y = {}
g_offset_tab_b = {}
g_offset_n_b = {}
g_offset_l_b = {}
g_offset_m_b = {}
g_offset_b_b = {}
g_offset_n_e = {}
g_offset_l_e = {}
g_offset_m_e = {}
g_offset_b_e = {}
g_offset_u1_b = {}
g_offset_u2_b = {}
g_offset_u3_b = {}
g_offset_u4_b = {}
g_offset_u5_b = {}
g_offset_u6_b = {}
g_offset_u1_e = {}
g_offset_u2_e = {}
g_offset_u3_e = {}
g_offset_u4_e = {}
g_offset_u5_e = {}
g_offset_u6_e = {}

g_offset_tab = 0
g_offset_n = 0
g_offset_l = 0
g_offset_m = 0
g_offset_b = 0
g_offset_u1 = 0
g_offset_u2 = 0
g_offset_u3 = 0
g_offset_u4 = 0
g_offset_u5 = 0
g_offset_u6 = 0
g_top_offset = 0
g_bottom_offset = -30
g_lines_offset = 0
g_icon_offset_xc = 0
g_icon_offset_yc = 0

# Determine game directory paths
try:
    _res_base = ResMgr.resolveToAbsolutePath('../paths.xml')[:-9]
    _res_mods = None
    _paths_sec = ResMgr.openSection('../paths.xml')['Paths']
    for _val in _paths_sec.values():
        _s = _val.asString
        if 'res_mods' in _s:
            _res_mods = _s
            break
    if _res_mods:
        g_res_mods_dir = _res_base + _res_mods + '/'
except Exception:
    g_res_mods_dir = ''

# ==============================================================================
# Core Functions: License Verification & Configuration Loading
# ==============================================================================

def get_ntp_timestamp(addr):
    """Query an NTP server to obtain the current UTC timestamp."""
    ntp_epoch_delta = 0x83AA7E80L # Seconds between 1900-01-01 and 1970-01-01
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_data = '\x1b' + 47 * '\x00'
    try:
        sock.settimeout(5)
        sock.sendto(packet_data, (addr, 123))
        recv_data, _ = sock.recvfrom(1024)
        if recv_data:
            transmit_timestamp = struct.unpack('!12I', recv_data)[10]
            transmit_timestamp -= ntp_epoch_delta
            return transmit_timestamp
    except socket.timeout:
        return None
    except Exception:
        return None
    finally:
        sock.close()
    return None

def check_license_validity():
    """Verify license expiration date against public NTP time."""
    current_time = None
    for server in NTP_SERVERS:
        ts = get_ntp_timestamp(server)
        if ts is not None:
            current_time = datetime.datetime.fromtimestamp(ts)
            break
    if current_time is not None:
        expiration_date = datetime.datetime(2026, 12, 31)
        if current_time < expiration_date:
            return True
        return False
    return True # Allow execution if NTP servers cannot be reached

def load_config():
    """Read XML configuration settings based on current screen resolution."""
    global g_active_config_path, g_detect_resolution, g_txt_offset_yc
    global g_txt_color_r, g_txt_color_g, g_txt_color_b, g_txt_alpha
    global g_txt_font, g_txt_h_anchor, g_shadow_enabled, g_shadow_offset, g_shadow_color
    global g_total_modes, g_mode_key, g_mod_mode
    global g_display_0, g_display_1, g_display_2, g_display_3, g_display_4, g_display_5, g_display_6
    global g_display_always_0, g_display_always_1, g_display_always_2, g_display_always_3
    global g_display_always_4, g_display_always_5, g_display_always_6
    global g_main_block_size_h, g_main_block_size_w, g_spectator_block_size_h, g_spectator_block_size_w
    global g_block_size_w1, g_block_size_w, g_main_block_y, g_spectator_block_y
    global g_icons_path, g_icons_size, g_icons_v_pos, g_right_icons
    global g_newline_b, g_newline_e, g_offset_y
    global g_offset_tab_b, g_offset_n_b, g_offset_l_b, g_offset_m_b, g_offset_b_b
    global g_offset_n_e, g_offset_l_e, g_offset_m_e, g_offset_b_e
    global g_offset_u1_b, g_offset_u2_b, g_offset_u3_b, g_offset_u4_b, g_offset_u5_b, g_offset_u6_b
    global g_offset_u1_e, g_offset_u2_e, g_offset_u3_e, g_offset_u4_e, g_offset_u5_e, g_offset_u6_e
    global g_offset_tab, g_offset_n, g_offset_l, g_offset_m, g_offset_b
    global g_offset_u1, g_offset_u2, g_offset_u3, g_offset_u4, g_offset_u5, g_offset_u6
    global g_top_offset, g_bottom_offset, g_lines_offset, g_icon_offset_xc, g_icon_offset_yc

    if g_detect_resolution == 'True':
        screen_w = int(BigWorld.screenSize()[0])
        if screen_w >= 2560:
            g_active_config_path = CONFIG_PATHS_BY_RES[2560]
        elif screen_w >= 1920:
            g_active_config_path = CONFIG_PATHS_BY_RES[1920]
        elif screen_w >= 1680:
            g_active_config_path = CONFIG_PATHS_BY_RES[1680]
        elif screen_w >= 1632:
            g_active_config_path = CONFIG_PATHS_BY_RES[1632]
        elif screen_w >= 1600:
            g_active_config_path = CONFIG_PATHS_BY_RES[1600]
        elif screen_w >= 1440:
            g_active_config_path = CONFIG_PATHS_BY_RES[1440]
        elif screen_w >= 1366:
            g_active_config_path = CONFIG_PATHS_BY_RES[1366]
        elif screen_w >= 1360:
            g_active_config_path = CONFIG_PATHS_BY_RES[1360]
        else:
            g_active_config_path = CONFIG_PATHS_BY_RES[1280]
    else:
        g_active_config_path = CONFIG_PATH_DEFAULT

    sec = ResMgr.openSection(g_active_config_path)
    if sec is None:
        return

    g_detect_resolution = sec.readString('detectResolution', 'False')
    g_txt_offset_yc = sec.readInt('txtOffsetyc', -4)
    raw_color = sec.readString('txtColor', '255,255,255').split(',')
    if len(raw_color) >= 3:
        g_txt_color_r = int(raw_color[0])
        g_txt_color_g = int(raw_color[1])
        g_txt_color_b = int(raw_color[2])
    g_txt_alpha = sec.readInt('txtAlpha', 255)
    g_txt_font = sec.readString('txtFont', 'modDefault_14.font')
    g_txt_h_anchor = sec.readString('txthorizontalAnchor', 'LEFT')
    g_shadow_enabled = sec.readString('shadow', 'True')
    g_shadow_offset = sec.readInt('shadowoffset', 1)
    g_shadow_color = sec.readString('shadowcolor', '64,64,64,32').split(',')
    g_total_modes = sec.readInt('total_modes', 1)
    g_mode_key = 'KEY_' + sec.readString('mode_key', 'F1').upper()

    def _split_or_empty(s):
        return s.split(',') if len(s) else []

    g_display_0 = _split_or_empty(sec.readString('display', ''))
    g_display_1 = _split_or_empty(sec.readString('display1', ''))
    g_display_2 = _split_or_empty(sec.readString('display2', ''))
    g_display_3 = _split_or_empty(sec.readString('display3', ''))
    g_display_4 = _split_or_empty(sec.readString('display4', ''))
    g_display_5 = _split_or_empty(sec.readString('display5', ''))
    g_display_6 = _split_or_empty(sec.readString('display6', ''))

    g_display_always_0 = sec.readString('display_always', 'True')
    g_display_always_1 = sec.readString('display1_always', 'True')
    g_display_always_2 = sec.readString('display2_always', 'True')
    g_display_always_3 = sec.readString('display3_always', 'True')
    g_display_always_4 = sec.readString('display4_always', 'True')
    g_display_always_5 = sec.readString('display5_always', 'True')
    g_display_always_6 = sec.readString('display6_always', 'True')

    g_mod_mode = sec.readInt('mode', 0)
    g_main_block_size_h = sec.readFloat('mainblockSizeH', 1.09)
    g_main_block_size_w = sec.readFloat('mainblockSizeW', 1.09)
    g_spectator_block_size_h = sec.readFloat('spectatorblockSizeH', 1.09)
    g_spectator_block_size_w = sec.readFloat('spectatorblockSizeW', 1.09)
    g_block_size_w1 = sec.readFloat('blockSizeW1', 0.83)
    g_block_size_w = sec.readFloat('blockSizeW', 1.56)
    g_main_block_y = sec.readFloat('mainblockY', 0.0)
    g_spectator_block_y = sec.readFloat('spectatorblockY', 0.27)
    g_icons_path = sec.readString('iconspath', 'icons\\0\\')
    g_icons_size = _split_or_empty(sec.readString('iconssize', '24,24'))
    g_icons_v_pos = sec.readString('IconsVpos', 'BOTTOM')
    g_right_icons = _split_or_empty(sec.readString('righticons', 'frags_m,frags_h,frags_a,frags_b,fragsB'))

    def _json_or_dict(s):
        try:
            return json.loads(s) if len(s) else {}
        except Exception:
            return {}

    g_newline_b = _json_or_dict(sec.readString('newlineb', ''))
    g_newline_e = _json_or_dict(sec.readString('newlinee', ''))
    g_offset_y = _json_or_dict(sec.readString('offsety', ''))
    g_offset_tab_b = _json_or_dict(sec.readString('offsettabb', ''))
    g_offset_n_b = _json_or_dict(sec.readString('offsetnb', ''))
    g_offset_l_b = _json_or_dict(sec.readString('offsetlb', ''))
    g_offset_m_b = _json_or_dict(sec.readString('offsetmb', ''))
    g_offset_b_b = _json_or_dict(sec.readString('offsetbb', ''))
    g_offset_n_e = _json_or_dict(sec.readString('offsetne', ''))
    g_offset_l_e = _json_or_dict(sec.readString('offsetle', ''))
    g_offset_m_e = _json_or_dict(sec.readString('offsetme', ''))
    g_offset_b_e = _json_or_dict(sec.readString('offsetbe', ''))
    g_offset_u1_b = _json_or_dict(sec.readString('offsetu1b', ''))
    g_offset_u2_b = _json_or_dict(sec.readString('offsetu2b', ''))
    g_offset_u3_b = _json_or_dict(sec.readString('offsetu3b', ''))
    g_offset_u4_b = _json_or_dict(sec.readString('offsetu4b', ''))
    g_offset_u5_b = _json_or_dict(sec.readString('offsetu5b', ''))
    g_offset_u6_b = _json_or_dict(sec.readString('offsetu6b', ''))
    g_offset_u1_e = _json_or_dict(sec.readString('offsetu1e', ''))
    g_offset_u2_e = _json_or_dict(sec.readString('offsetu2e', ''))
    g_offset_u3_e = _json_or_dict(sec.readString('offsetu3e', ''))
    g_offset_u4_e = _json_or_dict(sec.readString('offsetu4e', ''))
    g_offset_u5_e = _json_or_dict(sec.readString('offsetu5e', ''))
    g_offset_u6_e = _json_or_dict(sec.readString('offsetu6e', ''))

    g_offset_tab = sec.readInt('offsettab', 0)
    g_offset_n = sec.readInt('offsetn', 0)
    g_offset_l = sec.readInt('offsetl', 0)
    g_offset_m = sec.readInt('offsetm', 0)
    g_offset_b = sec.readInt('offsetb', 0)
    g_offset_u1 = sec.readInt('offsetu1', 0)
    g_offset_u2 = sec.readInt('offsetu2', 0)
    g_offset_u3 = sec.readInt('offsetu3', 0)
    g_offset_u4 = sec.readInt('offsetu4', 0)
    g_offset_u5 = sec.readInt('offsetu5', 0)
    g_offset_u6 = sec.readInt('offsetu6', 0)
    g_top_offset = sec.readInt('topoffset', 0)
    g_bottom_offset = sec.readInt('bottomoffset', -30)
    g_lines_offset = sec.readInt('linesoffset', 0)
    g_icon_offset_xc = sec.readInt('iconOffsetxc', 0)
    g_icon_offset_yc = sec.readInt('iconOffsetyc', 0)

    ResMgr.purge(g_active_config_path, True)

# ==============================================================================
# HUD Construction, Layout, & Visual Rendering
# ==============================================================================

def create_text_shadows(parent_line, text_elem, stat_name):
    """Create 4-directional drop shadows for a HUD text element."""
    stat_key = str(stat_name)
    shadow_names = [
        'txt' + stat_key + 'shadow',
        'txt' + stat_key + 'shadow1',
        'txt' + stat_key + 'shadow2',
        'txt' + stat_key + 'shadow3'
    ]
    color_tuple = (
        int(g_shadow_color[0]),
        int(g_shadow_color[1]),
        int(g_shadow_color[2]),
        int(g_shadow_color[3])
    )
    val_str = str(g_battle_stats.get(stat_key, ''))
    if 'damage' in stat_key:
        val_str = val_str.split('.')[0]

    for name in shadow_names:
        shadow_txt = GUI.Text('')
        shadow_txt.multiline = True
        shadow_txt.widthMode = 'PIXEL'
        shadow_txt.heightMode = 'PIXEL'
        shadow_txt.verticalPositionMode = 'PIXEL'
        shadow_txt.horizontalPositionMode = 'PIXEL'
        shadow_txt.horizontalAnchor = g_txt_h_anchor
        shadow_txt.verticalAnchor = 'CENTER'
        shadow_txt.colour = color_tuple
        shadow_txt.font = g_txt_font
        shadow_txt.visible = True
        shadow_txt.filterType = 'POINT'
        shadow_txt.text = val_str
        g_hud_elements[name] = shadow_txt

    base_x = text_elem.position.x
    base_y = text_elem.position.y
    g_hud_elements[shadow_names[0]].position.x = base_x + g_shadow_offset
    g_hud_elements[shadow_names[0]].position.y = base_y
    g_hud_elements[shadow_names[1]].position.x = base_x - g_shadow_offset
    g_hud_elements[shadow_names[1]].position.y = base_y
    g_hud_elements[shadow_names[2]].position.x = base_x
    g_hud_elements[shadow_names[2]].position.y = base_y + g_shadow_offset
    g_hud_elements[shadow_names[3]].position.x = base_x
    g_hud_elements[shadow_names[3]].position.y = base_y - g_shadow_offset

    for name in shadow_names:
        parent_line.addChild(g_hud_elements[name], name)

def _render_stat_group(parent_window, group_items, initial_y=0):
    """Instantiate and position icons, labels, and shadows for a group of stats."""
    x_cursor = 0
    y_pos = initial_y

    for stat_key in group_items:
        stat_name = str(stat_key)

        # 1. Newline offset before element
        if stat_name in g_newline_b:
            delta_y = (g_icon_offset_yc + g_lines_offset) * int(g_newline_b[stat_name])
            y_pos += delta_y
            x_cursor = 0

        # 2. Icon setup
        icon_path = g_icons_path + stat_name + '.dds'
        if not ResMgr.isFile(icon_path):
            icon_path = g_icons_path + 'notfound.dds'

        icon = GUI.Simple(icon_path)
        icon.horizontalPositionMode = 'PIXEL'
        icon.verticalPositionMode = 'PIXEL'
        icon.horizontalAnchor = 'LEFT'
        icon.materialFX = 'BLEND'
        icon.widthMode = 'PIXEL'
        icon.heightMode = 'PIXEL'
        if len(g_icons_size) >= 2:
            icon.width = int(g_icons_size[0])
            icon.height = int(g_icons_size[1])

        # 3. Text label setup
        txt = GUI.Text('')
        txt.multiline = True
        txt.horizontalPositionMode = 'PIXEL'
        txt.verticalPositionMode = 'PIXEL'
        txt.horizontalAnchor = g_txt_h_anchor
        txt.colour = (g_txt_color_r, g_txt_color_g, g_txt_color_b, g_txt_alpha)
        txt.font = g_txt_font

        stat_val = g_battle_stats.get(stat_key, 0)
        if 'damage' in stat_name:
            txt.text = str(stat_val).split('.')[0]
        else:
            txt.text = str(stat_val)

        # 4. Vertical positioning & per-stat offset
        icon.position.y = y_pos
        txt.position.y = y_pos + g_txt_offset_yc
        if stat_name in g_offset_y:
            y_offset = int(g_offset_y[stat_name])
            icon.position.y += y_offset
            txt.position.y += y_offset

        # 5. Pre-element horizontal offsets
        x_cursor += g_offset_tab * int(g_offset_tab_b.get(stat_name, 0))
        x_cursor += g_offset_n * int(g_offset_n_b.get(stat_name, 0))
        x_cursor += g_offset_l * int(g_offset_l_b.get(stat_name, 0))
        x_cursor += g_offset_m * int(g_offset_m_b.get(stat_name, 0))
        x_cursor += g_offset_b * int(g_offset_b_b.get(stat_name, 0))
        x_cursor += g_offset_u1 * int(g_offset_u1_b.get(stat_name, 0))
        x_cursor += g_offset_u2 * int(g_offset_u2_b.get(stat_name, 0))
        x_cursor += g_offset_u3 * int(g_offset_u3_b.get(stat_name, 0))
        x_cursor += g_offset_u4 * int(g_offset_u4_b.get(stat_name, 0))
        x_cursor += g_offset_u5 * int(g_offset_u5_b.get(stat_name, 0))
        x_cursor += g_offset_u6 * int(g_offset_u6_b.get(stat_name, 0))

        # 6. Horizontal placement (Normal vs Right-side icon)
        multiplier = FIELD_WIDTH_MULTIPLIERS.get(stat_name, 1)
        char_w = txt.stringWidth('0')

        if stat_name in g_right_icons:
            txt.position.x = x_cursor + (char_w / 2) * multiplier
            x_cursor += char_w * multiplier
            icon.position.x = x_cursor
            x_cursor += icon.width
        else:
            icon.position.x = x_cursor
            x_cursor += icon.width
            txt.position.x = x_cursor
            x_cursor += char_w * multiplier

        # 7. Post-element horizontal offsets
        x_cursor += g_offset_n * int(g_offset_n_e.get(stat_name, 0))
        x_cursor += g_offset_l * int(g_offset_l_e.get(stat_name, 0))
        x_cursor += g_offset_m * int(g_offset_m_e.get(stat_name, 0))
        x_cursor += g_offset_b * int(g_offset_b_e.get(stat_name, 0))
        x_cursor += g_offset_u1 * int(g_offset_u1_e.get(stat_name, 0))
        x_cursor += g_offset_u2 * int(g_offset_u2_e.get(stat_name, 0))
        x_cursor += g_offset_u3 * int(g_offset_u3_e.get(stat_name, 0))
        x_cursor += g_offset_u4 * int(g_offset_u4_e.get(stat_name, 0))
        x_cursor += g_offset_u5 * int(g_offset_u5_e.get(stat_name, 0))
        x_cursor += g_offset_u6 * int(g_offset_u6_e.get(stat_name, 0))

        # 8. Newline offset after element
        if stat_name in g_newline_e:
            delta_y = (g_icon_offset_yc + g_lines_offset) * int(g_newline_e[stat_name])
            y_pos += delta_y
            x_cursor = 0

        # 9. Register elements
        parent_window.addChild(icon, stat_name)
        if g_shadow_enabled == 'True':
            create_text_shadows(parent_window, txt, stat_name)
        parent_window.addChild(txt, 'txt' + stat_name)

        g_hud_icons[stat_name] = icon
        g_hud_elements['txt' + stat_name] = txt

    return y_pos

def create_hud_window():
    """Build the GUI hierarchy for the mod according to current configuration mode."""
    global g_hud_window, g_hud_elements, g_hud_icons

    if g_hud_window is not None:
        return

    load_config()

    g_hud_window = GUI.Window('')
    g_hud_window.materialFX = 'BLEND'
    g_hud_window.widthMode = 'CLIP'
    g_hud_window.heightMode = 'CLIP'
    g_hud_window.horizontalPositionMode = 'CLIP'
    g_hud_window.verticalPositionMode = 'CLIP'
    g_hud_window.size = (g_main_block_size_w, g_main_block_size_h)

    g_hud_elements = {}
    g_hud_icons = {}

    display_groups = [
        g_display_0,
        g_display_1,
        g_display_2,
        g_display_3,
        g_display_4,
        g_display_5,
        g_display_6
    ]

    if g_mod_mode == g_total_modes:
        # Multi-line combined view: render all non-empty groups
        total_lines = sum(g_newline_b.values()) + sum(g_newline_e.values())
        for grp in display_groups:
            if grp:
                total_lines += 1

        if g_icons_v_pos == 'BOTTOM':
            screen_h = int(BigWorld.screenSize()[1])
            start_y = screen_h + g_bottom_offset - (g_icon_offset_yc + g_lines_offset) * max(0, total_lines - 1)
        else:
            start_y = g_top_offset

        current_y = start_y
        for idx, grp in enumerate(display_groups):
            if not grp:
                continue
            line_win = GUI.Window('')
            line_win.materialFX = 'BLEND'
            line_win.widthMode = 'CLIP'
            line_win.heightMode = 'CLIP'
            line_win.horizontalPositionMode = 'CLIP'
            line_win.verticalPositionMode = 'CLIP'
            line_win.size = (g_block_size_w, 2)
            current_y = _render_stat_group(line_win, grp, current_y)
            g_hud_window.addChild(line_win, 'line%d' % idx)

    elif g_mod_mode == 0:
        g_hud_window.visible = False

    elif 1 <= g_mod_mode <= len(display_groups):
        # Single group view
        target_group = display_groups[g_mod_mode - 1]
        line_count = 0
        for item in target_group:
            if item in g_newline_b:
                line_count += int(g_newline_b[item])
            if item in g_newline_e:
                line_count += int(g_newline_e[item])

        if g_icons_v_pos == 'BOTTOM':
            screen_h = int(BigWorld.screenSize()[1])
            start_y = screen_h + g_bottom_offset - (g_icon_offset_yc + g_lines_offset) * line_count
        else:
            start_y = g_top_offset

        g_hud_window.size = (g_block_size_w, 2)
        _render_stat_group(g_hud_window, target_group, start_y)

    GUI.addRoot(g_hud_window)
    reposition_hud_window()
    update_hud_visibility()

def destroy_hud_window():
    """Tear down and recreate the HUD GUI hierarchy."""
    global g_hud_window
    if g_hud_window is not None:
        for name, child in list(g_hud_window.children):
            g_hud_window.delChild(child)
        GUI.delRoot(g_hud_window)
        g_hud_window = None
    create_hud_window()

def reposition_hud_window():
    """Adjust window Y position according to vertical alignment setting."""
    if g_hud_window is not None:
        if g_icons_v_pos == 'BOTTOM':
            g_hud_window.position.y = g_spectator_block_y
        elif g_icons_v_pos == 'TOP':
            g_hud_window.position.y = -g_spectator_block_y

def update_hud_dead_position():
    """Reposition HUD when the player enters spectator or dead states."""
    if g_hud_window is None:
        return
    player = BigWorld.player()
    if player is None:
        return

    dead_states = (
        EntityStates.DEAD,
        EntityStates.DESTROYED,
        EntityStates.OBSERVER,
        EntityStates.OUTRO,
        EntityStates.END_GAME,
        EntityStates.DESTROYED_FALL
    )
    if player.state in dead_states:
        if g_icons_v_pos == 'BOTTOM':
            g_hud_window.position.y = g_spectator_block_y
        elif g_icons_v_pos == 'TOP':
            g_hud_window.position.y = -g_spectator_block_y
    else:
        g_hud_window.position.y = g_main_block_y

def on_player_state_updated():
    """Update HUD size and Z-depth based on living vs deceased status."""
    if g_hud_window is None:
        return
    player = BigWorld.player()
    if player is None:
        return

    dead_states = (
        EntityStates.DEAD,
        EntityStates.DESTROYED,
        EntityStates.DESTROYED_FALL,
        EntityStates.OBSERVER,
        EntityStates.OUTRO,
        EntityStates.END_GAME
    )
    if player.state in dead_states:
        z_depth = 0.5
        g_hud_window.size = (g_spectator_block_size_w, g_spectator_block_size_h)
    else:
        z_depth = 1.0
        g_hud_window.size = (g_main_block_size_w, g_main_block_size_h)

    g_hud_window.position.z = z_depth
    for _, child in g_hud_window.children:
        child.position.z = z_depth
    for elem in g_hud_elements.values():
        elem.position.z = z_depth
    for icon in g_hud_icons.values():
        icon.position.z = z_depth

def update_hud_visibility():
    """Toggle HUD visibility according to current game state and mod mode."""
    try:
        player = BigWorld.player()
        if g_hud_window is None:
            return
        if g_mod_mode == 0:
            g_hud_window.visible = False
        elif player is not None and player.state in (
            EntityStates.ALL,
            EntityStates.UNDEFINED,
            EntityStates.CREATED,
            EntityStates.WAIT_START,
            EntityStates.PRE_START_INTRO
        ):
            g_hud_window.visible = False
        else:
            g_hud_window.visible = True
    except Exception:
        pass

def refresh_hud_field(field_name):
    """Update text and shadows for an individual HUD statistic."""
    key = str(field_name)
    txt_key = 'txt' + key

    if txt_key in g_hud_elements:
        if 'damage' in key:
            val_str = str(g_battle_stats.get(key, 0)).split('.')[0]
        elif 'fragsdeaths' in key:
            val_str = '%s : %s' % (g_battle_stats.get('frags', 0), g_battle_stats.get('deaths', 0))
        else:
            val_str = str(g_battle_stats.get(key, 0))

        g_hud_elements[txt_key].text = val_str
        if g_shadow_enabled == 'True':
            for shadow_suffix in ('shadow', 'shadow1', 'shadow2', 'shadow3'):
                s_name = txt_key + shadow_suffix
                if s_name in g_hud_elements:
                    g_hud_elements[s_name].text = val_str

    update_hud_visibility()

def update_all_hud_texts_and_shadows():
    """Synchronize all HUD text elements with current battle stats."""
    try:
        g_battle_stats['fragsdeaths'] = '%s : %s' % (g_battle_stats['frags'], g_battle_stats['deaths'])
        if g_hud_window is None:
            create_hud_window()
            return

        for stat_name, stat_val in g_battle_stats.items():
            key = str(stat_name)
            txt_key = 'txt' + key
            if txt_key in g_hud_elements:
                if 'damage' in key:
                    val_str = str(stat_val).split('.')[0]
                else:
                    val_str = str(stat_val)

                g_hud_elements[txt_key].text = val_str
                if g_shadow_enabled == 'True':
                    for shadow_suffix in ('shadow', 'shadow1', 'shadow2', 'shadow3'):
                        s_name = txt_key + shadow_suffix
                        if s_name in g_hud_elements:
                            g_hud_elements[s_name].text = val_str

        update_hud_visibility()
    except Exception:
        pass

def update_hud_display_values():
    """Refresh text across all child line containers in the HUD hierarchy."""
    g_battle_stats['fragsdeaths'] = '%s : %s' % (g_battle_stats['frags'], g_battle_stats['deaths'])
    if g_hud_window is None:
        create_hud_window()
        return

    groups = (g_display_0, g_display_1, g_display_2, g_display_3, g_display_4, g_display_5, g_display_6)
    if g_mod_mode == g_total_modes:
        for group in groups:
            if not group:
                continue
            for stat_key in group:
                txt_name = 'txt' + str(stat_key)
                shadow_names = (txt_name + 'shadow', txt_name + 'shadow1', txt_name + 'shadow2', txt_name + 'shadow3')
                stat_val = str(g_battle_stats.get(stat_key, 0))
                for line_child in g_hud_window.children:
                    for child in line_child[1].children:
                        if child[0] == txt_name or child[0] in shadow_names:
                            child[1].text = stat_val
    else:
        for group in groups:
            if not group:
                continue
            for stat_key in group:
                txt_name = 'txt' + str(stat_key)
                shadow_names = (txt_name + 'shadow', txt_name + 'shadow1', txt_name + 'shadow2', txt_name + 'shadow3')
                stat_val = str(g_battle_stats.get(stat_key, 0))
                for child in g_hud_window.children:
                    if child[0] == txt_name or child[0] in shadow_names:
                        child[1].text = stat_val

def reset_battle_stats():
    """Zero out all battle statistics for a fresh session."""
    global g_battle_stats, g_damage_log_timer
    for k in g_battle_stats:
        if k == 'fragsdeaths':
            g_battle_stats[k] = '00 : 00'
        elif k == 'sector':
            g_battle_stats[k] = 'start'
        elif k in ('damage_air', 'damage_ally', 'damage_ground'):
            g_battle_stats[k] = 0.0
        elif k == 'dmg_log':
            g_battle_stats[k] = u''
        else:
            g_battle_stats[k] = 0
    if g_damage_log_timer is not None:
        g_damage_log_timer.cancel()
        g_damage_log_timer = None

def cycle_mod_mode():
    """Cycle HUD display mode (0 -> 1 -> ... -> total_modes -> 0) and persist to XML."""
    global g_mod_mode
    load_config()
    g_mod_mode += 1
    if g_mod_mode > g_total_modes:
        g_mod_mode = 0

    sec = ResMgr.openSection(g_active_config_path)
    if sec is not None:
        sec.writeInt('mode', g_mod_mode)
        sec.save()
        ResMgr.purge(g_active_config_path, True)

    full_xml_path = g_res_mods_dir + g_active_config_path
    try:
        with open(full_xml_path, 'r') as f:
            content = f.read()
        content = content.replace('&quot;', '"')
        with open(full_xml_path, 'w') as f:
            f.write(content)
    except Exception:
        pass

    destroy_hud_window()
    update_all_hud_texts_and_shadows()

def set_in_attack_sector(val):
    """Set flag indicating if player is inside an active attack sector."""
    global g_in_attack_sector
    g_in_attack_sector = 'True' if str(val) == 'True' else 'False'

def clear_damage_log():
    """Clear combat damage log string and refresh HUD."""
    global g_damage_log_timer
    g_battle_stats['dmg_log'] = u''
    refresh_hud_field('dmg_log')
    g_damage_log_timer = None

def on_key_event(event):
    """Handle keyboard shortcuts (Ctrl+F1 reset, Shift+F1 V-pos, F1 mode cycle, Tab)."""
    global g_icons_v_pos, g_tab_pressed
    configured_key = getattr(Keys, g_mode_key, Keys.KEY_F1)

    if event.isCtrlDown() and event.key == configured_key and event.isKeyUp():
        reset_battle_stats()
        update_all_hud_texts_and_shadows()
    elif event.isShiftDown() and event.key == configured_key and event.isKeyUp():
        load_config()
        g_icons_v_pos = 'TOP' if g_icons_v_pos == 'BOTTOM' else 'BOTTOM'
        sec = ResMgr.openSection(g_active_config_path)
        if sec is not None:
            sec.writeString('IconsVpos', g_icons_v_pos)
            sec.save()
            ResMgr.purge(g_active_config_path, True)
        full_xml_path = g_res_mods_dir + g_active_config_path
        try:
            with open(full_xml_path, 'r') as f:
                content = f.read()
            content = content.replace('&quot;', '"')
            with open(full_xml_path, 'w') as f:
                f.write(content)
        except Exception:
            pass
        destroy_hud_window()
    elif event.key == configured_key and event.isKeyUp():
        cycle_mod_mode()

    if event.key == Keys.KEY_TAB and event.isKeyDown() and g_tab_pressed == 0:
        if g_hud_window is not None:
            if g_icons_v_pos == 'BOTTOM':
                g_hud_window.position.y = g_spectator_block_y
            elif g_icons_v_pos == 'TOP':
                g_hud_window.position.y = -g_spectator_block_y
        g_tab_pressed = 1

    if event.key == Keys.KEY_TAB and event.isKeyUp():
        g_tab_pressed = 0
        update_hud_dead_position()

# ==============================================================================
# Game Engine Event Hooks
# ==============================================================================

# Save original engine methods before hooking
_orig_refreshBattleLogPoints = clientEconomics.ClientEconomic.refreshBattleLogPoints
_orig_onAvatarDestroyed = CombatLogSource.onAvatarDestroyed
_orig_doLeaveWorld = gui.hud.HUD.doLeaveWorld
_orig_onTeamObjectDestruction = ClientArena.ClientArena._ClientArena__onTeamObjectDestruction
_orig_set_partStates = TeamObject.TeamObject.set_partStates
_orig_onChangeSector = gui.HUD2.features.Sectors.CurretntSectorSource.CurrentSectorSource._onChangeSector
_orig_onSectorStateChanged = gui.HUD2.features.Sectors.SectorSource.SectorSource._onSectorStateChanged
_orig_set_stateContainer = ACSector.ACSector.set_stateContainer
_orig_eAvatarHealthChanged = EntitySource._eAvatarHealthChanged
_orig_onUpdateHealth = gui.HUD2.features.Player.PlayerSource.PlayerSource._onUpdateHealth
_orig_save_video_mode = gui.Scaleform.GameOptions.preservers.GraphicSettingsPreserver.VideoModePreserver.save
_orig_onPlayerAvatarStateChanged = Camera.Camera.onPlayerAvatarStateChanged

def hook_refreshBattleLogPoints(self, events):
    """Intercept battle log score point events and parse combat contributions."""
    _orig_refreshBattleLogPoints(self, events)
    economics = GameEnvironment.getClientEconomics()
    if economics is not None and len(events):
        battle_points = getattr(economics, '_battlePoints', 0)
        desc = (events[0].get('description', '')
                .replace('HUD_', '')
                .replace('MESSAGES_BATTLE_', '')
                .replace('SCORE_', '')
                .replace('DAMAGE_ENEMY_PLANES', 'DMG')
                .replace('DAMAGE_DEFENDER', 'DMG DEF')
                .replace('DAMAGE_ALLY', 'DMG ALLY')
                .lower())

        points_delta = battle_points - g_battle_stats['points']
        if points_delta != 0:
            if desc == 'planes_defender':
                g_battle_stats['frags'] += 1
                g_battle_stats['fragsD'] += 1
                refresh_hud_field('frags')
                refresh_hud_field('fragsD')
                refresh_hud_field('fragsdeaths')
            elif desc == 'enemy_planes':
                g_battle_stats['frags'] += 1
                g_battle_stats['fragsP'] += 1
                refresh_hud_field('frags')
                refresh_hud_field('fragsP')
                refresh_hud_field('fragsdeaths')
            elif desc == 'destroy_bomber':
                g_battle_stats['frags'] += 1
                g_battle_stats['fragsB'] += 1
                refresh_hud_field('frags')
                refresh_hud_field('fragsB')
                refresh_hud_field('fragsdeaths')
            elif desc != 'assist_enemy_planes':
                if desc == 'assist_ground':
                    g_battle_stats['assists_ground'] += 1
                    refresh_hud_field('assists_ground')
                elif desc == 'destroy_part':
                    g_battle_stats['parts'] += 1
                    g_battle_stats['part'] += 1
                    refresh_hud_field('parts')
                    refresh_hud_field('part')
                elif desc == 'destroy_armored_part':
                    g_battle_stats['parts'] += 1
                    g_battle_stats['armored_part'] += 1
                    refresh_hud_field('parts')
                    refresh_hud_field('armored_part')
                elif desc == 'participation_cap_sector':
                    g_battle_stats['captured'] += 1
                    refresh_hud_field('captured')
                elif desc != 'assist_defender':
                    g_battle_stats['assists_air'] += 1
                    refresh_hud_field('assists_air')

            g_battle_stats['points'] = battle_points
            refresh_hud_field('points')

        update_hud_visibility()

def hook_onAvatarDestroyed(self, killingInfo):
    """Track plane frags, death types, attacker plane types, and capture points."""
    try:
        _orig_onAvatarDestroyed(self, killingInfo)
    except Exception:
        pass

    arena_objects = {}
    client_arena = GameEnvironment.getClientArena()
    if client_arena is not None:
        all_objects = getattr(client_arena, '_ClientArena__allObjectsData', {})
        for obj_id, obj_data in all_objects.items():
            grp = obj_data.get('groupName')
            if grp and grp not in arena_objects:
                arena_objects[grp] = obj_id

    current_sector_id = str(killingInfo.get('currentSector', ''))
    sector_state_container = None
    sector_state = None
    for entity in getattr(ACSector.ACSector, 'entities', []):
        if str(getattr(entity, 'ident', '')) == current_sector_id:
            sector_state_container = getattr(entity, 'stateContainer', None)
            if sector_state_container:
                sector_state = getattr(sector_state_container, 'state', None)
            break

    player = BigWorld.player()
    if player is None:
        return
    player_id = player.id
    death_reason = killingInfo.get('deathReason')
    victim_id = killingInfo.get('victimID')
    killer_id = killingInfo.get('killerID')
    avatar_info = getattr(self, '_clientArena').getAvatarInfo(victim_id)
    player_team = player.teamIndex

    if victim_id == player_id:
        g_battle_stats['deaths'] += 1
        g_battle_stats['dmg_log'] = u''
        refresh_hud_field('deaths')
        refresh_hud_field('fragsdeaths')
    elif killer_id == player_id and player_team != killingInfo.get('victimTeamIndex'):
        if death_reason == LOG_DEATH_REASON.ENEMY_RAMMING:
            g_battle_stats['frags_RAMMING'] += 1
            refresh_hud_field('frags_RAMMING')
        elif death_reason == LOG_DEATH_REASON.FIRING:
            g_battle_stats['frags_FIRING'] += 1
            refresh_hud_field('frags_FIRING')
        elif death_reason == LOG_DEATH_REASON.ENEMY_ROCKET:
            g_battle_stats['frags_ROCKET'] += 1
            refresh_hud_field('frags_ROCKET')
        elif death_reason == LOG_DEATH_REASON.ENEMY_BOMB:
            g_battle_stats['frags_BOMB'] += 1
            refresh_hud_field('frags_BOMB')
        elif death_reason == LOG_DEATH_REASON.GUNNER:
            g_battle_stats['frags_GUNNER'] += 1
            refresh_hud_field('frags_GUNNER')

        if avatar_info:
            plane_type = getattr(avatar_info['settings'].airplane, 'planeType', 0)
            is_npc = str(avatar_info.get('isNPC', 'False')) == 'True'
            if plane_type == 1:
                if is_npc:
                    g_battle_stats['frags_df'] += 1
                    refresh_hud_field('frags_df')
                else:
                    g_battle_stats['frags_f'] += 1
                    refresh_hud_field('frags_f')
            elif plane_type == 4:
                g_battle_stats['frags_m'] += 1
                refresh_hud_field('frags_m')
            elif plane_type == 2:
                if is_npc:
                    g_battle_stats['frags_dh'] += 1
                    refresh_hud_field('frags_dh')
                else:
                    g_battle_stats['frags_h'] += 1
                    refresh_hud_field('frags_h')
            elif plane_type == 3:
                g_battle_stats['frags_a'] += 1
                refresh_hud_field('frags_a')
            elif plane_type == 5:
                if is_npc:
                    g_battle_stats['fragsD'] += 1
                    refresh_hud_field('fragsD')
                else:
                    g_battle_stats['frags_b'] += 1
                    refresh_hud_field('frags_b')

            if killingInfo.get('currentSector') in arena_objects:
                if (sector_state_container and sector_state_container.teamIndex != player_team and str(sector_state) == 'C') or avatar_info.get('isNPC'):
                    g_battle_stats['in_def'] += 1
                    g_battle_stats['points_cap'] += 40
                    g_battle_stats['points_cap_defend'] += 40
                    g_battle_stats['points_air'] += 40
                    refresh_hud_field('in_def')
                    refresh_hud_field('points_cap')
                    refresh_hud_field('points_cap_defend')
                    refresh_hud_field('points_air')
                elif str(g_in_attack_sector) == 'True':
                    if avatar_info.get('isNPC') and not avatar_info.get('isBomber'):
                        g_battle_stats['in_atk'] += 1
                        g_battle_stats['points_cap'] += 40
                        g_battle_stats['points_cap_attack'] += 40
                        g_battle_stats['points_air'] += 40
                        refresh_hud_field('in_atk')
                        refresh_hud_field('points_cap')
                        refresh_hud_field('points_cap_attack')
                        refresh_hud_field('points_air')
                    elif not avatar_info.get('isNPC'):
                        g_battle_stats['in_atk'] += 1
                        g_battle_stats['points_cap'] += 60
                        g_battle_stats['points_cap_attack'] += 60
                        g_battle_stats['points_air'] += 60
                        refresh_hud_field('in_atk')
                        refresh_hud_field('points_cap')
                        refresh_hud_field('points_cap_attack')
                        refresh_hud_field('points_air')
                elif str(sector_state) == 'C':
                    if avatar_info.get('isNPC') and not avatar_info.get('isBomber'):
                        g_battle_stats['in_atk'] += 1
                        g_battle_stats['points_cap'] += 40
                        g_battle_stats['points_cap_attack'] += 40
                        g_battle_stats['points_air'] += 40
                        refresh_hud_field('in_atk')
                        refresh_hud_field('points_cap')
                        refresh_hud_field('points_cap_attack')
                        refresh_hud_field('points_air')
                    elif not avatar_info.get('isNPC'):
                        g_battle_stats['in_atk'] += 1
                        g_battle_stats['points_cap'] += 60
                        g_battle_stats['points_cap_attack'] += 60
                        g_battle_stats['points_air'] += 60
                        refresh_hud_field('in_atk')
                        refresh_hud_field('points_cap')
                        refresh_hud_field('points_cap_attack')
                        refresh_hud_field('points_air')

def hook_doLeaveWorld(self):
    """Clean up HUD root and reset session stats upon leaving the match world."""
    global g_hud_window, g_in_attack_sector, g_tab_pressed
    _orig_doLeaveWorld(self)
    g_in_attack_sector = 'False'
    reset_battle_stats()
    g_tab_pressed = 0
    if g_hud_window is not None:
        GUI.delRoot(g_hud_window)
        g_hud_window = None

def hook_onTeamObjectDestruction(self, argStr):
    """Track destruction of ground structures, AA guns, towers, and capture points."""
    unpickler = ClientArena.wgPickle
    info = unpickler.loads(unpickler.FromServerToClient, argStr)
    victim_data = self._ClientArena__allObjectsData[info['victimID']]
    sup_points, sec_points = self.getSuperiorityPoints4TeamObject(info['victimID'])
    obj_pts = info.get('points', sup_points)
    self.onTeamObjectDestruction(info['killerID'], info['victimID'], victim_data['settings'].type, victim_data['teamIndex'], obj_pts, sec_points)

    player = BigWorld.player()
    if player is None:
        return

    if info['killerID'] == player.id and str(g_in_attack_sector) == 'False':
        obj_name = victim_data['settings'].name
        pts_delta = 0

        if obj_name == 'HUD_SMALL_OBJECT':
            pts_delta = 15
            g_battle_stats['small_object'] += 1
            refresh_hud_field('small_object')
        elif obj_name == 'HUD_SMALL_ARMORED_OBJECT':
            pts_delta = 20
            g_battle_stats['small_object'] += 1
            refresh_hud_field('small_object')
        elif obj_name == 'HUD_MEDIUM_OBJECT':
            pts_delta = 20
            g_battle_stats['medium_object'] += 1
            refresh_hud_field('medium_object')
        elif obj_name == 'HUD_MEDIUM_ARMORED_OBJECT':
            pts_delta = 30
            g_battle_stats['medium_object'] += 1
            refresh_hud_field('medium_object')
        elif obj_name == 'HUD_HEAVY_ARMORED_OBJECT':
            pts_delta = 50
            g_battle_stats['hevy_object'] += 1
            refresh_hud_field('hevy_object')
        elif obj_name == 'HUD_CONTROL_TOWER_OBJECT':
            pts_delta = 35
            g_battle_stats['medium_object'] += 1
            refresh_hud_field('medium_object')
        elif obj_name == 'HUD_RADAR_TOWER_OBJECT':
            pts_delta = 50
            g_battle_stats['hevy_object'] += 1
            refresh_hud_field('hevy_object')
        elif obj_name in ('HUD_COMMAND_OBJECT', 'HUD_ARMORED_WORKSHOP_OBJECT'):
            pts_delta = 80
            g_battle_stats['special_object'] += 1
            refresh_hud_field('special_object')
        elif obj_name == 'OBJECT_NAME_BATTLESHIP':
            ac_type = victim_data.get('ACType', 0)
            if ac_type == 5:
                pts_delta = 20
            elif ac_type == 8:
                pts_delta = 15
            g_battle_stats['small_object'] += 1
            refresh_hud_field('small_object')
        elif obj_name == 'OBJECT_NAME_RLS STOREHOUSE':
            g_battle_stats['small_object'] += 1
            refresh_hud_field('small_object')

        if pts_delta > 0 or obj_name in ('HUD_SMALL_OBJECT', 'HUD_SMALL_ARMORED_OBJECT', 'HUD_MEDIUM_OBJECT',
                                         'HUD_MEDIUM_ARMORED_OBJECT', 'HUD_HEAVY_ARMORED_OBJECT',
                                         'HUD_CONTROL_TOWER_OBJECT', 'HUD_RADAR_TOWER_OBJECT',
                                         'HUD_COMMAND_OBJECT', 'HUD_ARMORED_WORKSHOP_OBJECT',
                                         'OBJECT_NAME_BATTLESHIP', 'OBJECT_NAME_RLS STOREHOUSE'):
            g_battle_stats['objects'] += 1
            refresh_hud_field('objects')
            if pts_delta > 0:
                g_battle_stats['points_cap'] += pts_delta
                g_battle_stats['points_cap_attack'] += pts_delta
                g_battle_stats['points_ground'] += pts_delta
                refresh_hud_field('points_cap')
                refresh_hud_field('points_cap_attack')
                refresh_hud_field('points_ground')

def hook_set_partStates(self, oldPartStates):
    """Monitor subsystem states to detect anti-aircraft gun destruction."""
    result = _orig_set_partStates(self, oldPartStates)
    player = BigWorld.player()
    if player is None or player.id != getattr(self, 'lastDamagerID', None):
        g_part_states_cache[self.id] = dict(getattr(self, 'partStates', {}))
        return result

    gun_part = getattr(getattr(self, '_settings', None), 'partsSettings', None)
    if gun_part:
        part_desc = gun_part.getPartByName('gun_1')
        if part_desc:
            pid = part_desc.partId
            current_states = dict(self.partStates)
            if self.id not in g_part_states_cache:
                if current_states.get(pid) == 2:
                    g_battle_stats['aagun'] += 1
                    refresh_hud_field('aagun')
            else:
                old_states = g_part_states_cache[self.id]
                if old_states.get(pid) == 1 and current_states.get(pid) == 2:
                    g_battle_stats['aagun'] += 1
                    refresh_hud_field('aagun')

    g_part_states_cache[self.id] = dict(getattr(self, 'partStates', {}))
    return result

def hook_onChangeSector(self, avatar, oldSector, newSector):
    """Update current player sector tracker."""
    _orig_onChangeSector(self, avatar, oldSector, newSector)
    player = BigWorld.player()
    if player is not None and avatar is not None and player.id == avatar.id:
        g_battle_stats['sector'] = str(newSector)
        refresh_hud_field('sector')

def hook_onSectorStateChanged(self, sectorId, oldState, oldTeamIndex, state, teamIndex, nextStateTimestamp, *args, **kwargs):
    """Trigger sector attack/defense alert timer when sector ownership changes."""
    player = BigWorld.player()
    if player is not None and getattr(player, 'currentSector', None) == sectorId:
        my_team = player.teamIndex
        enemy_team = 1 - my_team
        neutral_team = 3
        if (oldTeamIndex in (neutral_team, enemy_team)) and teamIndex == my_team and str(oldState) == 'C' and str(state) == 'L':
            set_in_attack_sector('True')
            t = Timer(0.2, set_in_attack_sector, ['False'])
            t.start()
    _orig_onSectorStateChanged(self, sectorId, oldState, oldTeamIndex, state, teamIndex, nextStateTimestamp, *args, **kwargs)

def hook_set_stateContainer(self, oldValue):
    """Hook for ACSector state container modification."""
    _orig_set_stateContainer(self, oldValue)

def hook_save_video_mode(self, value):
    """Reconstruct HUD window upon video settings or resolution change."""
    _orig_save_video_mode(self, value)
    t = Timer(2, destroy_hud_window)
    t.start()

def hook_eAvatarHealthChanged(self, id, health, lastDamager, oldHealth, maxHealth):
    """Accumulate combat damage dealt to enemy aircraft and ground installations."""
    try:
        _orig_eAvatarHealthChanged(self, id, health, lastDamager, oldHealth, maxHealth)
        target = BigWorld.entities.get(id, None)
        player = BigWorld.player()
        if target is not None and player is not None:
            my_team = player.teamIndex
            enemy_team = 1 - my_team
            neutral_team = 3
            if getattr(target, 'lastDamagerID', None) == player.id:
                if isAvatar(target):
                    if target.teamIndex == enemy_team:
                        if health < oldHealth:
                            g_battle_stats['damage_air'] += (oldHealth - health)
                            refresh_hud_field('damage_air')
                    elif target.teamIndex == neutral_team or health < oldHealth:
                        g_battle_stats['damage_ally'] += (oldHealth - health)
                        refresh_hud_field('damage_ally')
                elif health < oldHealth:
                    g_battle_stats['damage_ground'] += (oldHealth - health)
                    refresh_hud_field('damage_ground')
    except Exception:
        pass

def hook_onUpdateHealth(self, health, lastDamagerID, oldValue):
    """Update damage log HUD element when player avatar receives incoming damage."""
    _orig_onUpdateHealth(self, health, lastDamagerID, oldValue)
    if health >= oldValue:
        return

    player = BigWorld.player()
    if player is None:
        return

    damager = BigWorld.entities.get(lastDamagerID, None)
    if damager is None:
        class _DummyEntity(object):
            objectName = 0
            localizedName = 0
            planeID = 0
        damager = _DummyEntity

    damage_reasons = {
        0: 'DESTRUCTION',
        1: 'RAMMING',
        2: 'FIRING',
        3: 'BULLET',
        4: 'OBSTACLE',
        5: 'TERRAIN',
        6: 'WATER',
        7: 'COMMON_EXPLOSION',
        8: 'ROCKET_EXPLOSION',
        9: 'BOMB_EXPLOSION',
        10: 'REPAIRING',
        11: 'AA_GUN',
        12: 'NONE',
        13: 'TREES',
        14: 'AC_ROCKET_V2_EXPLOSION',
        15: 'AC_SECTOR_CAPTURE_SUICIDE'
    }

    if lastDamagerID == 0:
        reason_id = getattr(player, 'lastDamageReason', -1)
        reason_str = damage_reasons.get(reason_id, 'UNKNOWN')
        log_entry = '%s\n' % reason_str
    else:
        obj_name = str(getattr(damager, 'objectName', ''))
        if 'HUD' in obj_name:
            obj_name = obj_name.replace('HUD_', '').replace('FIGHTER', 'F').replace('HAVY', 'H')
        if '<' in obj_name and '>' in obj_name:
            obj_name = Helpers.namesHelper.getBotName(getattr(damager, 'objectName', ''), getattr(damager, 'planeID', 0))
        log_entry = '%s %s\n' % (str(getattr(damager, 'localizedName', '')), obj_name)

    global g_damage_log_timer
    if getattr(player, 'lastDamageReason', -1) == 12:
        g_battle_stats['dmg_log'] = u''
    else:
        g_battle_stats['dmg_log'] = log_entry

    refresh_hud_field('dmg_log')

    if g_damage_log_timer is not None:
        g_damage_log_timer.cancel()
    g_damage_log_timer = Timer(3, clear_damage_log)
    g_damage_log_timer.start()

def hook_onPlayerAvatarStateChanged(self, oldState, state):
    """Handle camera/player avatar state transitions."""
    _orig_onPlayerAvatarStateChanged(self, oldState, state)
    if g_hud_window is None:
        create_hud_window()
    update_hud_dead_position()
    update_hud_visibility()

# ==============================================================================
# Backward-Compatibility Aliases
# ==============================================================================

i11iiiIIIi = get_ntp_timestamp
IIii1i = check_license_validity
IIiiii11I1IIi = load_config
I1i1i111 = hook_refreshBattleLogPoints
II1II = hook_onAvatarDestroyed
II11IIiiiI = hook_doLeaveWorld
i1iII = cycle_mod_mode
IiIIiIi1i1Ii1 = hook_onTeamObjectDestruction
IiIIiIi = hook_set_partStates
i11I1I111i1Iii1 = update_hud_display_values
ii11I1iI111 = refresh_hud_field
IiI1IIiiiI = update_all_hud_texts_and_shadows
i1iIIIIi = create_hud_window
i1i1 = destroy_hud_window
IIIIIii1I1iIiI = reset_battle_stats
IiiiI1Ii = update_hud_visibility
Ii1I11iiIii = on_player_state_updated
Ii1iiI1I = update_hud_dead_position
Ii11iiii11 = reposition_hud_window
i1II1 = hook_onChangeSector
iI111I = hook_onSectorStateChanged
Iii11II11iIi11 = hook_set_stateContainer
Ii1I1iiI1I1i1 = set_in_attack_sector
i1i = on_key_event
iIii1ii1iI = create_text_shadows
IiI1I1I1IiiIIi = hook_save_video_mode
III11iIiiiIII1i = hook_eAvatarHealthChanged
iII11ii1i1 = hook_onUpdateHealth
iIiiiII1 = clear_damage_log
iiI1IiiI1i111I = hook_onPlayerAvatarStateChanged

# Global variable aliases
iIiiiI = g_battle_stats
iiiiiIiiI1i = g_hud_window
IIiIIIi1I = g_hud_elements
IiI11i11IiI11 = g_hud_icons
IIiII11 = NTP_SERVERS
Iii11IiIIiI = CONFIG_PATH_DEFAULT

# ==============================================================================
# Mod Entry Point & Hook Registration
# ==============================================================================

load_config()

try:
    if check_license_validity():
        GlobalEvents.onKeyEvent += on_key_event
        gui.hud.HUD.doLeaveWorld = hook_doLeaveWorld
        clientEconomics.ClientEconomic.refreshBattleLogPoints = hook_refreshBattleLogPoints
        CombatLogSource.onAvatarDestroyed = hook_onAvatarDestroyed
        ClientArena.ClientArena._ClientArena__onTeamObjectDestruction = hook_onTeamObjectDestruction
        TeamObject.TeamObject.set_partStates = hook_set_partStates
        gui.HUD2.features.Sectors.CurretntSectorSource.CurrentSectorSource._onChangeSector = hook_onChangeSector
        gui.HUD2.features.Sectors.SectorSource.SectorSource._onSectorStateChanged = hook_onSectorStateChanged
        ACSector.ACSector.set_stateContainer = hook_set_stateContainer
        EntitySource._eAvatarHealthChanged = hook_eAvatarHealthChanged
        gui.HUD2.features.Player.PlayerSource.PlayerSource._onUpdateHealth = hook_onUpdateHealth
        gui.Scaleform.GameOptions.preservers.GraphicSettingsPreserver.VideoModePreserver.save = hook_save_video_mode
        Camera.Camera.onPlayerAvatarStateChanged = hook_onPlayerAvatarStateChanged
except Exception:
    pass
