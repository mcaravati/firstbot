from abstract_control import AbstractControl
from math import *
import pypot.dynamixel
from time import sleep


#distance entre les deux roues en mètre
wheels_distance = 0.18
#rayon en m 
r = 0.025

class NormalControl(AbstractControl):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ports = pypot.dynamixel.get_available_ports()

        if not ports:
            exit('No port')

        self.dxl_io = pypot.dynamixel.DxlIO(ports[0])
        self.dxl_io.set_wheel_mode([2, 5])
        self.speed = 1
        
        print("[+] Control initialized")
        
    def forward(self):
        self.dxl_io.set_moving_speed({2: 360*self.speed})
        self.dxl_io.set_moving_speed({5: -360*self.speed})
        print("[+] Control forward")

    def backward(self):
        self.dxl_io.set_moving_speed({2: -360*self.speed})
        self.dxl_io.set_moving_speed({5: 360*self.speed})
        print("[+] Control backward")

    def left(self):
        self.dxl_io.set_moving_speed({2: 180*self.speed})
        self.dxl_io.set_moving_speed({5: -360*self.speed})
        print("[+] Control left")

    def right(self):
        self.dxl_io.set_moving_speed({2: 360*self.speed})
        self.dxl_io.set_moving_speed({5: -180*self.speed})
        print("[+] Dummy control right")

    def stop(self):
        self.dxl_io.set_moving_speed({2: 0})
        self.dxl_io.set_moving_speed({5: 0})
        self.dxl_io.disable_torque([2, 5])
        print("[+] Dummy control stop")

    def compute_odometry(self):
        dt = 0.02

        left, right = self.wheel_speed()

        # Filtrer les vitesses aberrantes
        if abs(left) < self.left_avg+self.speed_threshold:
            self.left_speeds.append(left)
        if abs(right) < self.right_avg + self.speed_threshold:
            self.right_speeds.append(right)

        # Maintenir la taille de la fenêtre pour la moyenne mobile
        self.left_speeds = self.left_speeds[-self.speed_window_size:]
        self.right_speeds = self.right_speeds[-self.speed_window_size:]

        # Calculer la moyenne mobile des vitesses
        self.left_avg = sum(self.left_speeds) / len(self.left_speeds)
        self.right_avg = sum(self.right_speeds) / len(self.right_speeds)


        v, theta = self.direct_kinematics(self.left_speeds[-1], self.right_speeds[-1])
        self._theta += theta*dt
        self._x += v * dt * cos(self._theta)
        self._y += v * dt * sin(self._theta)
        print(f"Filtered left: {round(self.left_avg,2):<5}, Filtered right: {round(self.right_avg, 2):<5}, Theta: {round(theta, 2):<5}")

        return (self._x, self._y, self._theta)

    # function to compute the rotation speed in rad/s of motor 2
    def wheel_speed(self):
        pos1_l = self.dxl_io.get_present_position([2])
        pos1_r = self.dxl_io.get_present_position([5])
        sleep(0.02)
        pos2_l = self.dxl_io.get_present_position([2])
        pos2_r = self.dxl_io.get_present_position([5])
        v_left = ((pos2_l[0]-pos1_l[0])/0.02)*pi/180
        v_right = ((pos2_r[0]-pos1_r[0])/-0.02)*pi/180

        return v_left, v_right

    #v_gauche et _droite sont en rad/s
    def direct_kinematics (self, v_left, v_right):
        v = r * (v_left + v_right) / 2
        omega = r * (v_left - v_right) / wheels_distance

        return v, omega