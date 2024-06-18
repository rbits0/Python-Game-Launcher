import sys
from typing import Optional, NamedTuple
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import qdarktheme

import storage
from storage import Config, Library
from Sidebar import Sidebar
from GameTile import GameTile
from AddGameWindow import AddGameWindow


GameTileInfo = NamedTuple(
    'GameTileInfo',
    [
        ('tile', GameTile),
        ('game', dict),
    ]
)


def main(argv) -> None:
    config = Config()
    library = Library()


    app = QApplication(argv)
    
    qss = '''
    QPushButton {
        border-width: 0px;
    }

    QPushButton:!hover {
        background-color: #2c669ff5;
    }

    QPushButton:hover {
        background-color: #5c669ff5;
    }

    QPushButton:pressed {
        background-color: #9a5796f4;
    }
    
    /* For some reason, this stops the item's text from moving when you hover over it */
    QAbstractItemView::item {
        background-color: #00000000;
    }
    
    '''
    
    qdarktheme.setup_theme(theme='dark', additional_qss=qss)

    window = MainWindow(library, config)
    window.show()

    app.exec()



class MainWindow(QMainWindow):
    def __init__(self, library: Library, config: Config) -> None:
        super().__init__()
        
        self.MAIN_CONTENT_PADDING = 20

        self.runningProcess = None
        self.library = library
        self.config = config
        self.addGameWindow = AddGameWindow(self.library, self.config, self)


        # Sidebar

        testButton1 = {'icon': QIcon.fromTheme('view-sort-ascending-name'), 'text': QStaticText('Alphabetical order')}
        testButton2 = {'icon': QIcon.fromTheme('view-sort-ascending-name'), 'text': QStaticText('Reverse')}
        self.sidebar = Sidebar(None, [testButton1, testButton2])
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self.sidebar.itemSelectionChanged.connect(self.sidebarClicked)
        
        
        # Scroll area with games
        
        self.scrollLayout = QHBoxLayout()
        self.scrollLayout.setContentsMargins(self.MAIN_CONTENT_PADDING, 0, self.MAIN_CONTENT_PADDING, self.MAIN_CONTENT_PADDING)
        scrollMargins = 20
        self.tiles: list[GameTileInfo] = []
        self.defaultImage = QPixmap(600, 900)
        self.defaultImage.fill(Qt.GlobalColor.white)
        self.imageHeight = 450
        self.expandedImageHeight = 540
        for i, game in enumerate(library.games):
            image = storage.getLibraryImage(game['id'])
            if image is None:
                image = self.defaultImage

            tile = GameTile(image, self, self.imageHeight, self.expandedImageHeight)
            tile.clicked.connect(lambda i=i: self.tileClicked(i))
            self.tiles.append(GameTileInfo(tile, game))
            self.scrollLayout.addWidget(tile)
        self.selectedTile = None

        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea = AnimatedScrollArea(self)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setFixedHeight(self.expandedImageHeight + 2 * scrollMargins + 15)
        
        
        # Buttons at the top
        
        settingsButtonSize = 50
        settingsIconSize = int(settingsButtonSize * 0.8)
        self.settingsButton = QPushButton(QIcon.fromTheme('settings'), '')
        self.settingsButton.setFixedSize(settingsButtonSize, settingsButtonSize)
        self.settingsButton.setIconSize(QSize(settingsIconSize, settingsIconSize))
        self.settingsButton.setToolTip('Settings')
        
        self.addGameButton = QPushButton(QIcon.fromTheme('add'), '')
        self.addGameButton.setFixedSize(settingsButtonSize, settingsButtonSize)
        self.addGameButton.setIconSize(QSize(settingsIconSize, settingsIconSize))
        self.addGameButton.setToolTip('Add game')
        self.addGameButton.clicked.connect(self.addGameClicked)

        topBar = QHBoxLayout()
        topBar.addStretch()
        topBar.addWidget(self.addGameButton)
        topBar.addWidget(self.settingsButton)
        topBar.setContentsMargins(0, 10, 10, 0)
        topBar.setSpacing(10)
        
        
        # Game info
        
        self.gameTitle = QLabel("Title")
        font = self.font()
        font.setPointSize(36)
        font.setBold(True)
        self.gameTitle.setFont(font)
        
        self.gameDescription = QLabel("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
        font = self.font()
        font.setPointSize(20)
        self.gameDescription.setFont(font)
        self.gameDescription.setWordWrap(True)
        self.gameDescription.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        self.gameDescription.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.gameDescription.setMaximumHeight(125)
        self.gameDescription.setMinimumWidth(20)
        
        self.playButton = PlayButton('Play', self)
        font = self.font()
        font.setPointSize(24)
        font.setBold(True)
        self.playButton.setFont(font)
        self.playButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.playButton.setMinimumWidth(150)
        self.playButton.setMaximumHeight(75)
        self.playButton.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.playButton.clicked.connect(self.playButtonClicked)
        playButtonLayout = QHBoxLayout()
        playButtonLayout.addWidget(self.playButton)
        playButtonLayout.addStretch()
        
        gameInfoLayout = QVBoxLayout()
        gameInfoLayout.addWidget(self.gameTitle)
        gameInfoLayout.addWidget(self.gameDescription)
        gameInfoLayout.addStretch()
        gameInfoLayout.addLayout(playButtonLayout)
        gameInfoLayout.setContentsMargins(self.MAIN_CONTENT_PADDING, 0, 0, 0)

        
        # Main contents (everything except sidebar)
        
        mainContentsLayout = QVBoxLayout()
        mainContentsLayout.addLayout(topBar)
        mainContentsLayout.addLayout(gameInfoLayout)
        mainContentsLayout.addWidget(self.scrollArea)

        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addLayout(mainContentsLayout)
        layout.setContentsMargins(0, 0, 0, 0)
        

        centralWidget = QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)

        self.tileClicked(0)
        self.scrollArea.setFocus(Qt.FocusReason.OtherFocusReason)
        
        self.setMinimumSize(1000, 875)
        self.resize(1200, 875)
        self.showMaximized()
        # self.showFullScreen()
    
    
    def tileClicked(self, index: int, animate: bool = True) -> None:
        """Select a tile and optionally start the selection animation"""
        
        if index == self.selectedTile:
            return
        if index >= self.scrollLayout.count():
            return

        prevTile = self.tiles[self.selectedTile].tile if self.selectedTile is not None else None
        currTile = self.tiles[index].tile
        
        if animate:
            currTile.growAnimation.start()
            if self.selectedTile is not None:
                prevTile.growAnimation.stop()
                prevTile.shrinkAnimation.start()
            self.scrollArea.ensureWidgetVisibleAnimated(currTile, 200)
        else:
            if self.selectedTile is not None:
                prevTile.imageSize = prevTile.baseImageSize
            currTile.imageSize = currTile.expandedImageSize
            self.scrollArea.ensureWidgetVisible(currTile, 200, 200)
        self.selectedTile = index
        
        self.updateGameInfo()


    def updateGameInfo(self) -> None:
        game = self.tiles[self.selectedTile].game
        self.gameTitle.setText(game['name'])
        if 'description' not in game.keys() or game['description'] is None:
            self.gameDescription.setText('No description')
        else:
            self.gameDescription.setText(game['description'])
        
        if self.runningProcess is not None:
            if game['id'] == self.runningProcess[1]:
                self.playButton.setText('Stop')
            else:
                self.playButton.setText('Play')
    
    
    def playButtonClicked(self) -> None:
        if self.playButton.text() == 'Play':
            game: dict = self.tiles[self.selectedTile].game
            self.launchGame(game)
            self.playButton.setText('Stop')
        else:
            self.runningProcess[0].terminate()

    def launchGame(self, game: dict) -> None:
        if self.runningProcess is not None:
            QMessageBox.warning(self, 'Game already running', 'Please close the running game before you launch another game')
            return

        process = QProcess()

        if game['source'] == 'steam':
            process.start('steam', [f'steam://rungameid/{game["appID"]}'])
        elif game['source'] == 'native':
            if 'args' in game.keys():
                args = game['args']
            else:
                args = []
            process.start(game['filepath'], args)

        self.runningProcess: tuple = (process, game['id'])
        
        process.finished.connect(self.processFinished)
    
    def processFinished(self) -> None:
        self.playButton.setText('Play')
        self.runningProcess = None
    

    def sidebarClicked(self) -> None:
        itemClicked = self.sidebar.currentRow()
        if itemClicked == 0:
            # Ascending alphabetical order
            self.library.games.sort(key=lambda x: x['name'])
        elif itemClicked == 1:
            # Descending alphabetical order
            self.library.games.sort(key=lambda x: x['name'], reverse=True)
        
        self.refresh()

    
    def refresh(self, selectedTile: int = 0) -> None:
        for gameTile in self.tiles:
            self.scrollLayout.removeWidget(gameTile.tile)
            gameTile.tile.deleteLater()
        
        self.tiles: list[GameTileInfo] = []
        
        for i, game in enumerate(self.library.games):
            print(game['name'])
            image = storage.getLibraryImage(game['id'])
            if image is None:
                image = self.defaultImage

            tile = GameTile(image, self, self.imageHeight, self.expandedImageHeight)
            tile.clicked.connect(lambda i=i: self.tileClicked(i))
            self.tiles.append(GameTileInfo(tile, game))
            self.scrollLayout.addWidget(tile)
        
        self.selectedTile = None
        self.tileClicked(selectedTile, animate=False)

        self.scrollLayout.update()
        self.scrollWidget.update()
        self.scrollArea.update()

    
    def addGameClicked(self) -> None:
        self.addGameWindow.show()
    

    def keyPressEvent(self, e: QKeyEvent) -> None:
        match e.key():
            case Qt.Key.Key_Left:
                if not self.sidebar.hasFocus():
                    if self.selectedTile == 0:
                        self.sidebar.setFocus(Qt.FocusReason.OtherFocusReason)
                    else:
                        self.tileClicked(self.selectedTile - 1)
            case Qt.Key.Key_Right:
                if self.sidebar.hasFocus():
                    self.tileClicked(0)
                else:
                    self.tileClicked(self.selectedTile + 1)
                self.scrollArea.setFocus(Qt.FocusReason.OtherFocusReason)
            case Qt.Key.Key_Up:
                if self.scrollArea.hasFocus():
                    self.playButton.setFocus(Qt.FocusReason.OtherFocusReason)
            case Qt.Key.Key_Down:
                if self.playButton.hasFocus():
                    self.scrollArea.setFocus(Qt.FocusReason.OtherFocusReason)
            case Qt.Key.Key_Return:
                if self.scrollArea.hasFocus():
                    self.playButton.click()
            case Qt.Key.Key_L:
                self.playButton.setFocus(Qt.FocusReason.OtherFocusReason)
            case Qt.Key.Key_K:
                print(self.playButton.hasFocus())
                print(self.keyboardGrabber())
        
        return super().keyPressEvent(e)



