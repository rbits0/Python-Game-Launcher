import sys, os, sidebar, json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtGui import *


CONFIG_FOLDER = os.path.join(os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), 'PythonGameLauncher')
CONFIG_FILE = os.path.join(CONFIG_FOLDER, 'config.json')
GAMES_FILE = os.path.join(CONFIG_FOLDER, 'games.json')
ARTWORK_FOLDER = os.path.join(CONFIG_FOLDER, 'artwork')


class GameTile(QWidget):
    clicked = pyqtSignal()

    def __init__(self, image: QPixmap, parent: QWidget = None, imageSize = 450, expandedImageSize = 540, flags = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)
        
        # self.FONT_SIZE = 30
        self.baseImageSize = imageSize
        self.expandedImageSize = expandedImageSize

        
        self.__imageSize = 450
        
        self.layout:QVBoxLayout = QVBoxLayout(self)
        self.layout.addStretch()
        
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # Scale the image to 600x900 first so the rounded corners are consistent
        image = image.scaled(600, 900, transformMode=Qt.TransformationMode.SmoothTransformation)

        # Image (with rounded corners)
        radius = 30
        self.image = QPixmap(image.size())
        self.image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(image))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(image.rect(), radius, radius)
        
        self.imageLabel = QLabel(self)
        self.imageLabel.setPixmap(self.image.scaledToHeight(self.imageSize, Qt.TransformationMode.SmoothTransformation))
        self.imageLabel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.layout.addWidget(self.imageLabel)
        
        # self.titleLabel = QLabel(text, self)
        # font = self.font()
        # font.setPointSize(self.FONT_SIZE)
        # self.titleLabel.setFont(font)
        # self.titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        # self.layout.addWidget(self.titleLabel)
        
        self.growAnimation = QPropertyAnimation(self, b'imageSize')
        self.growAnimation.setEndValue(self.expandedImageSize)
        self.growAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.growAnimation.setDuration(100)
        self.shrinkAnimation = QPropertyAnimation(self, b'imageSize')
        self.shrinkAnimation.setEndValue(self.baseImageSize)
        self.shrinkAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.shrinkAnimation.setDuration(100)
        
        self.setLayout(self.layout)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        self.clicked.emit()

    @pyqtProperty(int)
    def bottomSpacing(self) -> int:
        return self.__bottomSpacing
    
    @bottomSpacing.setter
    def bottomSpacing(self, bottomSpacing: int) -> None:
        self.spacer.changeSize(1, bottomSpacing)
        self.layout.invalidate()
        self.__bottomSpacing = bottomSpacing
    
    @pyqtProperty(int)
    def imageSize(self) -> int:
        return self.__imageSize
    
    @imageSize.setter
    def imageSize(self, imageSize: int) -> None:
        if imageSize == self.baseImageSize or self.expandedImageSize:
            # Smooth
            self.imageLabel.setPixmap(self.image.scaledToHeight(imageSize, Qt.TransformationMode.SmoothTransformation))
        else:
            # Fast
            self.imageLabel.setPixmap(self.image.scaledToHeight(imageSize, Qt.TransformationMode.FastTransformation))
        self.__imageSize = imageSize


