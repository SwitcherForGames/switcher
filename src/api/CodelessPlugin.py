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
from typing import Union, Iterable, Tuple

from api.Keys import Keys
from api.Platform import Platform
from api.Plugin import Plugin
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
        graphics: bool = self.get(Keys.GRAPHICS_CONFIG)
        keymap: bool = self.get(Keys.KEYMAP_CONFIG)
        saves: bool = self.get(Keys.SAVES_FOLDER)

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
                if graphics := self.get(Keys.GRAPHICS_CONFIG):
                    self._copyfile(game, path, graphics)

            elif p is ProfileType.KEYMAPS:
                if keymap := self.get(Keys.KEYMAP_CONFIG):
                    self._copyfile(game, path, keymap)

            elif p is ProfileType.GAME_SAVES:
                raise NotImplementedError("Game saves are not implemented yet!")

    def apply(self, profile: Profile, path: str) -> None:
        game = self.game_path

        for p in self._get_profile_types(profile):
            if p is ProfileType.GRAPHICS:
                if graphics := self.get(Keys.GRAPHICS_CONFIG):
                    self._copyfile(path, game, graphics)

            elif p is ProfileType.KEYMAPS:
                if keymap := self.get(Keys.KEYMAP_CONFIG):
                    self._copyfile(game, path, keymap)

            elif p is ProfileType.GAME_SAVES:
                raise NotImplementedError("Game saves are not implemented yet!")

    def _get_profile_types(self, profile: Profile) -> Tuple[ProfileType]:
        profile_type: Union[ProfileType, Iterable[ProfileType]] = profile.feature.types
        if isinstance(profile_type, ProfileType):
            profile_type = (profile_type,)

        return profile_type

    def _copyfile(self, from_path: str, to_path: str, relative_path: str) -> None:
        _from = join(from_path, relative_path)
        _to = join(to_path, relative_path)

        try:
            folder, _ = os.path.split(_to)
            os.makedirs(folder)
        except FileExistsError:
            pass

        shutil.copyfile(_from, _to)
        print(f"Copied file {_from} to {_to}")
