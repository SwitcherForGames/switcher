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
import inspect
import logging
import os
import shutil
import subprocess
import uuid
from abc import ABC, abstractmethod
from os import path
from typing import Dict, Optional, final, List, Any

import requests
import yaml

from api import files
from api.Keys import Keys
from api.Launcher import Launcher
from api.Platform import Platform
from api.profiles import ProfileType, Profile


class Plugin(ABC):
    """
    Abstract plugin class which will be inherited from by plugin implementations.
    """

    def __init__(self, platform: Platform):
        super(Plugin, self).__init__()
        self.platform = platform
        self.yaml = self.load_yaml()
        self.initialise()

        self.game_path: str = None

    @abstractmethod
    def initialise(self) -> None:
        """
        Called every time the plugin is imported.
        """
        pass

    def verify(self, folder_path: str) -> bool:
        r"""
        Verify whether a particular (absolute) file path belongs to the game handled by this plugin.

        This should return True when the full path to the folder containing the game is supplied as a parameter.
        For example, "D:\Program Files\SteamLibrary\steamapps\common\War Thunder" would return True for a
        War Thunder plugin but "D:\Program Files\SteamLibrary\steamapps\common\War Thunder\win64" should not.

        :param folder_path: the path to the folder being examined
        :return: whether the path belongs to the desired game
        """
        paths = self.get(Keys.VERIFICATION_PATHS)
        assert paths, (
            "Verification paths have not been defined. These are required to check if the game exists at a "
            "location. "
        )
        return all([os.path.exists(os.path.join(folder_path, p)) for p in paths])

    def save(self, profile: Profile, path: str) -> None:
        """
        Saves a profile for the current settings.

        :param profile: the profile to save
        :param path: a unique path, belonging only to this particular profile, to which the profile will be saved
        """
        self.save_profile_yaml(profile, path)

    def apply(self, profile: Profile, path: str) -> None:
        """
        Applies a profile. This will overwrite the current game settings with the settings from the profile.

        :param profile: the profile to apply
        :param path: the path to the profile
        """
        print(f"Applying profile '{profile.name}' from {path}...")

    def delete(self, profile: Profile, path: str) -> None:
        """
        Deletes a profile.

        :param profile: the profile to delete
        :param path: the path to the profile
        """
        print(f"Deleting profile at {path}...")
        shutil.rmtree(path)

    def save_profile_yaml(self, profile: Profile, path: str) -> None:
        """
        Saves the YAML file for a profile.
        """
        out = profile.to_dict()
        with open(os.path.join(path, "profile.yaml"), "w") as f:
            yaml.safe_dump(out, f)

    def load_profile_yaml(self, path: str) -> Profile:
        """
        Loads the YAML file for a profile.
        """
        try:
            with open(os.path.join(path, "profile.yaml"), "r") as f:
                return Profile.from_dict(yaml.safe_load(f))
        except (FileNotFoundError, AttributeError) as e:
            _, tail = os.path.split(path)
            return Profile(uuid=tail)

    def get_profiles(self, profile_dir: str) -> List[Profile]:
        """
        Returns a list of the profiles which have been saved.
        """
        profiles = []

        for folder in os.listdir(profile_dir):
            profile = self.load_profile_yaml(os.path.join(profile_dir, folder))
            profiles.append(profile)

        return profiles

    def get_executable(self) -> str:
        """
        :return: the path to the executable which launches the game
        """
        pass

    def load_yaml(self) -> Dict:
        """
        Loads the plugin's YAML file and returns a dictionary with the parsed contents.

        :return: dictionary containing the keys and values from the YAML file
        """
        folder_location = self.here()
        yaml_location = path.join(folder_location, "plugin.yaml")

        with open(yaml_location, "r") as stream:
            return yaml.safe_load(stream)

    @final
    async def get_header(self) -> Optional[str]:
        """
        Gets the path to the  header image. If it needs to be downloaded, it will download the image first.

        :return: the absolute file path to the header image
        """
        items = os.listdir(self.here())
        stripped = [path.splitext(i)[0] for i in items]
        header = "header"

        # Check if header already exists.
        if header in stripped:
            name = items[stripped.index(header)]
            return path.join(self.here(), name)

        return await self._download_header()

    async def _download_header(self) -> Optional[str]:
        """
        Downloads the header image. By default it will use the image from the Steam page.

        :return: the absolute file path to the downloaded header image
        """
        steam_id = int(self.get(Keys.STEAM_ID))
        if not steam_id:
            return None

        url = f"http://cdn.akamai.steamstatic.com/steam/apps/{steam_id}/header.jpg"
        return self._perform_download(url, "header")

    def _perform_download(self, url: str, filename: str, ext: str = "jpg") -> str:
        logging.info(f"Downloading header image from {url} as {filename}")
        data = requests.get(url).content
        filepath = f"{path.join(self.here(), filename)}.{ext}"
        with open(filepath, "wb") as handler:
            handler.write(data)

        return filepath

    def get(self, key: Keys) -> Optional[Any]:
        """
        Gets the value of an item from the YAML file.

        :param key: the key for the item, as a Keys enum
        :return: the value if it exists, or None if it does not exist
        """
        return self.yaml.get(key.value)

    def get_path(self, key: Keys) -> Optional[Any]:
        """
        Gets the value of a path from the YAML file. This evaluates any variables in the path.

        :param key: the key for an item, as a Keys enum
        :return: the path, after evaluating it to replace any variables
        """
        return files.evaluate_path(self.get(key))

    def launch_game(self, launcher: Launcher) -> bool:
        """
        Launches a game with a specified launcher.

        :param launcher: the launcher to use
        :return: whether the game was launched successfully
        """
        if launcher is Launcher.STEAM:
            steam = "C:'/Program Files (x86)'/Steam/Steam.exe"

            id = self.get(Keys.STEAM_ID)

            # Important security check to guard against malicious injection.
            assert id == int(str(int(id)))

            uri = f"steam://rungameid/{id}"
            subprocess.Popen(
                ["powershell", "-c", steam, uri],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            return True
        elif launcher is Launcher.STANDALONE:
            return False

        return False

    def uuid(self) -> str:
        return f"{uuid.uuid4()}"

    @final
    def here(self) -> str:
        """
        Returns the absolute path to the folder containing the current
        plugin class (which should be a subclass of this class).

        NOTE: '__file__' cannot be used because it returns the path to the abstract Plugin class,
        not the desired plugin implementation.
        """
        class_location = inspect.getfile(self.__class__)
        return path.abspath(path.dirname(class_location))

    @final
    def get_features(self) -> List[ProfileType]:
        features = self.get(Keys.FEATURES) or []
        out = []

        for f in features:
            out.append(ProfileType.get(f))

        return out

    @final
    def get_uid(self) -> str:
        return self.get(Keys.UID)

    @final
    def get_name(self) -> str:
        return self.get(Keys.GAME)

    @final
    def get_api_level(self) -> int:
        return self.get(Keys.API_VERSION)

    @final
    def is_windows(self) -> bool:
        return self.platform == Platform.WINDOWS

    @final
    def is_mac(self) -> bool:
        return self.platform == Platform.MAC_OS

    @final
    def is_linux(self) -> bool:
        return self.platform == Platform.LINUX
