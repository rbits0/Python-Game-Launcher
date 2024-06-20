from typing import Optional, Callable
from PySide6.QtWidgets import *
from PySide6.QtCore import * # type: ignore
from PySide6.QtGui import * # type: ignore

from add_game_screens.ManualAddGameScreen import ManualAddGameScreen
from storage import Config, Library

class AddGameWindow(QMainWindow):
    def __init__(
        self,
        library: Library,
        config: Config,
        refreshCallback: Callable[[], None],
        parent: Optional[QWidget] = None,
    ) -> None:
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
        self.manualAddGameWidget = ManualAddGameScreen(library, config, refreshCallback)
        self.stackedWidget.addWidget(self.manualAddGameWidget)
        
        self.mainLayout = QHBoxLayout()
        self.mainLayout.addWidget(self.listWidget)
        self.mainLayout.addWidget(self.stackedWidget)
        
        self.centralWidget_ = QWidget()
        self.centralWidget_.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget_)