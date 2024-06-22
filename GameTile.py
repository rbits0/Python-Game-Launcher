from typing import Optional
from PySide6.QtWidgets import *
from PySide6.QtCore import * # type: ignore
from PySide6.QtGui import * # type: ignore

class GameTile(QLabel):
    clicked = Signal()

    def __init__(self, image: QPixmap, imageHeight: int, expandedImageHeight: int, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        
        # Scale the image to 600x900 (or whatever x 900) first so the rounded corners are consistent
        image = image.scaledToHeight(900, mode=Qt.TransformationMode.SmoothTransformation)


        # I want all images to be the same size, but I also want to animate the width instead of the height,
        # so I convert the height to a width when the tile is created
        ratio = image.width() / image.height()
        self.baseImageWidth = int(imageHeight * ratio - 2)
        self.expandedImageWidth = int(expandedImageHeight * ratio - 2)
        
        self._imageWidth = self.baseImageWidth
        

        # Image (with rounded corners)
        radius = 30
        self.imagePixmap = QPixmap(image.size())
        self.imagePixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(self.imagePixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(image))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(image.rect(), radius, radius)
        
        self.setPixmap(self.imagePixmap.scaledToWidth(self._imageWidth, Qt.TransformationMode.SmoothTransformation))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        

    def mousePressEvent(self, _e: QMouseEvent) -> None:
        self.clicked.emit()

    @Property(int)
    def imageWidth(self) -> int:
        return self._imageWidth
    
    @imageWidth.setter # type: ignore
    def imageWidth(self, value: int) -> None:
        if value == self.baseImageWidth or self.expandedImageWidth:
            # If the animation is over, do a higher quality transformation
            self.setPixmap(self.imagePixmap.scaledToWidth(value, Qt.TransformationMode.SmoothTransformation))
        else:
            # Do fast transformation while animating
            self.setPixmap(self.imagePixmap.scaledToWidth(value, Qt.TransformationMode.FastTransformation))

        self._imageWidth = value