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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QWidget, QTableView
from qasync import asyncSlot
from scheduler.Scheduler import Scheduler

from src.main import resources, online
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
        self.btn_plugins.clicked.connect(self.coro_get_plugins)

        self.left.setAlignment(Qt.AlignTop)
        for p in self.handler.plugins:
            w = PluginWidget(p)
            self.left.insertWidget(0, w)

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

    @asyncSlot()
    async def coro_get_plugins(self):
        self.scheduler = Scheduler()
        self.scheduler.add(target=online.find_online_plugins)

        right = QWidget(self)
        uic.loadUi(resources.get_manage_plugins_layout(), right)
        self.right.addWidget(right)

        self.tbl1: QTableView = right.tbl_trusted
        self.tbl2: QTableView = right.tbl_community
        right.btn_apply.clicked.connect(self.on_apply_clicked)

        model = QStandardItemModel()
        model.itemChanged.connect(self.on_item_changed)
        model.setHorizontalHeaderLabels(["Game", "Author", "Install"])
        for t in (self.tbl1, self.tbl2):
            t.verticalHeader().setVisible(False)
            t.setModel(model)

        trusted, community = (await self.scheduler.run())[0]

        for p in trusted + community:
            print(p.description)
            checkbox = QStandardItem(True)
            checkbox.setCheckable(True)
            checkbox.setCheckState(Qt.Checked)
            checkbox.setText("Installed")
            checkbox.checkState()

            model.appendRow(
                [QStandardItem(p.game), QStandardItem(p.owner.login), checkbox]
            )

        self.tbl1.resizeColumnsToContents()
        self.tbl2.resizeColumnsToContents()

    def on_apply_clicked(self):
        pass

    def on_item_changed(self, item):
        print("Changed")

    def resize_plugin_widgets(self):
        window_height = self.height()
        count = max(5, len(self.plugin_widgets))

        widget_height = window_height / count

        cap = 250
        if widget_height > cap:
            widget_height = cap

        for w in self.plugin_widgets:
            _width, _height = w.exact_size

            aspect_ratio = _width / _height
            widget_width = widget_height * aspect_ratio

            w.setFixedHeight(widget_height)
            w.setFixedWidth(widget_width)

            w.exact_size = (widget_width, widget_height)
            asyncio.ensure_future(w.coro_initialise())

            self.btn_plugins.setFixedWidth(widget_width)
