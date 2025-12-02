import socket

class client_program():
    
    def __init__(self, host='6.tcp.ngrok.io', port=13052):
        self.host = host
        self.port = port
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            print(f"Connected to server at {self.host}:{self.port}")
            
            while True:
                message = input("Enter message to send (type 'stop' to end): ")
                if message.lower() == "exit":
                    break
                elif message == "stop":
                    s.sendall(message.encode())
                    data = s.recv(1024)
                    print("Received from server:", data.decode())
                    break
                else:
                    s.sendall(message.encode())
                    data = s.recv(1024)
                    print("Received from server:", data.decode())

if __name__ == "__main__":
    client = client_program()