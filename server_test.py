# server.py
import socket
import threading
import time
from ags import QUESTION, REPLY, ECHO, PING, KICK, msg, signal, decode

class GameServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.running = False
        
    def handle_client(self, client_socket, client_address):
          
        print(f"New connection from {client_address}")
        self.clients.append(client_socket)
        
        try:
            while self.running:
                question = "What is your name? "
                client_socket.send(msg(question, QUESTION).encode('utf-8'))
                time.sleep(0.01)

                response = client_socket.recv(1024).decode('utf-8')
                if not response:
                    break
                    
                msg_type, msg_txt = decode(response)
                if msg_type == REPLY:
                    name = msg_txt if msg_txt != "" else "Anonymous"
                    print(f"Client {client_address} says their name is: {name}")
                    
                    echo_msg = f"Hello, {name}! Welcome to the game server."
                    client_socket.send(msg(echo_msg).encode('utf-8'))
                    time.sleep(0.01)

                    client_socket.send(signal().encode('utf-8'))
                    time.sleep(0.01)
                    
                    
                    question2 = "How are you today? "
                    client_socket.send(msg(question2, QUESTION).encode('utf-8'))
                    time.sleep(0.01)
                      
                    response2 = client_socket.recv(1024).decode('utf-8')
                    msg_type2, msg_txt2 = decode(response2)
                    if msg_type2 == REPLY:
                        mood = msg_txt2 if msg_txt2 != "" else "No response"
                        print(f"Client {name} is feeling: {mood}")
                        
                          
                        goodbye_msg = "Thank you for testing! Connection will be closed."
                        client_socket.send(msg(goodbye_msg).encode('utf-8'))
                        time.sleep(0.01)
                        client_socket.send(signal(KICK).encode('utf-8'))
                        time.sleep(0.01)
                        break
                        
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            self.clients.remove(client_socket)
            client_socket.close()
            print(f"Connection with {client_address} closed")
    
    def start(self):
         
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True
        
        print(f"Game server started on {self.host}:{self.port}")
        print("Waiting for connections...")
        
        try:
            while self.running:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nServer is shutting down...")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
    
    def stop(self):
         
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        try:
            self.server_socket.close()
        except:
            pass
        print("Server stopped")

if __name__ == "__main__":
    server = GameServer()
    server.start()