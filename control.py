from abstract_control import AbstractControl

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
