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
import os
import shutil
from os.path import join
from typing import List

from api.Keys import Keys
from api.Platform import Platform
from api.Plugin import Plugin
from api.Profile import Profile


class CodelessPlugin(Plugin):
    """
    Plugin class which implements a "codeless" plugin with no custom code.

    Codeless plugins only require a YAML file to define their functionality.
    """

    def __init__(self, platform: Platform, path: str):
        self.here = lambda: path
        super(CodelessPlugin, self).__init__(platform)

    def initialise(self) -> None:
        graphics: bool = self.get(Keys.GRAPHICS_CONFIG)
        keymap: bool = self.get(Keys.KEYMAP_CONFIG)
        saves: bool = self.get(Keys.SAVES_FOLDER)

        error_msg = (
            "Codeless plugins must define at least the location of the graphics config,"
            " the keymap config or the game saves."
        )

        assert graphics or keymap or saves, error_msg

    def save_graphics_profile(self, abs_path: str) -> Profile:
        game = self.game_path
        graphics = self.get(Keys.GRAPHICS_CONFIG)

        uuid = self.uuid()

        _from = join(game, graphics)
        _to = join(abs_path, uuid)

        os.mkdir(_to)
        shutil.copyfile(_from, _to)

        return Profile("New profile", uuid)

    def list_graphics_profiles(self, abs_path: str) -> List:
        pass
