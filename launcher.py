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
        return super().mousePressEvent(e)

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

        self.scrollAnimation = QPropertyAnimation(self.horizontalScrollBar(), b'value')
        self.scrollAnimation.setDuration(100)
        self.scrollAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)


    def ensureWidgetVisible(self, childWidget: QWidget, xMargin: int = ..., yMargin: int = ...) -> None:
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

    @pyqtProperty(int)
    def xPos(self) -> int:
        return self._xPos

    @xPos.setter
    def xPos(self, xPos: int) -> None:
        self._xPos = xPos
        

class MainWindow(QMainWindow):
    def __init__(self, library: list):
        super().__init__()
        
        self.MAIN_CONTENT_PADDING = 20

        self.runningProcess = None

        testButton1 = {'icon': QIcon.fromTheme('view-sort-ascending-name'), 'text': QStaticText('Alphabetical order')}
        testButton2 = {'icon': QIcon.fromTheme('view-sort-ascending-name'), 'text': QStaticText('Reverse')}
        self.sidebar = sidebar.Sidebar(self, [testButton1, testButton2])
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        
        # self.sidebar.itemClicked.connect(self.testAnimation)
        
        # self.tempButton = QPushButton('a')
        # self.tempButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.scrollLayout = QHBoxLayout()
        self.scrollLayout.setContentsMargins(self.MAIN_CONTENT_PADDING, 0, self.MAIN_CONTENT_PADDING, self.MAIN_CONTENT_PADDING)
        scrollMargins = 20
        self.tiles: list[tuple] = []
        defaultImage = QPixmap(600, 900)
        defaultImage.fill(Qt.GlobalColor.white)
        imageHeight = 450
        expandedImageHeight = 540
        for i, game in enumerate(library):
            image = getLibraryImage(game['id'])
            if image is None:
                image = defaultImage

            tile = GameTile(image, self, imageHeight, expandedImageHeight)
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
        self.scrollArea.setFixedHeight(expandedImageHeight + 2 * scrollMargins + 15)
        
        
        
        settingsButtonSize = 50
        self.settingsButton = QPushButton(QIcon.fromTheme('settings'), '')
        self.settingsButton.setFixedSize(settingsButtonSize, settingsButtonSize)
        self.settingsButton.setIconSize(QSize(int(settingsButtonSize*0.8), int(settingsButtonSize*0.8)))

        topBar = QHBoxLayout()
        topBar.addStretch()
        topBar.addWidget(self.settingsButton)
        
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
        
        self.playButton = QPushButton('Play')
        font = self.font()
        font.setPointSize(24)
        font.setBold(True)
        self.playButton.setFont(font)
        self.playButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        self.playButton.setMinimumWidth(150)
        self.playButton.setMaximumHeight(75)
        self.playButton.clicked.connect(self.playButtonClicked)
        playButtonLayout = QHBoxLayout()
        playButtonLayout.addWidget(self.playButton)
        playButtonLayout.addStretch()
        
        gameInfoLayout = QVBoxLayout()
        gameInfoLayout.addWidget(self.gameTitle)
        gameInfoLayout.addWidget(self.gameDescription)
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
        
        self.setMinimumHeight(875)
        self.resize(1200, 875)
        self.showMaximized()
        # self.showFullScreen()
    
    
    def tileClicked(self, index):
        if index == self.selectedTile:
            return
        
        animationGroup = QParallelAnimationGroup(self)
        animationGroup.addAnimation(self.tiles[index][0].growAnimation)
        if self.selectedTile is not None:
            animationGroup.addAnimation(self.tiles[self.selectedTile][0].shrinkAnimation)
        animationGroup.start()
        self.scrollArea.ensureWidgetVisible(self.tiles[index][0], 200, 200)
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
        game: dict = self.tiles[self.selectedTile][1]
        self.launchGame(game)
        self.playButton.setText('Stop')

    def launchGame(self, game: dict) -> None:
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