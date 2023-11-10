from abstract_server import AbtractServer
from websockets import serve, broadcast
import asyncio
import json

class WebSocketServer(AbtractServer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._websocket_server = None
        self._function_map = {
            'forward': self._forward,
            'backward': self._backward,
            'left': self._left,
            'right': self._right,
            'stop': self._stop,
            'odometry': self._send_odometry,
            'goto': self._goto,
            'set_speed': self._set_speed
        }

    async def _server_wrapper(self):
        async with serve(self._message_handler, "0.0.0.0", 8080):
            await asyncio.Future()
        
    def start(self):
        asyncio.get_event_loop().run_until_complete(self._server_wrapper())

    def stop(self):
        self._websocket_server.shutdown()

    async def _message_handler(self, websocket):
        async for message in websocket:
            json_data = json.loads(message)
            function_args = json_data['data'] if 'data' in json_data else None

            if json_data['type'] in self._function_map:
                await self._function_map[json_data['type']](websocket, function_args)

    async def _forward(self, websocket, args):
        return self._robot_control.forward()

    async def _backward(self, websocket, args):
        return self._robot_control.backward()

    async def _left(self, websocket, args):
        return self._robot_control.left()

    async def _right(self, websocket, args):
        return self._robot_control.right()

    async def _stop(self, websocket, args):
        return self._robot_control.stop()

    async def _send_odometry(self, websocket):
        x, y, theta = self._robot_control.compute_odometry()
        
        # Construire et envoyer le message
        response = {
            'type': 'odometry',
            'data': {
                'x': x,
                'y': y,
                'theta': theta
            }
        }

        await websocket.send(json.dumps(response))

    async def _goto(self, websocket, args):
        return self._robot_control.goto(args['x'], args['y'], args['theta'])
        