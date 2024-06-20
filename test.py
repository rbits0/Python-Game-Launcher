from PySide6 import QtCore, QtWidgets

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        
        self.myProperty = 0
    
    @QtCore.Property(int)
    def myProperty(self) -> int:
        return self.myNum
    
    @myProperty.setter
    def myProperty(self, value: int) -> None:
        self.myNum = value