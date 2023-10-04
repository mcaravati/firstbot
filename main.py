from websocket_server import WebSocketServer
from dummy_control import DummyControl
# from control import NormalControl

server = WebSocketServer(robot_control=DummyControl())
server.start()