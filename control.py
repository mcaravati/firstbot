from abstract_control import AbstractControl
from math import *
import pypot.dynamixel
from time import sleep, time
import threading


#distance entre les deux roues en mètre
wheels_distance = 0.18
#rayon en m 
r = 0.026
dt = 0.01

class NormalControl(AbstractControl):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ports = pypot.dynamixel.get_available_ports()

        if not ports:
            exit('No port')

        self.dxl_io = pypot.dynamixel.DxlIO(ports[0])
        self.dxl_io.set_wheel_mode([2, 5])
        self.speed = 1
        self.start_background_odo()
        print("[+] Control initialized")
    

    def move(self, v_line, v_rot):
        v_left = v_line - v_rot * wheels_distance / 2
        v_right = v_line + v_rot * wheels_distance / 2
        self.dxl_io.set_moving_speed({2: v_left})
        self.dxl_io.set_moving_speed({5: -v_right})
        
    def forward(self):
        """ self.dxl_io.set_moving_speed({2: 360 * self.speed})
        self.dxl_io.set_moving_speed({5: -360 * self.speed}) """
        self.move(360*self.speed, 0)
        print("[+] Control forward")

    def backward(self):
        """ self.dxl_io.set_moving_speed({2: -360*self.speed})
        self.dxl_io.set_moving_speed({5: 360*self.speed}) """
        self.move(-360*self.speed, 0)
        print("[+] Control backward")

    def left(self):
        """ self.dxl_io.set_moving_speed({2: 180*self.speed})
        self.dxl_io.set_moving_speed({5: -360*self.speed}) """
        self.move(180, 360*self.speed)
        print("[+] Control left")

    def right(self):
        """ self.dxl_io.set_moving_speed({2: 360*self.speed})
        self.dxl_io.set_moving_speed({5: -180*self.speed}) """
        self.move(180, -360*self.speed)
        print("[+] Dummy control right")

    def stop(self):
        self.move(0, 0)
        self.dxl_io.disable_torque([2, 5])
        print("[+] Dummy control stop")
    
    def set_speed(self, sp):
        self.speed = sp
    
    def goto(self, x, y, w):
        #compute the angle to turn
        self._theta = atan2(sin(self._theta), cos(self._theta))
        theta_to_go = atan2(y-self._y, x-self._x)
        print("theta", theta_to_go)
        #compute the distance to travel
        distance = sqrt((x-self._x)**2 + (y-self._y)**2)
        print("distance", distance)
        #compute the angle to turn
        angle = theta_to_go - self._theta
        print("angle", angle)
        #turn
        while abs(angle) >= 0.0001:
            if theta_to_go > self._theta:
                self.move(0, -360 * self.speed)
            else:
                self.move(0, 360 * self.speed)

            angle = theta_to_go - self._theta
            print("error angle:",abs(angle))
        #move
        dist = 1
        while dist >= 0.01:
            if angle < 0:
                self.move(100+ 500 * self.speed * dist, -720 * angle * self.speed)
            else:
                self.move(100+ 500 * self.speed * dist, 720 * angle * self.speed)
            last_dist = dist
            angle = theta_to_go - self._theta
            dist = sqrt((x-self._x)**2 + (y-self._y)**2)
            print(dist, last_dist)
            print("error distance:", dist)
        #stop
        self.stop()

    def start_background_odo(self):
        # Créer et démarrer un thread pour exécuter background_odo en arrière-plan
        self.odo_thread = threading.Thread(target=self.background_odo_loop, daemon=True)
        self.odo_thread.start()
    
    def background_odo_loop(self):
        # Boucle infinie pour continuer à mettre à jour l'odométrie en arrière-plan
        self._tps = time()
        while True:
            self.background_odo()
            sleep(dt) 

    def background_odo(self):
        left_speed, right_speeds = self.wheel_speed()
        v, theta = self.direct_kinematics(left_speed, right_speeds)
        rdt = time()-self._tps
        self._tps = time()
        self._theta += theta*rdt
        self._x += v * rdt * cos(self._theta)
        self._y += v * rdt * sin(self._theta)
        #print(f"V: {round(v,2):<5}, theta: {round(self._theta, 2):<5}")

    def compute_odometry(self):
        return (self._x, self._y, self._theta)

    # function to compute the rotation speed in rad/s of motor 2
    def wheel_speed(self):
        v_left = self.dxl_io.get_present_speed([2])[0]*pi/180
        v_right = self.dxl_io.get_present_speed([5])[0]*pi/180
        #print(f"v_left: {round(v_left[0], 2):<5}, v_right: {round(v_right[0], 2):<5}")

        return v_left, -v_right

    #v_gauche et _droite sont en rad/s
    def direct_kinematics (self, v_left, v_right):
        v_robot = (v_left + v_right) / 2

        v = v_robot*r #en m/s

        omega = r * (v_left - v_right) / wheels_distance
        #print(f"v_left: {round(v_left, 2):<5}, v_right: {round(v_right, 2):<5}, tet: {round(self._theta, 2):<5}, v: {round(v, 2):<5}")

        return v, omega

    def reset_odometry(self):
        return super().reset_odometry()