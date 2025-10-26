import socket
import threading
import time
from ags import KICK, QUESTION, REPLY, ECHO, PING, decode, encode

class GameClient:
    def __init__(self, host=None, port=5555):
        if host:
            if len(host.split('.')) == 1:
                host = "192.168.0." + host
        else:
            host = socket.gethostname()
            
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def receive(self):
        msg_type = ""
        msg_txt = ""
        while True:
            response = self.client_socket.recv(1024).decode('utf-8')
            msg_type, msg_txt = decode(response)
            if msg_type != PING:
                break
            #print("\n###\nPING\n###\n")
        return msg_type, msg_txt

    def send(self, msg_type, msg_txt = ""):
        self.client_socket.send(encode(msg_txt, msg_type).encode('utf-8'))

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print("Connected to the server!")
            self.running = True

            # Start the connection verification thread
            #threading.Thread(target=self.verify_connection, daemon=True).start()

            while self.running:
                msg_type, msg_txt = self.receive()

                if msg_txt != "":
                    print(msg_txt, end="")

                if msg_type == KICK:
                    self.running = False
                    continue

                if msg_type == QUESTION:
                    self.send(REPLY, input())
                    continue

            self.disconnect()

        except Exception as e:
            print(f"Connection error: {e}")

    def verify_connection(self):
        while self.running:
            try:
                self.send(PING)
                time.sleep(1)
            except Exception as e:
                print(f"Connection verification failed: {e}")
                self.running = False
                self.disconnect()
                break

    def disconnect(self):
        self.running = False
        try:
            self.client_socket.close()
            print("Disconnected from the server.")
        except Exception as e:
            print(f"Error while disconnecting: {e}")

if __name__ == "__main__":
    client = GameClient(input("Enter server ip: "))
    client.connect()
