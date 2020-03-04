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
from enum import Enum
from typing import List, Tuple, Dict


class ProfileType(Enum):
    GRAPHICS = "graphics"
    KEYMAPS = "keymaps"
    GAME_SAVES = "saves"

    @staticmethod
    def all() -> Tuple["ProfileType", ...]:
        return ProfileType.GRAPHICS, ProfileType.KEYMAPS, ProfileType.GAME_SAVES

    @staticmethod
    def get(value: str) -> "ProfileType":
        for v in ProfileType.all():
            if v.value == value:
                return v

        return None


class Profile:
    def __init__(self, name: str = None, uuid: str = None, feature: "Feature" = None):
        self.uuid = uuid
        self.name = name

        self.feature = feature

    def rename(self, new_name: str) -> None:
        self.name = new_name

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "uuid": self.uuid,
            "features": self.feature.to_strings(),
        }

    @staticmethod
    def from_dict(dict: Dict) -> "Profile":
        name = dict.get("name")
        uuid = dict.get("uuid")
        features = dict.get("features")

        return Profile(name, uuid, Feature.from_strings(features))

    @staticmethod
    def create(name: str, feature: "Feature") -> "Profile":
        import uuid

        uuid = str(uuid.uuid4())

        if not name:
            name = "New profile"

        return Profile(name, uuid, feature)


class Feature:
    @staticmethod
    def create(profile_types: List[ProfileType]):
        strings = []
        for f in profile_types:
            spl = [s.rstrip() for s in f.value.split(" ")]
            assert spl, "Plugin defines no features."

            strings.append(spl[0])

        if len(strings) == 1:
            return SingleFeature(ProfileType.get(strings[0]))
        else:
            types = [ProfileType.get(v) for v in strings]
            return ComboFeature(*types)

    def to_strings(self) -> List[str]:
        out = []

        types = self.types
        if not isinstance(types, tuple):
            types = (types,)

        for t in types:
            out.append(t.value)

        return out

    @staticmethod
    def from_strings(strings: List[str]) -> "Feature":
        types = []
        for s in strings:
            types.append(ProfileType.get(s))

        return Feature.create(types)


class SingleFeature(Feature):
    def __init__(self, type: ProfileType):
        super().__init__()
        self.types = type


class ComboFeature(Feature):
    def __init__(self, *types: ProfileType):
        super().__init__()
        self.types = types
