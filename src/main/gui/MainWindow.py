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
from PyQt5 import uic, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import QMainWindow

from src.main import resources
from src.main.gui.MainGUI import MainGUI
from src.main.gui.PluginItem import PluginItem


class MainWindow(MainGUI, QMainWindow):
    """
    The main window of the application.
    """

    def __init__(self, application):
        MainGUI.__init__(self)
        QMainWindow.__init__(self)

        self.application = application
        self.handler = application.handler

        self.handler.initialise()
        self.setup_ui()

    def setup_ui(self) -> None:
        uic.loadUi(resources.get_layout(), self)
        # self.listwidget_plugins.setGraphicsEffect(QGraphicsBlurEffect())
        # self.listwidget_plugins.setStyleSheet(
        r"""
        QListWidget {
        background-color: transparent;
        border: none;
        }
        
        QListWidget::item {
        background-color:green;
        }
        
        QListWidget::item::hover {
        background-color:orange;
        }
        
        # 
        # QListWidget::item::selected {
        # background-color:red;
        # }
        """
        # )
        self.left.setAlignment(Qt.AlignTop)

        for p in self.handler.plugins:
            # item = QListWidgetItem(self.listwidget_plugins)
            # self.listwidget_plugins.addItem(item)

            w = PluginItem(p.get_name())
            height = 215
            width = 460
            w.setFixedHeight(height)
            w.setFixedWidth(width)
            # w.setStyleSheet("background-color:green;")
            # item.setSizeHint(w.minimumSizeHint())

            # self.listwidget_plugins.setItemWidget(item, w)
            self.left.addWidget(w)
            # self.left.setAlignment(w, Qt.AlignTop)

        # self.centralWidget().setStyleSheet("border-image: url(\"plugins/banner.jpg\") 0 0 0 0 stretch stretch; background-position: center; ")
        # # background-image: url("E:\Files\Projects\Pycharm\profile-switcher\plugins\warthunder\banner.jpg");

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        backgrnd = QPixmap(
            "E:\\Files\\Projects\\Pycharm\\profile-switcher\\plugins\\warthunder\\background.png"
        )
        backgrnd = backgrnd.scaled(self.size(), Qt.KeepAspectRatioByExpanding)
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(backgrnd))
        # self.setPalette(palette)
