#  Switcher, a tool for managing graphics and keymap profiles in games.
#  Copyright (C) 2020 Sam McCormack
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.


def get_layout() -> str:
    return f"res/layout/main_window.ui"


def get_plugin_item_layout() -> str:
    return f"res/layout/plugin_item.ui"


def get_profile_item_layout() -> str:
    return f"res/layout/profile_item.ui"


def get_manage_plugins_layout() -> str:
    return f"res/layout/manage_plugins.ui"


def get_update_dialog_layout() -> str:
    return f"res/layout/update_dialog.ui"


def get_create_plugin_dialog_layout() -> str:
    return f"res/layout/create_plugin_dialog.ui"


def get_settings_layout() -> str:
    return f"res/layout/settings_dialog.ui"
