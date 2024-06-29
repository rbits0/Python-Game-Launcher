from typing import Any, Optional
from PySide6.QtCore import QAbstractAnimation, QPropertyAnimation, QObject, Property


class CoupledPropertyAnimation(QPropertyAnimation):
    '''
    Animation that animates the values of 2 properties. Properties must be ints.
    
    Ensures that if each property has the same range, they both change at the exact same rate each frame
    
    You must the start and end value of properties by calling setStartValues and setEndValues.
    '''
    
    def __init__(
        self,
        target1: QObject,
        propertyName1: str,
        target2: QObject,
        propertyName2: str,
        parent: Optional[QObject] = None
    ) -> None:
        '''
        Initialise CoupledPropertyAnimation

        Args:
            target1: Object with property 1
            propertyName1: Name of property 1
            target2: Object with property 2
            propertyName2: Name of property 2
            parent: Parent object. Defaults to None

        Raises:
            TypeError: Properties are not of type int
        '''        
        if (
            not isinstance(target1.property(propertyName1), int)
        ) or (
            not isinstance(target2.property(propertyName2), int)
        ):
            raise TypeError("Properties must be of type int")
        

        self.coupledProperty = _CoupledProperty(target1, propertyName1, target2, propertyName2, parent)
        
        
        super().__init__(self.coupledProperty, b'coupledProperty', parent)

    
    def _onStart(self) -> None:
        if self.startValue() is None or self.endValue() is None:
            raise RuntimeError('Must set start and end values')
    
    def updateState(self, newState: QAbstractAnimation.State, oldState: QAbstractAnimation.State) -> None:
        # If state changed to Running
        if oldState != QAbstractAnimation.State.Running and newState == QAbstractAnimation.State.Running:
            self._onStart()

        super().updateState(newState, oldState)


    def setStartValues(self, value1: int, value2: int) -> None:
        '''
        Set the start values

        Args:
            value1: Start value of property 1
            value2: Start value of property 2
        '''        
        
        self.coupledProperty.setStartValues(value1, value2)
        super().setStartValue(value1)

    def setEndValues(self, value1: int, value2: int) -> None:
        '''
        Set the start values

        Args:
            value1: Start value of property 1
            value2: Start value of property 2
        '''        

        self.coupledProperty.setEndValues(value1, value2)
        super().setEndValue(value1)

    def setStartValue(self, value: int) -> None:
        '''
        Set both start values to value
        
        Not intended to be used, it is only included for compatibility with QPropertyAnimation.
        '''
        self.setStartValues(value, value)
    
    def setEndValue(self, value: int) -> None:
        '''
        Set both end values to value
        
        Not intended to be used, it is only included for compatibility with QPropertyAnimation.
        '''
        self.setEndValues(value, value)
            



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
        
        self._coupledProperty: Optional[int] = None
        self.startValue1: Optional[int] = None
        self.endValue1: Optional[int] = None
        self.startValue2: Optional[int] = None
        self.endValue2: Optional[int] = None
        
        self.value2Ratio: Optional[float] = None
        'Ratio of property2 range to property 1 range'
        
        super().__init__(parent)
    
    
    def setStartValues(self, value1: int, value2: int) -> None:
        '''
        Sets the start value of properties
        You should not call this after the animation has already started.
        '''

        self.startValue1 = value1
        self.startValue2 = value2

        self._coupledProperty = value1

    def setEndValues(self, value1: int, value2: int) -> None:
        'Sets the end value of properties'
        self.endValue1 = value1
        self.endValue2 = value2

    def calculateValues(self) -> None:
        '''
        Calculate values once based on start and end values,
        so we don't have to calculate them every frame.
        '''
        # I don't know if this is even necessary, but why not

        assert (
            self._coupledProperty is not None and
            self.startValue1 is not None and
            self.endValue1 is not None and
            self.startValue2 is not None and
            self.endValue2 is not None
        ), '''
            Must set start and end values for CoupledProperty
        '''

        value1Range = self.endValue1 - self.startValue1
        value2Range = self.endValue2 - self.startValue2
        self.value2Ratio = value2Range / value1Range
        
        
    @Property(int)
    def coupledProperty(self) -> int:
        return self._coupledProperty
    
    @coupledProperty.setter # type: ignore
    def coupledProperty(self, value: int) -> None:
        assert (
            self._coupledProperty is not None and
            self.startValue1 is not None and
            self.endValue1 is not None and
            self.startValue2 is not None and
            self.endValue2 is not None
        ), '''
            Must set start and end values for CoupledProperty
        '''
        
        if self.value2Ratio is None:
            self.calculateValues()
            assert self.value2Ratio is not None
        
        # Set property 1
        self.target1.setProperty(self.propertyName1, value)
        
        # Set property 2
        differenceSinceStart = value - self.startValue1
        property2Value = self.startValue2 + int(self.value2Ratio * differenceSinceStart)
        self.target2.setProperty(self.propertyName2, property2Value)

        self._coupledProperty = value