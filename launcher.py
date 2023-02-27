import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtGui import *
import sidebar


class GameTile(QWidget):
    def __init__(self, image: QPixmap, text: str = None, parent: QWidget = None, flags = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)
        
        self.__bottomSpacing = 0
        
        self.layout:QVBoxLayout = QVBoxLayout(self)
        
        self.layout.addStretch()
        
        imageLabel = QLabel(self)
        imageLabel.setPixmap(image)
        imageLabel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.layout.addWidget(imageLabel)
        
        titleLabel = QLabel(text, self)
        titleLabel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.layout.addWidget(titleLabel)
        
        self.raiseAnimation = QPropertyAnimation(self, b'bottomSpacing')
        self.raiseAnimation.setEndValue(100)
        self.dropAnimation = QPropertyAnimation(self, b'bottomSpacing')
        self.dropAnimation.setEndValue(0)
        
        self.spacer = QSpacerItem(0, 100)
        self.layout.addSpacerItem(self.spacer)
    

    @pyqtProperty(int)
    def bottomSpacing(self) -> int:
        return self.__bottomSpacing
    
    @bottomSpacing.setter
    def bottomSpacing(self, bottomSpacing: int) -> None:
        self.spacer.changeSize(1, bottomSpacing)
        self.__bottomSpacing = bottomSpacing
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.animationState = False
        
        testButton = {'icon': QIcon.fromTheme('view-sort-ascending-name'), 'text': QStaticText('Alphabetical order')}
        self.sidebar = sidebar.Sidebar(self, [testButton])
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        
        self.sidebar.itemClicked.connect(self.testAnimation)
        
        # self.tempButton = QPushButton('a')
        # self.tempButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self.scrollLayout = QHBoxLayout()
        self.tiles = []
        image = QPixmap('test_image.jpg')
        for i in range(10):
            tile = GameTile(image, 'test', self)
            self.tiles.append(tile)
            self.scrollLayout.addWidget(tile)
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
    
    
    def testAnimation(self, itemClicked):
        if self.animationState == False:
            self.tiles[0].raiseAnimation.start()
        else:
            self.tiles[0].dropAnimation.start()
        
        self.animationState = not self.animationState
            


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()