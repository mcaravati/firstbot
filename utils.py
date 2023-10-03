from math import *

# function to compute the rotation speed in rad/s of motor 2
def left_wheel_speed():
    pos1 = dxl_io.get_present_position([2])
    sleep(0.01)
    pos2 = dxl_io.get_present_position([2])
    return ((pos2[0]-pos1[0])/0.01)*pi/180

def right_wheel_speed():
    pos1 = dxl_io.get_present_position([5])
    sleep(0.01)
    pos2 = dxl_io.get_present_position([5])
    return ((pos2[0]-pos1[0])/-0.01)*pi/180

#v_gauche et _droite sont en rad/s
def direct_kinematics (v_gauche, v_droite):
    if v_gauche != v_droite:
        v_min = min(v_gauche, v_droite)
        x = v_min*r #en m/s
        teta = (v_gauche - v_droite)*r/wheels_distance #en rad/s
    else:
        x = v_gauche*r
        teta = 0
    return [x, teta]