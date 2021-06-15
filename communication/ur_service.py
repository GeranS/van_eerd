import socket
from enum import Enum
import _thread
from functools import partial

from conversion_service import ConversionService

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

    def send_command_to_ur(self, command, params=None):
        switch = {
            URCommand.grab_stack: partial(self.__grab_stack, params),
            URCommand.safe_position: self.__safe_position,
            URCommand.grab_sheet: self.__grab_sheet
        }

        function = switch.get(command)
        return function()

    def __grab_stack(self, stack):
        conversion_service = ConversionService.get_instance()
        x, y, z = stack.x, stack.y, stack.z
        x = x + stack.w/2
        y = y + stack.h/2
        x, y, z = conversion_service.convert_to_robot_coordinates(x, y, z)

        self.robot_client.send("PICK".encode())
        self.robot_client.send([x, y, z])

    def __grab_sheet(self):
        pass

    def __safe_position(self):
        pass


class URCommand(Enum):
    grab_stack = 1
    grab_sheet = 2
    safe_position = 3
