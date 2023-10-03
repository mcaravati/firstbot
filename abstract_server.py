from abc import ABC, abstractmethod
from abstract_control import AbstractControl

class AbtractServer(ABC):
    def __init__(self, **kwargs):
        super().__init__()

        self._robot_control: AbstractControl = kwargs.get("robot_control", None)

        if self._robot_control is None:
            raise ValueError("robot_control is required")
        elif not isinstance(self._robot_control, AbstractControl):
            raise ValueError("robot_control must be an instance of AbstractControl")

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

