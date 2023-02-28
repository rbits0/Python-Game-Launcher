import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtGui import *
import sidebar


class GameTile(QWidget):
    clicked = pyqtSignal()

    def __init__(self, image: QPixmap, parent: QWidget = None, flags = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)
        
        # self.FONT_SIZE = 30

        
        self.__bottomSpacing = 0
        self.__imageSize = 600
        
        self.layout:QVBoxLayout = QVBoxLayout(self)
        self.layout.addStretch()
        
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        self.image = image
        self.imageLabel = QLabel(self)
        self.imageLabel.setPixmap(image.scaledToHeight(600))
        self.imageLabel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.layout.addWidget(self.imageLabel)
        
        # self.titleLabel = QLabel(text, self)
        # font = self.font()
        # font.setPointSize(self.FONT_SIZE)
        # self.titleLabel.setFont(font)
        # self.titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        # self.layout.addWidget(self.titleLabel)
        
        self.raiseAnimation = QPropertyAnimation(self, b'bottomSpacing')
        self.raiseAnimation.setEndValue(100)
        self.raiseAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.raiseAnimation.setDuration(100)
        self.dropAnimation = QPropertyAnimation(self, b'bottomSpacing')
        self.dropAnimation.setEndValue(0)
        self.dropAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.dropAnimation.setDuration(100)
        
        self.growAnimation = QPropertyAnimation(self, b'imageSize')
        self.growAnimation.setEndValue(700)
        self.growAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.growAnimation.setDuration(100)
        self.shrinkAnimation = QPropertyAnimation(self, b'imageSize')
        self.shrinkAnimation.setEndValue(600)
        self.shrinkAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.shrinkAnimation.setDuration(100)
        
        self.spacer: QSpacerItem = QSpacerItem(0, 0)
        self.layout.addSpacerItem(self.spacer)
    

    # def enterEvent(self, e: QEvent) -> None:
    #     # self.raiseAnimation.start()
    #     self.growAnimation.start()
    #     return super().enterEvent(e)

    # def leaveEvent(self, e: QEvent) -> None:
    #     # self.dropAnimation.start()
    #     self.shrinkAnimation.start()
    #     return super().leaveEvent(e)
    
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
        self.imageLabel.setPixmap(self.image.scaledToHeight(imageSize))
        self.__imageSize = imageSize
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        testButton1 = {'icon': QIcon.fromTheme('view-sort-ascending-name'), 'text': QStaticText('Alphabetical order')}
        testButton2 = {'icon': QIcon.fromTheme('view-sort-ascending-name'), 'text': QStaticText('Reverse')}
        self.sidebar = sidebar.Sidebar(self, [testButton1, testButton2])
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        
        self.sidebar.itemClicked.connect(self.testAnimation)
        
        # self.tempButton = QPushButton('a')
        # self.tempButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.scrollLayout = QHBoxLayout()
        self.tiles = []
        image = QPixmap('test_image.jpg')
        for i in range(10):
            tile = GameTile(image, self)
            tile.clicked.connect(lambda i=i: self.tileClicked(i))
            self.tiles.append(tile)
            self.scrollLayout.addWidget(tile)
        self.selectedTile = 0

        self.scrollWidget = QWidget()
        self.scrollWidget.setLayout(self.scrollLayout)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        
        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        # layout.addWidget(self.tempButton)
        layout.addWidget(self.scrollArea)
        # layout.addWidget(self.scrollWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        centralWidget = QWidget(self)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        
        self.resize(1000, 700)
        self.showMaximized()
    
    
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
        
        self.tiles[index].growAnimation.start()
        self.tiles[self.selectedTile].shrinkAnimation.start()
        self.selectedTile = index
            
            


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()