from websocket_server import WebSocketServer
from dummy_control import DummyControl

server = WebSocketServer(robot_control=DummyControl())
server.start()