import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtGui import *


class Sidebar(QListWidget):
    def __init__(self, parent, buttons: list = None):
        super().__init__(parent)
        
        if buttons is None:
            buttons = [{'icon': None, 'text': ''}]
        
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)
        self.setIconSize(QSize(48, 48))

        for i, button in enumerate(buttons):
            self.addItem(QListWidgetItem())
            self.setItemDelegateForRow(i, CustomDelegate(self, button['text'], button['icon']))
        
        iconWidth = self.iconSize().width()
        leftPadding = self.itemDelegateForRow(0).LEFT_PADDING
        rightPadding = self.itemDelegateForRow(0).ICON_R_PADDING
        self.minWidth = iconWidth + leftPadding + rightPadding + 4
        self.awidth = self.minWidth
        
        self.expandAnimation = QPropertyAnimation(self, b'awidth')
        self.expandAnimation.setDuration(200)
        self.expandAnimation.setEasingCurve(QEasingCurve.InOutCubic)
        
        self.contractAnimation = QPropertyAnimation(self, b'awidth')
        self.contractAnimation.setEndValue(self.minWidth)
        self.contractAnimation.setDuration(200)
        self.contractAnimation.setEasingCurve(QEasingCurve.InOutCubic)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)
        

    def leaveEvent(self, e) -> None:
        self.contractAnimation.start()
    
    def enterEvent(self, e) -> None:
        self.expand()
    

    # def mousePressEvent(self, e: QMouseEvent) -> None:
    #     super().mousePressEvent(e)
    #     focusedWidget = QApplication.focusWidget()
    #     if isinstance(focusedWidget, Sidebar):
    #         focusedWidget.clearFocus()
    

    def expand(self) -> None:
        self.expandAnimation.setEndValue(self.maxWidth())
        self.expandAnimation.start()
    

    def maxWidth(self) -> None:
        return max([self.sizeHintForColumn(i) for i in range(self.count())]) + 4


    @pyqtProperty(int)
    def awidth(self) -> int:
        return self._awidth
    
    @awidth.setter
    def awidth(self, value) -> None:
        self._awidth = value
        super().setFixedWidth(self._awidth)
        

class CustomDelegate(QStyledItemDelegate):
    def __init__(self, parent, text, icon = None) -> None:
        self.text = text
        self.icon: QIcon = icon
        self.iconSize: QSize = parent.iconSize() if icon is not None else QSize(0, 0)
        
        self.LEFT_PADDING = 5
        self.RIGHT_PADDING = 10
        self.ICON_H_PADDING = 5
        self.ICON_R_PADDING = 5

        super().__init__(parent)
    
    def paint(self, painter: QPainter, option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
        super().paint(painter, option, index)
        
        posRect = option.rect
        
        if self.icon is not None:
            pixmap = self.icon.pixmap(self.iconSize)
            iconPos = QPoint(posRect.left() + self.LEFT_PADDING, posRect.top() + self.ICON_H_PADDING)
            painter.drawPixmap(iconPos, pixmap)
        
        painter.setFont(option.font)
        textHeight = option.fontMetrics.height()
        textRelativeYPos = (posRect.height() - textHeight) / 2 # Vertically center the text
        textXPos = posRect.left() + self.LEFT_PADDING + self.iconSize.width() + self.ICON_R_PADDING
        textPos = QPoint(textXPos, int(posRect.top() + textRelativeYPos))
        painter.drawStaticText(textPos, self.text)

    
    def sizeHint(self, option: 'QStyleOptionViewItem', index: QModelIndex) -> QSize:
        textWidth = self.text.size().width()
        textHeight = option.fontMetrics.height()
        iconWidth = self.iconSize.width()
        iconHeight = self.iconSize.height() + 2 * self.ICON_H_PADDING
        width = int(self.LEFT_PADDING + iconWidth + self.ICON_R_PADDING + textWidth + self.RIGHT_PADDING)
        height = int(max(textHeight, iconHeight))
        
        return QSize(width, height)
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.buttonState = False
        self.setMinimumSize(500, 300)
        
        button1 = {'text': QStaticText('Button 1'), 'icon': QIcon.fromTheme('battery')}
        button2 = {'text': QStaticText('Button 2aaaaaaaaaaaaa'), 'icon': QIcon.fromTheme('computer')}
        button3 = {'text': QStaticText('Button 3'), 'icon': QIcon.fromTheme('camera-web')}
        self.sidebar = Sidebar(self, [button1, button2, button3])
        self.sidebar.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Expanding)
        
        self.mainWidget = QPushButton()
        self.mainWidget.setText('0')
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.mainWidget.setFont(font)
        self.mainWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.mainWidget.pressed.connect(self.buttonPressed)


        layout = QHBoxLayout()
        layout.addWidget(self.sidebar)
        layout.addWidget(self.mainWidget)
        centralWidget = QWidget()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        
        self.sidebar.itemSelectionChanged.connect(self.sidebarChanged)
        

    def sidebarChanged(self):
        selection = self.sidebar.selectedIndexes()[0].row()
        
        self.mainWidget.setText(str(selection))
    

    def buttonPressed(self):
        if self.buttonState:
            self.sidebar.contractAnimation.start()
        else:
            self.sidebar.expand()
        
        self.buttonState = not self.buttonState
    
def main(argv):
    app = QApplication(argv)

    window = MainWindow()
    window.show()

    app.exec()

if __name__ == '__main__':
    main(sys.argv)