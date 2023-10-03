from abstract_control import AbstractControl

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
