from abstract_control import AbstractControl
from random import randint

class DummyControl(AbstractControl):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("[+] Dummy control initialized")
        
    def forward(self):
        print("[+] Dummy control forward")

    def backward(self):
        print("[+] Dummy control backward")

    def left(self):
        print("[+] Dummy control left")

    def right(self):
        print("[+] Dummy control right")

    def stop(self):
        print("[+] Dummy control stop")

    def compute_odometry(self):
        print("[+] Dummy control odometry")

        x = randint(0, 699)
        y = randint(0, 699)
        theta = randint(0, 360)

        return (x, y, theta)