class AnimatedScrollArea(QScrollArea):
    def __init__(self, parent: QWidget = ...) -> None:
        super().__init__(parent)
        
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.scrollAnimation = QPropertyAnimation(self.horizontalScrollBar(), b'value')
        self.scrollAnimation.setDuration(100)
        self.scrollAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        # self.scrollEndValue = 0

        # self.scroller: QScroller = QScroller.scroller(self)
        # scrollerProperties = QScrollerProperties()
        # scrollerProperties.setScrollMetric(
        #     QScrollerProperties.ScrollMetric.HorizontalOvershootPolicy,
        #     QScrollerProperties.OvershootPolicy.OvershootAlwaysOff
        # )
        # scrollerProperties.setScrollMetric(QScrollerProperties.ScrollMetric.DecelerationFactor, 0.6)
        # scrollerProperties.setScrollMetric(QScrollerProperties.ScrollMetric.MaximumVelocity, 0)
        # self.scroller.setScrollerProperties(scrollerProperties)
        # QScroller.grabGesture(self, QScroller.ScrollerGestureType.LeftMouseButtonGesture)

    def ensureWidgetVisibleAnimated(self, childWidget: QWidget, xMargin: int = ..., yMargin: int = ...) -> None:
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
            # print(isLeft, scrollBarValue, xPos, pos)
            # self.horizontalScrollBar().setValue(xPos)
    
    def testScroll(self) -> None:
        # self.scroller.scrollTo(QPoint(100, 100))
        pass
    
    def wheelEvent(self, e: QWheelEvent) -> None:
        delta = e.angleDelta().y()
        # if self.scrollAnimation.state() == QAbstractAnimation.State.Running:
        #     newValue = self.scrollEndValue - delta
        # else:
        newValue = self.horizontalScrollBar().value() - delta
        
        self.horizontalScrollBar().setValue(newValue)
        
        # self.scrollEndValue = newValue
        # self.scrollAnimation.setEndValue(newValue)
        # self.scrollAnimation.start()
        # if self.scroller.state() == QScroller.State.Inactive:
        #     newValue = self.horizontalScrollBar().value() - delta
        # else:
        #     newValue = self.scroller.finalPosition().x() - delta
        # self.scroller.stop()
        # self.scroller.scrollTo(QPointF(newValue, 0))
    
    def keyPressEvent(self, e: QKeyEvent) -> None:
        e.ignore()
        

    @pyqtProperty(int)
    def xPos(self) -> int:
        return self._xPos

    @xPos.setter
    def xPos(self, xPos: int) -> None:
        self._xPos = xPos


class PlayButton(QPushButton):
    def keyPressEvent(self, e: QKeyEvent) -> None:
        # print(e, e.key())
        # print(Qt.Key.Key_Return)
        if e.key() == Qt.Key.Key_Return:
            self.click()
        else:
            e.ignore()
    
    def focusInEvent(self, e: QFocusEvent) -> None:
        self.setStyleSheet('QPushButton {background-color: blue;}')
        # palette = self.parent().palette()
        # highlightColor = palette.color(QPalette.ColorRole.Highlight)
        # palette.setColor(QPalette.ColorRole.Button, highlightColor)
        return super().focusInEvent(e)
    
    def focusOutEvent(self, e: QFocusEvent) -> None:
        self.setStyleSheet('')
        return super().focusInEvent(e)
    
        
        



