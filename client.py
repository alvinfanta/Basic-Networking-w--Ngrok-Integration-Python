import socket

class client_program():
    
    def __init__(self, host, port):
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
    IP = input("Enter server IP: ")
    try:
        PORT = int(input("Enter server port: "))
    except ValueError:
        print("Invalid port number. Please enter an integer.")
        exit(1)
    try:
        client = client_program(IP, PORT)
    except Exception as e:
        print(f"An error occurred: {e}")