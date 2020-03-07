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
from typing import Tuple

from api.Keys import Keys
from api.Platform import Platform
from api.Plugin import Plugin
from api.files import _copyfiles
from api.profiles import Profile, ProfileType


class CodelessPlugin(Plugin):
    """
    Plugin class which implements a "codeless" plugin with no custom code.

    Codeless plugins only require a YAML file to define their functionality.
    """

    def __init__(self, platform: Platform, path: str):
        self.here = lambda: path
        super(CodelessPlugin, self).__init__(platform)

    def initialise(self) -> None:
        graphics: bool = self.get_path(Keys.GRAPHICS_CONFIG)
        keymap: bool = self.get_path(Keys.KEYMAP_CONFIG)
        saves: bool = self.get_path(Keys.SAVES_FOLDER)

        error_msg = (
            "Codeless plugins must define at least the location of the graphics config,"
            " the keymap config or the game saves."
        )

        assert graphics or keymap or saves, error_msg

    def save(self, profile: Profile, path: str) -> None:
        self.save_profile_yaml(profile, path)
        game = self.game_path

        for p in self._get_profile_types(profile):
            if p is ProfileType.GRAPHICS:
                if graphics := self.get_path(Keys.GRAPHICS_CONFIG):
                    _copyfiles(game, path, graphics, creating_profile=True)

            elif p is ProfileType.KEYMAPS:
                if keymap := self.get_path(Keys.KEYMAP_CONFIG):
                    _copyfiles(game, path, keymap, creating_profile=True)

            elif p is ProfileType.GAME_SAVES:
                if saves := self.get_path(Keys.SAVES_FOLDER):
                    _copyfiles(game, path, saves, creating_profile=True)

    def apply(self, profile: Profile, path: str) -> None:
        game = self.game_path

        for p in self._get_profile_types(profile):
            if p is ProfileType.GRAPHICS:
                if graphics := self.get_path(Keys.GRAPHICS_CONFIG):
                    _copyfiles(path, game, graphics, creating_profile=False)

            elif p is ProfileType.KEYMAPS:
                if keymap := self.get_path(Keys.KEYMAP_CONFIG):
                    _copyfiles(path, game, keymap, creating_profile=False)

            elif p is ProfileType.GAME_SAVES:
                if saves := self.get_path(Keys.SAVES_FOLDER):
                    _copyfiles(path, game, saves, creating_profile=False)

    def _get_profile_types(self, profile: Profile) -> Tuple[ProfileType]:
        profile_type = profile.feature.types
        if isinstance(profile_type, ProfileType):
            profile_type = (profile_type,)

        return profile_type
