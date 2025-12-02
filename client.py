import socket
import threading
import os
import sys

class ClientProgram:
    def __init__(self, host, port, username):
        self.host = host
        self.port = port
        self.username = username
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"[CLIENT] Connected to {self.host}:{self.port}")
            
            # Send Handshake immediately
            self.sock.sendall(f"{self.username}:joined".encode())

            # Start listening thread
            threading.Thread(target=self.listen_for_messages, daemon=True).start()
            
            # Start sending loop (Main Thread)
            self.send_messages()
            
        except ConnectionRefusedError:
            print("Could not connect to server.")
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit()

    def listen_for_messages(self):
        while True:
            try:
                data = self.sock.recv(1024)
                if not data:
                    print("\n[SERVER] Disconnected unexpectedly.")
                    os._exit(0) # Force kill the program
                
                message = data.decode(errors="ignore")
                
                # Check for the specific Shutdown command
                if "[Server] Shutting Down!" in message:
                    print(f"\n{message}")
                    print("Press Enter to exit...")
                    input()
                    os._exit(0) # Force kill the program immediately
                
                # Print normal message and restore the input prompt
                print(f"\r{message}\n{self.username}: ", end="", flush=True)
                
            except Exception:
                break

    def send_messages(self):
        while True:
            try:
                msg = input(f"{self.username}: ")
                full_msg = f"{self.username}: {msg}"
                self.sock.sendall(full_msg.encode())
            except EOFError:
                # Handle Ctrl+D or unexpected input closure
                print("Exiting...")
                self.sock.close()
                os._exit(0)
            except Exception:
                self.sock.close()
                break

if __name__ == "__main__":
    # You can change these defaults or use input()
    os.system('cls' if os.name == 'nt' else 'clear')
    IP = input("Enter server IP: ")
    PORT = int(input("Enter server Port: "))
    Username = input("Enter your username: ")
    os.system('cls' if os.name == 'nt' else 'clear')
    ClientProgram(IP, PORT, Username)