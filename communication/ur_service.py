import socket
from enum import Enum
import _thread

robot_client_ip = "192.168.0.4"
robot_client_port = 22

port = 8000


class URService:
    def __init__(self, pick_logic):
        self.pick_logic = pick_logic

        host = socket.gethostname()
        self.robot_socket = socket.socket()
        self.robot_socket.bind((host, port))

        self.robot_client = self.connect_to_ur()

        _thread.start_new_thread(self.listen_for_messages, ())

    def connect_to_ur(self):
        pass

    def listen_for_messages(self):
        while 1:
            try:
                message = self.robot_client.recv(1024).decode()
            except ConnectionResetError as e:
                print("Error while receiving data from robot. Error message: ", str(e))
                break

            if not message:
                break

            print("UR: " + str(message))

            # todo: switch case here

    def send_command_to_ur(self, command):
        switch = {
            URCommand.grab_stack: self.__grab_stack,
            URCommand.place_stack: self.__place_stack,
            URCommand.safe_position: self.__safe_position
        }

        function = switch.get(command)
        return function()

    def __grab_stack(self):
        pass

    def __place_stack(self):
        pass

    def __safe_position(self):
        pass


class URCommand(Enum):
    grab_stack = 1
    place_stack = 2
    safe_position = 3
