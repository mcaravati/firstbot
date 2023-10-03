from abstract_server import AbtractServer
from websockets import serve
import asyncio
import json
import pypot.dynamixel
from utils import *
from math import *

class WebSocketServer(AbtractServer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._websocket_server = None
        self._function_map = {
            'forward': self._forward,
            'backward': self._backward,
            'left': self._left,
            'right': self._right,
            'stop': self._stop
        }

    async def _server_wrapper(self):
        async with serve(self._message_handler, "0.0.0.0", 8080):
            await asyncio.Future()
    
    async def send_odometry(self, websocket, path):
        x = 0
        y = 0
        while True:
            # Récupérer les données odométriques
            dt = 0.01
            left = left_wheel_speed()
            right = right_wheel_speed()
            v, theta = direct_kinematics(left, right)
            x += v * dt * math.cos(theta)
            y += v * dt * math.sin(theta)
            
            # Construire et envoyer le message
            response = {
                'status': 'odometry',
                'odometry': {
                    'x': x,
                    'y': y,
                    'theta': theta
                }
            }
            await websocket.send(json.dumps(response))
            await asyncio.sleep(0.01)  # Attendre 0,01 secondes
        

    def start(self):
        asyncio.get_event_loop().run_until_complete(self._server_wrapper())
        asyncio.get_event_loop().run_until_complete(self.send_odometry())

    def stop(self):
        self._websocket_server.shutdown()

    async def _message_handler(self, websocket):
        async for message in websocket:
            json_data = json.loads(message)

            if json_data['type'] in self._function_map:
                self._function_map[json_data['type']]()

    def _forward(self):
        return self._robot_control.forward()

    def _backward(self):
        return self._robot_control.backward()

    def _left(self):
        return self._robot_control.left()

    def _right(self):
        return self._robot_control.right()

    def _stop(self):
        return self._robot_control.stop()