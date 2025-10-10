import socket
import threading

class MathGameClient:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = input("Введите ваш никнейм: ")
        
    def receive_messages(self):
        """Получает сообщения от сервера"""
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                
                if message == "EXIT":
                    print("Вы исключены из игры...")
                    break

                elif message == "NICK":
                    self.client_socket.send(f"NICKNAME:{self.nickname}".encode('utf-8'))
                
                elif message.startswith("PROBLEM:"):
                    problem = message.split(":")[1]
                    print(f"\n🎯 Ваша задача: {problem}")
                    answer = input("Введите ответ: ")
                    self.client_socket.send(f"ANSWER:{answer}".encode('utf-8'))
                
                elif message.startswith("WAIT:"):
                    print(f"\n{message.split(':')[1]}")
                
                else:
                    print(message)
                    
            except:
                print("❌ Соединение с сервером потеряно")
                self.client_socket.close()
                break
    
    def start_client(self):
        """Запускает клиент"""
        try:
            self.client_socket.connect((self.host, self.port))
            print("✅ Подключение к серверу установлено!")

            self.receive_messages()
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")

if __name__ == "__main__":
    client = MathGameClient()
    client.start_client()