class MainWindow(QMainWindow):
    def __init__(self, library: list):
        super().__init__()
        
        self.MAIN_CONTENT_PADDING = 20

        self.runningProcess = None
        self.library = library

        testButton1 = {'icon': QIcon.fromTheme('view-sort-ascending-name'), 'text': QStaticText('Alphabetical order')}
        testButton2 = {'icon': QIcon.fromTheme('view-sort-ascending-name'), 'text': QStaticText('Reverse')}
        self.sidebar = sidebar.Sidebar(None, [testButton1, testButton2])
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        self.sidebar.itemSelectionChanged.connect(self.sidebarClicked)
        
        
        self.scrollLayout = QHBoxLayout()
        self.scrollLayout.setContentsMargins(self.MAIN_CONTENT_PADDING, 0, self.MAIN_CONTENT_PADDING, self.MAIN_CONTENT_PADDING)
        scrollMargins = 20
        self.tiles: list[tuple] = []
        self.defaultImage = QPixmap(600, 900)
        self.defaultImage.fill(Qt.GlobalColor.white)
        self.imageHeight = 450
        self.expandedImageHeight = 540
        for i, game in enumerate(library):
            image = getLibraryImage(game['id'])
            if image is None:
                image = self.defaultImage

            tile = GameTile(image, self, self.imageHeight, self.expandedImageHeight)
            tile.clicked.connect(lambda i=i: self.tileClicked(i))
            self.tiles.append((tile, game))
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
        
        
        
        settingsButtonSize = 50
        self.settingsButton = QPushButton(QIcon.fromTheme('settings'), '')
        self.settingsButton.setFixedSize(settingsButtonSize, settingsButtonSize)
        self.settingsButton.setIconSize(QSize(int(settingsButtonSize*0.8), int(settingsButtonSize*0.8)))

        topBar = QHBoxLayout()
        topBar.addStretch()
        topBar.addWidget(self.settingsButton)
        topBar.setContentsMargins(0, 10, 10, 0)
        
        self.gameTitle = QLabel("Title")
        font = self.font()
        font.setPointSize(36)
        font.setBold(True)
        self.gameTitle.setFont(font)
        
        self.gameDescription = QLabel("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.")
        font = self.font()
        font.setPointSize(20)
        self.gameDescription.setFont(font)
        # self.gameDescription.setMinimumWidth(0)
        # self.gameDescription.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
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
        # self.playButton.setStyleSheet('QPushButton:focus {background-color: blue;}')
        # self.playButton.clicked.connect(self.scrollArea.testScroll)
        playButtonLayout = QHBoxLayout()
        playButtonLayout.addWidget(self.playButton)
        playButtonLayout.addStretch()
        
        gameInfoLayout = QVBoxLayout()
        gameInfoLayout.addWidget(self.gameTitle)
        gameInfoLayout.addWidget(self.gameDescription)
        gameInfoLayout.addStretch()
        gameInfoLayout.addLayout(playButtonLayout)
        gameInfoLayout.setContentsMargins(self.MAIN_CONTENT_PADDING, 0, 0, 0)
        
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
    
    
    def tileClicked(self, index: int, animate: bool=True):
        if index == self.selectedTile:
            return
        if index >= self.scrollLayout.count():
            return

        prevTile = self.tiles[self.selectedTile][0] if self.selectedTile is not None else None
        currTile = self.tiles[index][0]
        
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

        game = self.tiles[index][1]
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
            game: dict = self.tiles[self.selectedTile][1]
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
            process.start(game['filePath'], args)

        self.runningProcess: tuple = (process, game['id'])
        
        process.finished.connect(self.processFinished)
    
    def processFinished(self) -> None:
        self.playButton.setText('Play')
        self.runningProcess = None
    

    def sidebarClicked(self) -> None:
        itemClicked = self.sidebar.currentRow()
        if itemClicked == 0:
            # Ascending alphabetical order
            self.library.sort(key=lambda x: x['name'])
        elif itemClicked == 1:
            # Descending alphabetical order
            self.library.sort(key=lambda x: x['name'], reverse=True)
        
        for tile in self.tiles:
            self.scrollLayout.removeWidget(tile[0])
            tile[0].deleteLater()
        
        self.tiles: list[tuple] = []
        
        for i, game in enumerate(self.library):
            image = getLibraryImage(game['id'])
            if image is None:
                image = self.defaultImage

            tile = GameTile(image, self, self.imageHeight, self.expandedImageHeight)
            tile.clicked.connect(lambda i=i: self.tileClicked(i))
            self.tiles.append((tile, game))
            self.scrollLayout.addWidget(tile)
        
        self.selectedTile = None
        self.tileClicked(0, animate=False)
        
        self.scrollLayout.update()
        self.scrollWidget.update()
        self.scrollArea.update()
    

    def keyPressEvent(self, e: QKeyEvent) -> None:
        # print(self.scrollArea.hasFocus(), self.sidebar.hasFocus())
        # print(e.key())
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

    

    # def resizeEvent(self, e: QResizeEvent) -> None:
    #     self.gameDescription.setMaximumWidth(self.scrollArea.width())
    #     return super().resizeEvent(e)


def readConfig() -> dict:
    if not os.path.exists(ARTWORK_FOLDER):
        os.mkdir(ARTWORK_FOLDER)

    if not os.path.exists(CONFIG_FILE):
        return False
    
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    
    return config

def getLibrary() -> list:
    if os.path.exists(GAMES_FILE) and os.path.getsize(GAMES_FILE) > 0:
        with open(GAMES_FILE, 'r') as file:
            game_library = json.load(file)
        
        return game_library
    else:
        with open(GAMES_FILE, 'w') as file:
            json.dump([], file, indent='\t')
        return []

def getLibraryImage(id: int) -> QPixmap:
    if os.path.exists(os.path.join(ARTWORK_FOLDER, f'{id}_library_image.jpg')):
        path = os.path.join(ARTWORK_FOLDER, f'{id}_library_image.jpg')
    elif os.path.exists(os.path.join(ARTWORK_FOLDER, f'{id}_library_image.png')):
        path = os.path.join(ARTWORK_FOLDER, f'{id}_library_image.png')
    else:
        # print(os.path.join(ARTWORK_FOLDER, f'{id}_library_image.jpg'))
        return None

    return QPixmap(path)

            

def main(argv) -> None:
    config = readConfig()
    library = getLibrary()


    app = QApplication(argv)

    window = MainWindow(library)
    window.show()

    app.exec()


if __name__ == '__main__':
    main(sys.argv)