import socket
import threading
import time
import random
from ags import QUESTION, REPLY, PING, KICK, ECHO, encode, decode

class GameServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.players = {}
        self.voted = {}
        self.game_running = False
        self.curr_ans = ""
        self.answered = False

    def sendall(self, msg_type, msg_txt = "", ignore = None):
        for client in self.clients:
            if ignore is not None:
                if client == ignore:
                    continue
            client.send(encode(msg_txt, msg_type).encode('utf-8'))

    def send(self, client, msg_type, msg_txt = ""):
        client.send(encode(msg_txt, msg_type).encode('utf-8'))

    def receive(self, client):
        msg_type = ""
        msg_txt = ""
        while True:
            response = client.recv(1024).decode('utf-8')
            msg_type, msg_txt = decode(response)
            if msg_type != PING:
                break
#            print(f"\n###\nPING by {client}\n###\n")
        return msg_type, msg_txt

    def tab(self):
        table = "\n##############\n"
        i = 1
        for player in self.players:
            table += f"{i})\t{player}\n"
            i+=1
        table += "##############\n\n"
        return table
    
    def mkchallenge(self):
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        task = f"{a} + {b}"
        answer = f"{a + b}"
        return task, answer
    
    def game_start(self):
        votes = 0
        for _, value in self.voted.items():
            if value:
                votes += 1

        if len(self.voted) > votes  or  len(self.voted) < 2:
            return
        
        self.game_running = True
        self.sendall(ECHO, "Game started!")
        time.sleep(1)

        while self.game_running:
            self.sendall(ECHO, self.tab())
            
            self.answered = False
            self.curr_ans = ""
            task, answer = self.mkchallenge()

            rnd_name = random.choice(list(self.players))
            rnd_socket = self.players[rnd_name]

            self.send(rnd_socket, QUESTION, f"Your task is {task} = ?\n[{rnd_name}]")
            self.sendall(ECHO, f"{rnd_name} is solving {task}", rnd_socket)

            while not self.answered and rnd_socket in self.clients:
                self.send(rnd_socket, PING)
                time.sleep(1)

            if self.curr_ans == answer:
                self.send(rnd_socket, ECHO, "Correct!")
                self.sendall(ECHO, f"{rnd_name} solved his task!", rnd_socket)
            else:
                if rnd_socket in self.clients:
                    self.send(rnd_socket, KICK, "Wrong! You are out of the game")
                self.sendall(ECHO, f"{rnd_name} dropped out!")

            time.sleep(1)
            if len(self.players) < 2:
                self.game_running = False

        time.sleep(1)
        self.sendall(KICK, "\n\n\nYou are winner!!!\n\n")
        self.stop()

    def handle_client(self, client_socket, client_address):
          
        print(f"New connection from {client_address}")
        self.clients.append(client_socket)
        
        try:
            # Start the connection verification thread
            #threading.Thread(target=self.verify_connection, daemon = True, args = (client_socket,)).start()
            if self.game_running:
                self.send(client_socket, KICK, "Wait! Server is busy!")


            # Name ask dialog
            name_question = "What is your name?\n[?]"
            while True:
                self.send(client_socket, QUESTION, name_question)    
                msg_type, msg_txt = self.receive(client_socket)
                if msg_type != REPLY:
                    continue

                if msg_txt in self.players:
                    name_question = f"There is someone with the name {msg_txt}. Please, choose another nick:\n[?]"
                    continue

                name = msg_txt
                self.players[name] = client_socket
                self.voted[name] = False
                print(f"Client {client_address} says their name is: {name}")
                
                echo_msg = f"Hello, [{name}]! Welcome to the game server!"
                self.send(client_socket, ECHO, echo_msg)
                break
            
            # Pre game menu
            while True:
                question = f"[{name}]"
                self.send(client_socket, QUESTION, question)
                    
                msg_type, msg_txt = self.receive(client_socket)
                if msg_type == REPLY:
                    if msg_txt.lower() == "start":
                        self.voted[name] = True
                        break
                    
                    if msg_txt.lower() == "help":
                        self.send(client_socket, ECHO, f"\nType \n\thelp - for this message\n\texit - exit\n\tstart - start the game\n\t<enter> to list players")
                        continue

                    if msg_txt.lower() == "exit":
                        self.send(client_socket, KICK)
                        continue

                    self.send(client_socket, ECHO, self.tab())

            threading.Thread(target=self.game_start, daemon = True).start()

            # Waiting for all
            while not self.game_running:
                time.sleep(1)


            # Playing
            while self.game_running:
                msg_type, msg_txt = self.receive(client_socket)
                if msg_type == REPLY:
                    self.curr_ans = msg_txt
                    self.answered = True
                    

            goodbye_msg = "Thank you for playing! Connection will be closed."
            self.send(client_socket, KICK, goodbye_msg)
        except Exception as e:
            print(f"\n\nError handling client {client_address}: {e}\n\n")

        self.clients.remove(client_socket)
        for player in self.players:
            if self.players[player] == client_socket:
                del self.players[player]
                del self.voted[player]
                break
        client_socket.close()
        print(f"Connection with {client_address} closed({len(self.clients)})")

    def verify_connection(self, client):
        while client in self.clients:
            self.send(client, PING)
            time.sleep(1)
    
    def start(self):
         
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        print(f"Game server started on {self.host}:{self.port}")
        print("Waiting for connections...")
        
        try:
            while True:
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
    
    def stop(self):
         
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
    server = GameServer("0.0.0.0")
    server.start()