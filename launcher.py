import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtGui import *
import sidebar


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
        print(isLeft, doScroll)
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
    def __init__(self):
        super().__init__()
        
        self.MAIN_CONTENT_PADDING = 20

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
        self.tiles: list[GameTile] = []
        image = QPixmap('test_image2.png')
        imageHeight = 450
        expandedImageHeight = 540
        for i in range(10):
            tile = GameTile(image, self, imageHeight, expandedImageHeight)
            tile.clicked.connect(lambda i=i: self.tileClicked(i))
            self.tiles.append(tile)
            self.scrollLayout.addWidget(tile)
        self.tiles[0].growAnimation.start()
        self.selectedTile = 0

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
        
        gameTitle = QLabel("Title")
        font = self.font()
        font.setPointSize(36)
        font.setBold(True)
        gameTitle.setFont(font)
        
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
        self.playButton.clicked.connect(lambda: print(self.height()))
        self.playButton.setMinimumWidth(150)
        self.playButton.setMaximumHeight(75)
        playButtonLayout = QHBoxLayout()
        playButtonLayout.addWidget(self.playButton)
        playButtonLayout.addStretch()
        
        gameInfoLayout = QVBoxLayout()
        gameInfoLayout.addWidget(gameTitle)
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
        
        self.setMinimumHeight(875)
        self.resize(1200, 875)
        self.showMaximized()
        # self.showFullScreen()
    
    
    def testAnimation(self, e):
        row = self.sidebar.currentRow()
        print(row)
        if row == 0:
            self.tiles[0].raiseAnimation.start()
        else:
            self.tiles[0].dropAnimation.start()
    

    def tileClicked(self, index):
        if index == self.selectedTile:
            return
        
        animationGroup = QParallelAnimationGroup(self)
        animationGroup.addAnimation(self.tiles[index].growAnimation)
        animationGroup.addAnimation(self.tiles[self.selectedTile].shrinkAnimation)
        animationGroup.start()
        self.scrollArea.ensureWidgetVisible(self.tiles[index], 200, 200)
        self.selectedTile = index
    

    # def resizeEvent(self, e: QResizeEvent) -> None:
    #     self.gameDescription.setMaximumWidth(self.scrollArea.width())
    #     return super().resizeEvent(e)
            


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()