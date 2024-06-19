from typing import Optional
from PySide6.QtWidgets import *
from PySide6.QtCore import * # type: ignore
from PySide6.QtGui import * # type: ignore

class GameTile(QWidget):
    clicked = Signal()

    def __init__(self, image: QPixmap, parent: Optional[QWidget] = ..., imageSize: int = 450, expandedImageSize: int = 540, flags: Qt.WindowType = Qt.WindowFlags()) -> None:
        super().__init__(parent, flags)
        
        self.baseImageSize = imageSize
        self.expandedImageSize = expandedImageSize

        
        self.__imageSize = imageSize
        
        self.layout:QVBoxLayout = QVBoxLayout(self)
        self.layout.addStretch()
        
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        
        # Scale the image to 600x900 first so the rounded corners are consistent
        image = image.scaled(600, 900, mode=Qt.TransformationMode.SmoothTransformation)

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

    def mousePressEvent(self, _e: QMouseEvent) -> None:
        self.clicked.emit()

    @Property(int)
    def bottomSpacing(self) -> int:
        return self.__bottomSpacing
    
    @bottomSpacing.setter
    def bottomSpacing(self, bottomSpacing: int) -> None:
        self.spacer.changeSize(1, bottomSpacing)
        self.layout.invalidate()
        self.__bottomSpacing = bottomSpacing
    
    @Property(int)
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