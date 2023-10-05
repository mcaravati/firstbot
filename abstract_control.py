from abc import ABC, abstractmethod

class AbstractControl(ABC):
    def __init__(self):
        self._theta = 0
        self._x = 0
        self._y = 0
        self.left_avg = 0
        self.right_avg = 0
        self.left_speeds = []
        self.right_speeds = []
        self.speed_window_size = 5  # Taille de la fenêtre pour la moyenne mobile
        self.speed_threshold = 50  # Seuil de tolérance pour les valeurs aberrantes

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

