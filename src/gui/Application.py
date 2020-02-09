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
import time

from PyQt5.QtWidgets import QApplication

from gui.MainWindow import MainWindow
from src.api.PluginHandler import PluginHandler


class Application(QApplication):
    def __init__(self, argv):
        super(Application, self).__init__(argv)
        self.plugin_handler = PluginHandler()

    def launch(self) -> None:
        self.window = MainWindow(self)
        self.window.show()

    def restart(self):
        self.plugin_handler = PluginHandler()
        self.window.close()

        time.sleep(0.5)
        self.launch()