class PlayButton(QPushButton):
    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == Qt.Key.Key_Return:
            self.click()
        else:
            e.ignore()



class AnimatedScrollArea(QScrollArea):
    def __init__(self, parent: Optional[QWidget] = ...) -> None:
        super().__init__(parent)
        
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.scrollAnimation = QPropertyAnimation(self.horizontalScrollBar(), b'value')
        self.scrollAnimation.setDuration(100)
        self.scrollAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def ensureWidgetVisibleAnimated(self, childWidget: QWidget, xMargin: int = 0, yMargin: int = 0) -> None:
        contentsRect: QRect = childWidget.contentsRect()
        pos = childWidget.pos()
        scrollBarValue: int  = self.horizontalScrollBar().value()
        viewWidth = self.width()
        isLeft = pos.x() < scrollBarValue + xMargin
        
        if isLeft:
            xPos = pos.x() - xMargin
            doScroll = True if xPos < self.horizontalScrollBar().value() else False
        else:
            xPosInLayout = pos.x() + contentsRect.width() + xMargin
            xPos = xPosInLayout - viewWidth
            doScroll = True if xPos > self.horizontalScrollBar().value() else False
        if doScroll:
            self.scrollAnimation.setEndValue(xPos)
            self.scrollAnimation.start()
    
    def wheelEvent(self, e: QWheelEvent) -> None:
        delta = e.angleDelta().y()
        newValue = self.horizontalScrollBar().value() - delta
        
        self.horizontalScrollBar().setValue(newValue)
    
    def keyPressEvent(self, e: QKeyEvent) -> None:
        e.ignore()
        

    @Property(int)
    def xPos(self) -> int:
        return self._xPos

    @xPos.setter
    def xPos(self, xPos: int) -> None:
        self._xPos = xPos



if __name__ == '__main__':
    main(sys.argv)