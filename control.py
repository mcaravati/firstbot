from abstract_control import AbstractControl
import pypot.dynamixel
from utils import *
from math import *

class NormalControl(AbstractControl):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ports = pypot.dynamixel.get_available_ports()

        if not ports:
            exit('No port')

        self.dxl_io = pypot.dynamixel.DxlIO(ports[0])
        self.dxl_io.set_wheel_mode([2, 5])
        print("[+] Control initialized")
        
    def forward(self):
        self.dxl_io.set_moving_speed({2: 360})
        self.dxl_io.set_moving_speed({5: -360})
        print("[+] Control forward")

    def backward(self):
        self.dxl_io.set_moving_speed({2: -360})
        self.dxl_io.set_moving_speed({5: 360})
        print("[+] Control backward")

    def left(self):
        self.dxl_io.set_moving_speed({2: 180})
        self.dxl_io.set_moving_speed({5: -360})
        print("[+] Control left")

    def right(self):
        self.dxl_io.set_moving_speed({2: 360})
        self.dxl_io.set_moving_speed({5: -180})
        print("[+] Dummy control right")

    def stop(self):
        self.dxl_io.set_moving_speed({2: 0})
        self.dxl_io.set_moving_speed({5: 0})
        self.dxl_io.disable_torque([2, 5])
        print("[+] Dummy control stop")

    def compute_odometry(self):
        # Récupérer les données odométriques
        dt = 0.01

        left = left_wheel_speed()
        right = right_wheel_speed()

        v, theta = direct_kinematics(left, right)
        self._x += v * dt * math.cos(theta)
        self._y += v * dt * math.sin(theta)

        return (self._x, self._y, theta)