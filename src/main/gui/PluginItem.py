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
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import QWidget

from src.main import resources


class PluginItem(QWidget):
    def __init__(self, game: str):
        super(PluginItem, self).__init__()
        uic.loadUi(resources.get_plugin_item_layout(), self)

        self.lbl_name.setText(game)
        # self.setAutoFillBackground(True)
        # self.setStyleSheet(
        #     r"""
        #     background-image: url("E:\Files\Projects\Pycharm\profile-switcher\plugins\warthunder\banner.jpg");
        #     background-repeat:no-repeat;
        #     background-position: center;
        #     """
        # )

        # p = self.palette()
        # p.setColor(self.backgroundRole(), Qt.red)
        # backgrnd = QPixmap("E:\\Files\\Projects\\Pycharm\\profile-switcher\\plugins\\warthunder\\banner.jpg")
        # backgrnd = backgrnd.scaled(self.size(), Qt.IgnoreAspectRatio)
        # palette = QPalette()
        # palette.setBrush(QPalette.Background, QBrush(backgrnd))
        # self.setPalette(palette)

        self.setAutoFillBackground(True)
        backgrnd = QPixmap(
            "E:\\Files\\Projects\\Pycharm\\profile-switcher\\plugins\\warthunder\\header.jpg"
        )
        # backgrnd = backgrnd.scaled(self.size(), Qt.KeepAspectRatioByExpanding)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(backgrnd))
        self.setPalette(palette)
