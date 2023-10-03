from websocket_server import WebSocketServer
from control import NormalControl

server = WebSocketServer(robot_control=NormalControl())
server.start()