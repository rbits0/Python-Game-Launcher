import sys
from typing import Optional, NamedTuple, Callable
from PySide6.QtWidgets import * 
from PySide6.QtCore import * # type: ignore
from PySide6.QtGui import * # type: ignore


SidebarButton = NamedTuple('SidebarButton', [
    ('icon', QIcon),
    ('text', QStaticText),
    ('callback', Callable[[], None]),
])


class Sidebar(QListWidget):
    def __init__(self, buttons: list[SidebarButton], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        self.buttons = buttons
        
        font = QFont()
        font.setPointSize(20)
        self.setFont(font)
        self.setIconSize(QSize(48, 48))

        for i, button in enumerate(self.buttons):
            self.addItem(QListWidgetItem())
            self.setItemDelegateForRow(i, CustomDelegate(self, button.text, button.icon))
        
        iconWidth = self.iconSize().width()
        leftPadding = CustomDelegate.LEFT_PADDING
        rightPadding = CustomDelegate.ICON_R_PADDING
        self.minWidth = iconWidth + leftPadding + rightPadding + 4
        self.fixedWidth = self.minWidth # type: ignore
        
        self.expandAnimation = QPropertyAnimation(self, b'fixedWidth')
        self.expandAnimation.setDuration(200)
        self.expandAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self.contractAnimation = QPropertyAnimation(self, b'fixedWidth')
        self.contractAnimation.setEndValue(self.minWidth)
        self.contractAnimation.setDuration(200)
        self.contractAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTextElideMode(Qt.TextElideMode.ElideNone)

        self.setCurrentRow(0)
        
        self.itemSelectionChanged.connect(self.handleItemSelectionChanged)
        

    def leaveEvent(self, e: QEvent) -> None:
        self.contractAnimation.start()
    
    def enterEvent(self, e: QEnterEvent) -> None:
        self.expand()
    
    def focusInEvent(self, e: QFocusEvent) -> None:
        self.expand()
        super().focusInEvent(e)

    def focusOutEvent(self, e: QFocusEvent) -> None:
        self.contractAnimation.start()
        super().focusOutEvent(e)
    
    def expand(self) -> None:
        self.expandAnimation.setEndValue(self.maxWidth())
        self.expandAnimation.start()
    
    
    def maxWidth(self) -> int:
        return max([self.sizeHintForColumn(i) for i in range(self.count())]) + 4
    
    
    def handleItemSelectionChanged(self) -> None:
        index = self.currentRow()
        self.buttons[index].callback()


    @Property(int, doc=
        '''
        Width of the sidebar
        
        Whenever it is changed, it calls self.setFixedWidth with the new value
        '''
    )
    def fixedWidth(self) -> int:
        return self._fixedWidth
    
    @fixedWidth.setter # type: ignore
    def fixedWidth(self, value: int) -> None:
        self._fixedWidth = value
        self.setFixedWidth(self._fixedWidth)
        

class CustomDelegate(QStyledItemDelegate):
    LEFT_PADDING = 5
    RIGHT_PADDING = 10
    ICON_H_PADDING = 5
    ICON_R_PADDING = 5
    
    def __init__(self, parent: QListWidget, text: QStaticText, icon: Optional[QIcon] = None) -> None:
        super().__init__(parent)

        self.text = text
        self.icon: Optional[QIcon] = icon
        self.iconSize: QSize = parent.iconSize() if icon is not None else QSize(0, 0)
        print(parent.iconSize())
        

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> None:
        # We're drawing the text/icon ourselves so it's consistent between themes
        
        super().paint(painter, option, index)
        
        # For some reason, QStyleOption doesn't expose its variables, so suppress the error
        posRect: QRect = option.rect # type: ignore
        
        if self.icon is not None:
            pixmap = self.icon.pixmap(self.iconSize)
            iconPos = QPoint(posRect.left() + self.LEFT_PADDING, posRect.top() + self.ICON_H_PADDING)
            painter.drawPixmap(iconPos, pixmap)
        
        painter.setFont(option.font) # type: ignore
        textHeight: int = option.fontMetrics.height() # type: ignore
        textRelativeYPos = (posRect.height() - textHeight) / 2 # Vertically center the text
        textXPos = posRect.left() + self.LEFT_PADDING + self.iconSize.width() + self.ICON_R_PADDING
        textPos = QPoint(textXPos, int(posRect.top() + textRelativeYPos))
        painter.drawStaticText(textPos, self.text)

    
    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex) -> QSize:
        textWidth = self.text.size().width()
        textHeight = option.fontMetrics.height() # type: ignore
        iconWidth = self.iconSize.width()
        iconHeight = self.iconSize.height() + 2 * self.ICON_H_PADDING
        width = int(self.LEFT_PADDING + iconWidth + self.ICON_R_PADDING + textWidth + self.RIGHT_PADDING)
        height = int(max(textHeight, iconHeight))
        
        return QSize(width, height)
        