from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import storage
from storage import Config

class ManualAddGameScreen(QWidget):
    def __init__(self, library: list[dict], config: Config, refreshFunction) -> None:
        super().__init__()
        
        self.library = library
        self.config = config
        self.refreshFunction = refreshFunction
        
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
        
        for i, tag in enumerate(self.config.tags):
            self.tagList.addItem(tag)
            self.tagList.item(i).setCheckState(Qt.CheckState.Unchecked)

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

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.nameInput)
        self.layout.addWidget(self.filepathLabel)
        self.layout.addWidget(self.filepathInput)
        self.layout.addWidget(self.argumentLabel)
        self.layout.addLayout(self.argumentLayout)
        self.layout.addWidget(self.tagLabel)
        self.layout.addLayout(self.tagLayout)
        self.layout.addWidget(self.saveButton)
        self.layout.addStretch()
        
        self.setLayout(self.layout)
    
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
        
        storage.addNativeGame(self.library, name, filepath, args, tags)
        storage.saveLibrary(self.library)
        
        self.nameInput.setText('')
        self.filepathInput.setText('')
        self.argumentList.clear()
        
        self.refreshFunction()