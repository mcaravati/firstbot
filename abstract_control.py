from abc import ABC, abstractmethod

class AbstractControl(ABC):
    def __init__(self):
        self._x = 0
        self._y = 0

    @abstractmethod
    def forward(self):
        pass

    @abstractmethod
    def backward(self):
        pass

    @abstractmethod
    def left(self):
        pass

    @abstractmethod
    def right(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def compute_odometry(self):
        pass

