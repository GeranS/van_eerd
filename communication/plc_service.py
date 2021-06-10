import socket
import time
import _thread

plc_client_ip = "192.168.0.1"
plc_client_port = 2000


class PLCService:
    def __init__(self, pick_logic):
        self.pick_logic = pick_logic

        self.socket_plc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__connect_to_plc()

    def __connect_to_plc(self):
        while True:
            print("Connecting to PLC...")
            try:
                self.socket_plc = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.socket_plc.connect((plc_client_ip, plc_client_port))
                break
            except Exception as e:
                print("Failed to connect to PLC. Trying again in one second.")
                print(e)
                time.sleep(1)

    def __listen_for_plc_messages(self):
        while 1:
            try:
                message = self.socket_plc.recv(1024)
            except ConnectionResetError as e:
                print("Error while receiving data from PLC. Error message: ", str(e))
                break
            except Exception as e:
                print(e)
                break

            if not message:
                print("PLC message is none.")
                break

            if len(message) == 2:
                # todo: use messages to do things
                pass