from typing import Optional
from PySide6.QtWidgets import *
from PySide6.QtCore import * # type: ignore
from PySide6.QtGui import * # type: ignore

class GameTile(QLabel):
    clicked = Signal()

    def __init__(self, image: QPixmap, parent: Optional[QWidget] = None, imageHeight: int = 450, expandedImageHeight: int = 540) -> None:
        super().__init__(parent)
        
        self.baseImageHeight = imageHeight - 2
        self.expandedImageHeight = expandedImageHeight - 2

        
        self._imageHeight = imageHeight
        
        # Scale the image to 600x900 first so the rounded corners are consistent
        image = image.scaled(600, 900, mode=Qt.TransformationMode.SmoothTransformation)

        # Image (with rounded corners)
        radius = 30
        self.imagePixmap = QPixmap(image.size())
        self.imagePixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.imagePixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(image))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(image.rect(), radius, radius)
        
        self.setPixmap(self.imagePixmap.scaledToHeight(self._imageHeight, Qt.TransformationMode.SmoothTransformation))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        self.growAnimation = QPropertyAnimation(self, b'imageHeight')
        self.growAnimation.setEndValue(self.expandedImageHeight)
        self.growAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.growAnimation.setDuration(100)
        self.shrinkAnimation = QPropertyAnimation(self, b'imageHeight')
        self.shrinkAnimation.setEndValue(self.baseImageHeight)
        self.shrinkAnimation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.shrinkAnimation.setDuration(100)
        

    def mousePressEvent(self, _e: QMouseEvent) -> None:
        self.clicked.emit()

    @Property(int)
    def imageHeight(self) -> int:
        return self._imageHeight
    
    @imageHeight.setter # type: ignore
    def imageHeight(self, value: int) -> None:
        if value == self.baseImageHeight or self.expandedImageHeight:
            # If the animation is over, do a higher quality transformation
            self.setPixmap(self.imagePixmap.scaledToHeight(value, Qt.TransformationMode.SmoothTransformation))
        else:
            # Do fast transformation while animating
            self.setPixmap(self.imagePixmap.scaledToHeight(value, Qt.TransformationMode.FastTransformation))

        self._imageHeight = value