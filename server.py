import socket
import threading
import os

class SimpleServer():
    def __init__(self, host="127.0.0.1", port=23901):
        self.host = host
        self.port = port
        self.running = True
        self.lock = threading.Lock()
        self.clients = [] # List of tuples: (conn, username)
        
    def broadcast(self, sender_conn, message):
        """
        Sends a message to all clients except the sender.
        If sender_conn is None, sends to EVERYONE.
        """
        with self.lock:
            for client in self.clients:
                # client is a tuple (conn, username)
                target_conn = client[0]
                
                # If sender_conn is None (server message), send to all. 
                # Otherwise, don't send back to the sender.
                if sender_conn is None or target_conn != sender_conn:
                    try:
                        target_conn.sendall(message.encode())
                    except:
                        pass # Dead connections are handled in their own threads
        
    def handle_client(self, conn, addr):
        print(f"Connected by {addr}")
        username = "Unknown"
        try:
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    
                    text = data.decode(errors="ignore")
                    
                    # FILTER: Ignore HTTP requests from browsers (GET, POST, etc.)
                    if text.startswith(("GET /", "POST /", "HEAD /", "Host:", "User-Agent:")):
                        print(f"[Log] Ignored HTTP request from {addr}")
                        continue

                    # 1. Handshake: "Username:joined"
                    if text.endswith(":joined"):
                        username = text.split(":")[0]
                        with self.lock:
                            self.clients.append((conn, username))
                        print(f"{username} has joined.")
                        self.broadcast(conn, f"{username} has joined the chat.")
                    
                    # 2. Regular Message: "Username:Message"
                    elif ":" in text:
                        print(f"Broadcasting: {text}")
                        self.broadcast(conn, text)
                        
        except Exception as e:
            print(f"Error with {addr}: {e}")
        finally:
            # --- DISCONNECT LOGIC ---
            disconnected_user = None
            
            # 1. Remove client from list safely
            with self.lock:
                for client in self.clients:
                    if client[0] == conn:
                        self.clients.remove(client)
                        disconnected_user = client[1]
                        break
            
            conn.close()
            print(f"Connection with {addr} closed.")
            
            # 2. Broadcast departure (only if they had actually joined)
            if disconnected_user:
                print(f"{disconnected_user} has left.") 
                self.broadcast(None, f"{disconnected_user} has left the chat.")
        
    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self.server_socket = s
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen()
            s.settimeout(1.0)
            print(f"Server listening on {self.host}:{self.port}")
            
            try:
                while self.running:
                    try:
                        conn, addr = s.accept()
                        threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
                    except socket.timeout:
                        continue
                        
            except KeyboardInterrupt:
                print("\n[Server] Caught KeyboardInterrupt. Shutting down...")
                self.broadcast(None, "[Server] Shutting Down!")
                
            finally:
                self.running = False
                if self.server_socket:
                    self.server_socket.close()
                print("Server has stopped.")

if __name__ == "__main__":
    server = SimpleServer()
    os.system('cls' if os.name == 'nt' else 'clear')
    server.start()