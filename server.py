import socket
import threading
import random
import time

class MathGameServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.nicknames = []
        self.game_active = False
        self.current_player = None
        
    def generate_math_problem(self):
        """Генерирует простую арифметическую задачу"""
        operations = ['+', '-', '*']
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        op = random.choice(operations)
        
        if op == '+':
            answer = a + b
        elif op == '-':
            # Избегаем отрицательных ответов
            a, b = max(a, b), min(a, b)
            answer = a - b
        else:  # '*'
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            answer = a * b
            
        problem = f"{a} {op} {b}"
        return problem, answer
    
    def broadcast(self, message, exclude_client=None):
        """Отправляет сообщение всем подключенным клиентам"""
        for client in self.clients:
            if client != exclude_client:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    self.remove_client(client)
    
    def remove_client(self, client):
        """Удаляет клиента из игры"""
        if client in self.clients:
            index = self.clients.index(client)
            nickname = self.nicknames[index]
            
            self.broadcast(f"Игрок {nickname} выбыл из игры!")
            self.clients.remove(client)
            self.nicknames.remove(nickname)
            
            self.current_player.send(f"EXIT".encode('utf-8'))
            client.close()

            print(f"Игрок {nickname} отключился")
    
    def handle_client(self, client):
        """Обрабатывает сообщения от клиента"""
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                
                if message.startswith('NICKNAME:'):
                    nickname = message.split(':')[1]
                    self.nicknames.append(nickname)
                    self.clients.append(client)
                    print(f"Игрок {nickname} присоединился к игре")
                    self.broadcast(f"Игрок {nickname} присоединился к игре!")
                    
                    # Если игроков достаточно, начинаем игру
                    if len(self.clients) >= 2 and not self.game_active:
                        self.start_game()
                
                elif message.startswith('ANSWER:'):
                    if client == self.current_player:
                        answer = int(message.split(':')[1])
                        nickname = self.nicknames[self.clients.index(client)]
                        
                        if answer == self.current_answer:
                            self.broadcast(f"✓ Игрок {nickname} правильно решил задачу!")
                            time.sleep(1)
                            self.next_round()
                        else:
                            self.broadcast(f"✗ Игрок {nickname} ошибся! Правильный ответ: {self.current_answer}")
                            time.sleep(1)
                            self.remove_client(client)
                            
                            if len(self.clients) > 1:
                                self.next_round()
                            else:
                                self.end_game()
                
            except:
                self.remove_client(client)
                break
    
    def next_round(self):
        """Начинает следующий раунд"""
        if len(self.clients) > 1:
            self.current_player = random.choice(self.clients)
            problem, answer = self.generate_math_problem()
            self.current_answer = answer
            
            player_nickname = self.nicknames[self.clients.index(self.current_player)]
            self.broadcast(f"\n🎯 Следующий игрок: {player_nickname}")
            time.sleep(1)
            
            # Отправляем задачу выбранному игроку
            self.current_player.send(f"PROBLEM:{problem}".encode('utf-8'))
            
            # Уведомляем других игроков
            for client in self.clients:
                if client != self.current_player:
                    client.send(f"WAIT:Игрок {player_nickname} решает задачу: {problem}".encode('utf-8'))
        
        else:
            self.end_game()
    
    def start_game(self):
        """Начинает игру"""
        self.game_active = True
        self.broadcast("🎮 Игра начинается!")
        time.sleep(2)
        self.broadcast(f"Игроков в игре: {len(self.clients)}")
        time.sleep(1)
        self.next_round()
    
    def end_game(self):
        """Завершает игру"""
        if self.clients:
            winner = self.nicknames[0]
            self.broadcast(f"🏆 Победитель: {winner}! Поздравляем!")
            self.game_active = False
    
    def start_server(self):
        """Запускает сервер"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"🚀 Сервер запущен на {self.host}:{self.port}")
        
        while True:
            client, address = self.server_socket.accept()
            print(f"🔗 Подключение от {address[0]}:{address[1]}")
            
            # Запрашиваем никнейм
            client.send("NICK".encode('utf-8'))
            
            # Запускаем поток для обработки клиента
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.daemon = True
            thread.start()

if __name__ == "__main__":
    server = MathGameServer()
    server.start_server()
