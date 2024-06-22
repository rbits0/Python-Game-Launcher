from typing import Any, Optional
from PySide6.QtCore import QAbstractAnimation, QPropertyAnimation, QObject, Property


class CoupledPropertyAnimation(QPropertyAnimation):
    '''
    Animation that switches the values of 2 properties. Properties must be ints.
    
    You can change the start and end value of property 1 by calling setStartValue and setEndValue.
    These are also the end value and the start value respectively of property 2.
    '''
    
    def __init__(
        self,
        target1: QObject,
        propertyName1: str,
        target2: QObject,
        propertyName2: str,
        parent: Optional[QObject] = None
    ) -> None:
        if (
            not isinstance(target1.property(propertyName1), int)
        ) or (
            not isinstance(target2.property(propertyName2), int)
        ):
            raise TypeError("Properties must be of type int")
        
        
        self.coupledProperty = _CoupledProperty(target1, propertyName1, target2, propertyName2, parent)
        
        self.startManuallySet = False
        self.endManuallySet = False
        self._initialiseValues()

        super().__init__(self.coupledProperty, b'coupledProperty', parent)

    
    def _initialiseValues(self) -> None:
        '''
        Gets the start values (which are also the end values) from the properties.
        Do not call this after the animation has already started.
        
        Will not set value if already set manually
        (via setStartValue or setEndValue).
        '''
        if not self.startManuallySet:
            startValue: int = self.coupledProperty.target1.property(
                self.coupledProperty.propertyName1
            )
            self.coupledProperty.setStartValue(startValue)
            
        if not self.endManuallySet:
            endValue: int = self.coupledProperty.target2.property(
                self.coupledProperty.propertyName2
            )
            self.coupledProperty.setEndValue(endValue)
        
    
    def _onStart(self) -> None:
        # Doing this here as well as __init__ in case property is changed after CoupledPropertyAnimation is already created
        self._initialiseValues()

        super().setStartValue(self.coupledProperty.startValue)
        super().setEndValue(self.coupledProperty.endValue)
    
    def updateState(self, newState: QAbstractAnimation.State, oldState: QAbstractAnimation.State) -> None:
        # If state changed to Running
        if oldState != QAbstractAnimation.State.Running and newState == QAbstractAnimation.State.Running:
            self._onStart()

        super().updateState(newState, oldState)


    # Start and end value is stored in coupledProperty, and actually set when the animation is started.
    # This is so I can set them in __init__ before the object is initialised

    def setStartValue(self, value: int) -> None:
        self.coupledProperty.setStartValue(value)
        self.startManuallySet = True

    def setEndValue(self, value: int) -> None:
        self.coupledProperty.setEndValue(value)
        self.endManuallySet = True
            



class _CoupledProperty(QObject):
    def __init__(
        self,
        target1: QObject,
        propertyName1: str,
        target2: QObject,
        propertyName2: str,
        parent: Optional[QObject] = None
    ):
        self.target1 = target1
        self.propertyName1 = propertyName1
        self.target2 = target2
        self.propertyName2 = propertyName2
        
        self.startValue: Optional[int] = None
        '''Start value of property 1'''

        self.endValue: Optional[int] = None
        '''End value of property 1 (start value of property 2)'''
        
        super().__init__(parent)
    
    
    def setStartValue(self, value: int) -> None:
        '''
        Sets the start value of property 1.
        You should not call this after the animation has already started.
        '''
        self.startValue = value
        self._coupledProperty = value

    def setEndValue(self, value: int) -> None:
        'Sets the end value of property 1 (start value of property 2)'
        self.endValue = value
        
        
    @Property(int)
    def coupledProperty(self) -> int:
        return self._coupledProperty
    
    @coupledProperty.setter # type: ignore
    def coupledProperty(self, value: int) -> None:
        assert self.startValue is not None and self.endValue is not None, 'Must set start values for CoupledProperty'
        
        self.target1.setProperty(self.propertyName1, value)
        
        differenceSinceStart = value - self.startValue
        property2Value = self.endValue - differenceSinceStart
        self.target2.setProperty(self.propertyName2, property2Value)

        self._coupledProperty = value