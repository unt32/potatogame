import socket
import threading
from ags import KICK, QUESTION, REPLY, ECHO, PING, decode, msg

class gameClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def receive(self):
        msg_type, msg_txt = decode(self.client_socket.recv(1024).decode('utf-8'))
        return msg_type, msg_txt

    def send(self, txt):
        self.client_socket.send(msg(txt, REPLY).encode('utf-8'))
    
    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print("Connected to the server!")

            while True:
                msg_type, msg_txt = self.receive()

                if msg_type == KICK:
                    break

                if msg_type == ECHO:
                    print(msg_txt)
                    continue

                if msg_type == QUESTION:
                    self.send(input(msg_txt))
                    continue
            
            self.disconnect()

        except Exception as e:
            print(f"Connection error: {e}")

    def disconnect(self):
        try:
            self.client_socket.close()
            print("Disconnected from the server.")
        except Exception as e:
            print(f"Error while disconnecting: {e}")

if __name__ == "__main__":
    client = gameClient()
    client.connect()