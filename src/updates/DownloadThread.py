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
from os.path import join
from urllib.request import urlopen

from PyQt5.QtCore import QThread, pyqtSignal
from github.GitRelease import GitRelease

from api import files
from api.Platform import Platform
from updates import checksum
from updates.UpdateHandler import parse_checksum
from utils import online


class DownloadThread(QThread):
    signal_download_started = pyqtSignal()
    signal_download_progress = pyqtSignal(float)
    signal_installer_name = pyqtSignal(str)
    signal_verify_started = pyqtSignal()
    signal_verify_finished = pyqtSignal(bool)
    signal_installer_path = pyqtSignal(str)

    def __init__(self, *args):
        super(DownloadThread, self).__init__(*args)
        self.installer_folder = files.installer_path()

    def run(self, priority=None) -> None:
        # Get latest release.
        releases = online.get_switcher_releases()
        release: GitRelease = releases[0]

        assets = release.raw_data["assets"]
        platform = Platform.get()

        # Get details for platform-specific installer.
        if platform is Platform.WINDOWS:
            installer = [a for a in assets if a["name"].endswith(".exe")][0]
            name = installer["name"]
            url = installer["browser_download_url"]
            size = installer["size"]
        else:
            raise NotImplementedError(
                f"Platform {platform} cannot download updates at this time."
            )

        tag = release.tag_name

        # Emit signal so dialog shows which installer is being downloaded.
        self.signal_installer_name.emit(tag)
        self.signal_download_started.emit()

        # Download installer.
        location: str = self.download_release(tag, url, name, size)

        _checksum = parse_checksum(release.body, name)

        self.signal_verify_started.emit()
        verified = self.verify_installer(location, _checksum)
        self.signal_verify_finished.emit(verified)

        if verified:
            self.signal_installer_path.emit(location)

    def verify_installer(self, location: str, expected_checksum: str) -> bool:
        real_checksum = checksum.sha256sum(location)
        return expected_checksum == real_checksum

    def download_release(self, tag: str, url: str, filename: str, size: int):
        target_dir = join(self.installer_folder, tag)
        os.makedirs(target_dir, exist_ok=True)

        filepath = join(target_dir, filename)

        with urlopen(url) as response:
            with open(filepath, "wb") as f:
                bytes = 0
                bs = 1024 * 10

                while True:
                    buffer = response.read(bs)
                    if not buffer:
                        break

                    f.write(buffer)
                    bytes += bs

                    self.signal_download_progress.emit(bytes / size)

        return filepath
