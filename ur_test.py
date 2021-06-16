import socket
import _thread
import time

robot_client_ip = "192.168.0.4"
robot_client_port = 22

port = 8000

host = socket.gethostname()
robot_socket = socket.socket()
robot_socket.bind((host, port))
robot_socket.listen(2)

# example: [-0.090, 0.588, 0, 0, 0, 0]

def listen_for_robot_messages():
    while 1:
        try:
            message = robot_client.recv(1024).decode()
        except ConnectionResetError as e:
            print("Error while receiving data from robot. Error message: ", str(e))
            break

        if not message:
            break

        print("UR: " + str(message))


conn, _ = robot_socket.accept()
robot_client = conn

_thread.start_new_thread(listen_for_robot_messages, ())

while 1:
    message = input('>')

    if message == "PICK":
        robot_client.send("PICK".encode())
        time.sleep(0.1)
        message_to_send = '({x:.4f},{y:.4f},{z:.4f},{rx:.4f})'.format(x=-0.26, y=0.682, z=0.0810, rx=90.0000)
        #robot_socket.send('(-0.0900,0.5880,0.0000,0.0000)'.encode())
        robot_client.send(message_to_send.encode())
    else:
        robot_client.send(message.encode())

