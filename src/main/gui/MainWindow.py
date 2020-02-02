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
import asyncio
from typing import List

from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import QMainWindow
from scheduler.Scheduler import Scheduler

from src.main import resources
from src.main.gui.MainGUI import MainGUI
from src.main.gui.PluginWidget import PluginWidget


class MainWindow(MainGUI, QMainWindow):
    """
    The main window of the application.
    """

    def __init__(self, application):
        MainGUI.__init__(self)
        QMainWindow.__init__(self)

        self.plugin_widgets: List[PluginWidget] = []

        self.application = application
        self.handler = application.handler

        self.handler.initialise()
        self.setup_ui()

    def setup_ui(self) -> None:
        uic.loadUi(resources.get_layout(), self)
        self.btn_get_plugins.clicked.connect(self.get_plugins)

        self.left.setAlignment(Qt.AlignTop)
        for p in self.handler.plugins:
            w = PluginWidget(p)
            self.left.addWidget(w)

            self.plugin_widgets.append(w)

        self.resize_plugin_widgets()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        backgrnd = QPixmap(
            "E:\\Files\\Projects\\Pycharm\\profile-switcher\\plugins\\warthunder\\background.png"
        )
        backgrnd = backgrnd.scaled(self.size(), Qt.KeepAspectRatioByExpanding)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(backgrnd))
        # self.setPalette(palette)

        self.resize_plugin_widgets()

    @pyqtSlot()
    def get_plugins(self) -> None:
        pass

    async def coro_get_plugins(self):
        self.scheduler = Scheduler()

    def resize_plugin_widgets(self):
        window_height = self.height()
        count = max(5, len(self.plugin_widgets))

        widget_height = window_height / count
        cap = 250

        for w in self.plugin_widgets:
            _width, _height = w.exact_size
            if widget_height > cap:
                widget_height = cap

            aspect_ratio = _width / _height
            widget_width = widget_height * aspect_ratio

            w.setFixedHeight(widget_height)
            w.setFixedWidth(widget_width)

            w.exact_size = (widget_width, widget_height)

            asyncio.ensure_future(w.coro_initialise())
