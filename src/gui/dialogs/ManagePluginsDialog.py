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
from typing import Optional, Dict, List

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QDialog, QTableView
from scheduler.Scheduler import Scheduler

from utils import resources, online


class ManagePluginsDialog(QDialog):
    def __init__(self, parent, installed: List[str]):
        super(ManagePluginsDialog, self).__init__(parent)
        uic.loadUi(resources.get_manage_plugins_layout(), self)

        self.setWindowTitle("Manage plugins")
        self.btn_apply.clicked.connect(self.on_apply_clicked)

        self.installed = installed
        self.changes = {}

        asyncio.ensure_future(self.coro_get_plugins())

    async def coro_get_plugins(self):
        self.scheduler = Scheduler()
        self.scheduler.add(target=online.find_online_plugins)

        self.tbl1: QTableView = self.tbl_trusted
        self.tbl2: QTableView = self.tbl_community
        self.btn_apply.clicked.connect(self.on_apply_clicked)

        self.model1 = QStandardItemModel()
        self.model2 = QStandardItemModel()

        for m in (self.model1, self.model2):
            m.itemChanged.connect(self.on_item_changed)
            m.setHorizontalHeaderLabels(["Install status", "Game", "Author"])

        for t, m in zip([self.tbl1, self.tbl2], [self.model1, self.model2]):
            t.verticalHeader().setVisible(False)
            t.setModel(m)

        trusted, community = (await self.scheduler.run())[0]

        self.add_items(self.model1, trusted)
        self.add_items(self.model2, community)

        self.tbl1.resizeColumnsToContents()
        self.tbl2.resizeColumnsToContents()

    def add_items(self, model, items) -> None:
        for p in items:
            checkbox = QStandardItem(True)
            checkbox.setCheckable(True)
            checkbox.setText("Installed")
            checkbox.url = p.url

            if p.url in self.installed:
                checkbox.setCheckState(Qt.Checked)
            else:
                checkbox.setCheckState(Qt.Unchecked)

            print(p.description)
            model.appendRow([checkbox, QStandardItem(p.game), QStandardItem(p.author)])

    def on_apply_clicked(self) -> None:
        self.accept()

    def get_changes(self) -> Dict:
        return self.changes

    def on_item_changed(self, item) -> None:
        url = self.get_plugin(self.model1, item)
        if not url:
            url = self.get_plugin(self.model2, item)

        install_status = item.checkState() == Qt.Checked
        print(f"Changed installation status for {url} to {install_status}.")

        if self.changes.get(url):
            del self.changes[url]
        else:
            self.changes[url] = install_status

    def get_plugin(self, model, checkbox) -> Optional[str]:
        for i in range(model.rowCount()):
            item = model.item(i, 0)
            if checkbox == item:
                return item.url

        return None
