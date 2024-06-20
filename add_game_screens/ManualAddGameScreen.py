from typing import Callable
from PySide6.QtWidgets import *
from PySide6.QtCore import * # type: ignore
from PySide6.QtGui import * # type: ignore

from storage import Config, Library

class ManualAddGameScreen(QWidget):
    def __init__(self, library: Library, config: Config, refreshCallback: Callable[[], None]) -> None:
        super().__init__()
        
        self.library = library
        self.config = config
        self.refreshCallback = refreshCallback
        
        self.nameLabel = QLabel('Name')
        self.nameInput = QLineEdit()
        self.filepathLabel = QLabel('File path')
        self.filepathInput = QLineEdit()

        self.argumentLabel = QLabel('Arguments')
        self.argumentList = QListWidget()
        self.argumentAddButton = QPushButton(QIcon.fromTheme('add'), '')
        self.argumentAddButton.clicked.connect(self.addArgument)
        self.argumentRemoveButton = QPushButton(QIcon.fromTheme('remove'), '')
        self.argumentRemoveButton.clicked.connect(self.removeArgument)
        self.argumentButtonLayout = QVBoxLayout()
        self.argumentButtonLayout.addWidget(self.argumentAddButton)
        self.argumentButtonLayout.addWidget(self.argumentRemoveButton)
        self.argumentButtonLayout.addStretch()
        self.argumentLayout = QHBoxLayout()
        self.argumentLayout.addWidget(self.argumentList)
        self.argumentLayout.addLayout(self.argumentButtonLayout)
        
        self.tagLabel = QLabel('Tags')
        self.tagList = QListWidget()
        itemHeight = int(self.tagList.fontMetrics().height() * 1.5)
        itemSizeHint = QSize(0, itemHeight)
        
        for i, tag in enumerate(self.config.tags):
            self.tagList.addItem(tag)
            self.tagList.item(i).setCheckState(Qt.CheckState.Unchecked)
            self.tagList.item(i).setSizeHint(itemSizeHint)

        self.tagAddButton = QPushButton(QIcon.fromTheme('add'), '')
        self.tagAddButton.clicked.connect(self.addTag)
        self.tagRemoveButton = QPushButton(QIcon.fromTheme('remove'), '')
        self.tagRemoveButton.clicked.connect(self.removeTag)
        self.tagButtonLayout = QVBoxLayout()
        self.tagButtonLayout.addWidget(self.tagAddButton)
        self.tagButtonLayout.addWidget(self.tagRemoveButton)
        self.tagButtonLayout.addStretch()
        self.tagLayout = QHBoxLayout()
        self.tagLayout.addWidget(self.tagList)
        self.tagLayout.addLayout(self.tagButtonLayout)

        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.save)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.nameLabel)
        self.mainLayout.addWidget(self.nameInput)
        self.mainLayout.addWidget(self.filepathLabel)
        self.mainLayout.addWidget(self.filepathInput)
        self.mainLayout.addWidget(self.argumentLabel)
        self.mainLayout.addLayout(self.argumentLayout)
        self.mainLayout.addWidget(self.tagLabel)
        self.mainLayout.addLayout(self.tagLayout)
        self.mainLayout.addWidget(self.saveButton)
        self.mainLayout.addStretch()
        
        self.setLayout(self.mainLayout)
    
    def addArgument(self) -> None:
        self.argumentList.addItem('')
        item = self.argumentList.item(self.argumentList.count() - 1)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.argumentList.setCurrentRow(self.argumentList.count() - 1)
        self.argumentList.edit(self.argumentList.currentIndex())
    
    def removeArgument(self) -> None:
        self.argumentList.takeItem(self.argumentList.currentRow())
    
    def addTag(self) -> None:
        self.tagList.addItem('')
        item = self.tagList.item(self.tagList.count() - 1)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        item.setCheckState(Qt.CheckState.Unchecked)
        self.tagList.setCurrentRow(self.tagList.count() - 1)
        self.tagList.edit(self.tagList.currentIndex())

    def removeTag(self) -> None:
        self.tagList.takeItem(self.tagList.currentRow())
    
    def save(self) -> None:
        name = self.nameInput.text()
        filepath = self.filepathInput.text()
        
        # Save newly created tags
        tags = [self.tagList.item(i).text() for i in range(self.tagList.count())]
        self.config.updateTags(tags)
        self.config.save()
        

        if name == '':
            QMessageBox.critical(self, 'Error', 'Please enter a name')
            return
        
        if filepath == '':
            QMessageBox.critical(self, 'Error', 'Please enter a filepath')
            return

        args = [self.argumentList.item(i).text() for i in range(self.argumentList.count())]
        
        gameTags = [
            self.tagList.item(i).text()
            for i in range(self.tagList.count())
            if self.tagList.item(i).checkState() == Qt.CheckState.Checked
        ]
        self.library.addNativeGame(name, filepath, args, gameTags)
        self.library.save()
        
        self.nameInput.setText('')
        self.filepathInput.setText('')
        self.argumentList.clear()
        
        self.refreshCallback()