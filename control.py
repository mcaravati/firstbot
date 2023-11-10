from abstract_control import AbstractControl
from math import *
import pypot.dynamixel
from time import sleep, time
import threading
from vision import *


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
        self.speed = 0.25
        self.start_background_odo()
        print("[+] Control initialized")
    

    def move(self, v_line, v_rot):
        """ v_left = v_line - v_rot * wheels_distance / 2
        v_right = v_line + v_rot * wheels_distance / 2
        v_left = v_left*180/pi
        v_right = v_right*180/pi
        self.dxl_io.set_moving_speed({2: v_left})
        self.dxl_io.set_moving_speed({5: -v_right}) """
        # Calculate wheel velocities in m/s
        v_R = v_line + (v_rot * wheels_distance) / 2
        v_L = v_line - (v_rot * wheels_distance) / 2
        
        # Convert wheel velocities to deg/s
        v_R_deg = -v_R * (360 / (2 * pi * r))
        v_L_deg = v_L * (360 / (2 * pi * r))

        self.dxl_io.set_moving_speed({2: v_L_deg})
        self.dxl_io.set_moving_speed({5: v_R_deg})

        
    def forward(self):
        """ self.dxl_io.set_moving_speed({2: 360 * self.speed})
        self.dxl_io.set_moving_speed({5: -360 * self.speed}) """
        self.move(self.speed, 0)
        print("[+] Control forward")

    def backward(self):
        """ self.dxl_io.set_moving_speed({2: -360*self.speed})
        self.dxl_io.set_moving_speed({5: 360*self.speed}) """
        self.move((-self.speed), 0)
        print("[+] Control backward")

    def left(self):
        """ self.dxl_io.set_moving_speed({2: 180*self.speed})
        self.dxl_io.set_moving_speed({5: -360*self.speed}) """
        self.move(self.speed*0 ,2*self.speed)
        print("[+] Control left")

    def right(self):
        """ self.dxl_io.set_moving_speed({2: 360*self.speed})
        self.dxl_io.set_moving_speed({5: -180*self.speed}) """
        self.move(self.speed*0, -2*self.speed)
        print("[+] Dummy control right")

    def stop(self):
        self.move(0, 0)
        self.dxl_io.disable_torque([2, 5])
        print("[+] Dummy control stop")
    
    def set_speed(self, sp):
        self.speed = sp

    def goto(self, x, y, w):
        self.goto_thread = threading.Thread(target=self.background_goto, args=(x, y, w), daemon=True)
        self.goto_thread.start()

    
    def background_goto(self, x, y, w):
        #compute the angle to turn
        theta_to_go = atan2(y-self._y, x-self._x)
        print("theta", theta_to_go)
        #compute the distance to travel
        distance = sqrt((x-self._x)**2 + (y-self._y)**2)
        print("distance", distance)
        #compute the angle to turn
        angle = (theta_to_go - self._theta) % pi
        last_angle = inf
        print("angle", angle)
        #turn
        while abs(angle) >= 0.01 or last_angle < angle:
            self._theta = atan2(sin(self._theta), cos(self._theta))
            angle = theta_to_go - self._theta
            angle = atan2(sin(angle), cos(angle))
            last_angle = angle
            self.move(0, -0.5 * angle + 0.2)

            print(f"error angle: {abs(angle):<5}",end="\r")
        #move
        dist = inf
        last_dist = inf
        while  last_dist >= dist or dist >= 0.1:
            self._theta = atan2(sin(self._theta), cos(self._theta))
            theta_to_go = atan2(y-self._y, x-self._x)
            angle = theta_to_go - self._theta
            angle = atan2(sin(angle), cos(angle))

            self.move(0.1+self.speed * dist, -angle)
            last_dist = dist
            dist = sqrt((x-self._x)**2 + (y-self._y)**2)
            print(f"dist: {round(dist, 3):<5}, angle {round(angle,3):<5}", end="\r")
        
        angle = (w - self._theta) % pi
        last_angle = inf
        #turn
        while abs(angle) >= 0.01 or last_angle < angle:
            self._theta = atan2(sin(self._theta), cos(self._theta))
            angle = w - self._theta
            angle = atan2(sin(angle), cos(angle))
            last_angle = angle
            self.move(0, -0.5 * angle + 0.2)


            print(f"error angle: {abs(angle):<5}",end="\r")
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
        #print(f"V: {round(v,2):<5}, x: {round(self._x, 2):<5}")

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

    def background_track(self):
        track = True
        curr_col = 1 #1 = black; 0 = green; -1 = stop
        # old_calc = 0 #backup action
        while track:
            image = capture()
            percent = compute_black(image) if curr_col == 1 else compute(image)
            self.move(self.speed*(1-abs(percent/100)), (-percent)/50)
            # print(curr_col)
            # print(percent, detect[curr_col], f"old : {old_calc}")
            # old_calc = percent
            curr_col = swap(image, curr_col)
            track = curr_col >= 0
        self.move(0, 0)
    
    def track_line(self):
        self.track_thread = threading.Thread(target=self.background_track, daemon=True)
        self.track_thread.start()
        
