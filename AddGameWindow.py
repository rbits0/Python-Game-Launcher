from typing import Optional
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from add_game_screens.ManualAddGameScreen import ManualAddGameScreen

class AddGameWindow(QMainWindow):
    def __init__(self, library: list[dict], config: dict, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.listWidget = QListWidget(self)
        listItemManual = QListWidgetItem(QIcon.fromTheme('edit'), 'Manual')
        # TODO: Add steam and heroic icons
        listItemSteam = QListWidgetItem(QIcon.fromTheme('edit'), 'Steam')
        listItemHeroic = QListWidgetItem(QIcon.fromTheme('edit'), 'Heroic')
        
        self.listWidget.addItem(listItemManual)
        self.listWidget.addItem(listItemSteam)
        self.listWidget.addItem(listItemHeroic)
        
        self.stackedWidget = QStackedWidget(self)
        self.manualAddGameWidget = ManualAddGameScreen(library, config, self.parent().refresh)
        self.stackedWidget.addWidget(self.manualAddGameWidget)
        
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.listWidget)
        self.layout.addWidget(self.stackedWidget)
        
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.layout)
        self.setCentralWidget(self.centralWidget)