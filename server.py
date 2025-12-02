import socket
import threading
from pyngrok import ngrok

class SimpleServer():
    def __init__(self, host="127.0.0.1", port=23901):
        self.host = host
        self.port = port
        self.running = True
        
    def handle_client(self, conn, addr):
        try:
            with conn:
                print("Connected by", addr)
                while True:
                    data = conn.recv(1024) # Receive data from the client up to 1024 bytes
                    # Break the loop if no data is received
                    if data.decode() == "stop":
                        conn.sendall(b'Server stopping connection.')
                        conn.close()
                        break
                    elif data.decode().lower() == "hi" or data.decode().lower() == "hello":
                        response = b'Hello! How can I help you?'
                        conn.sendall(response)
                    else:
                        print(f"Recieved from client {addr}:", data.decode())
                        conn.sendall(b"Recieved!") # Echo the received data back to the client
                        
        except Exception as e:
            print(f"An error occurred with client {addr}: {e}")
        finally:
            conn.close()
            print(f"Connection with {addr} closed.")
        
    def start(self):
        #socket.AF_INET is used for IPv4 addresses
        #socket.SOCK_STREAM is used for TCP connections
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self.server_socket = s
            s.bind((self.host, self.port))
            s.listen(5)
            s.settimeout(1.0)  # Set timeout to allow periodic checks for self.running
            print(f"Server listening on {self.host}:{self.port}")
            try:
                while self.running:
                    try:
                        conn, addr = s.accept()
                        client_thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                        client_thread.start()
                    except socket.timeout:
                        continue
            except KeyboardInterrupt:
                print("Server is shutting down.")
            finally:
                self.running = False
                print("Server has stopped.")
                
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
if __name__ == "__main__":
    ngrok.set_auth_token("auth_token_here")
    tcp_tunnel = ngrok.connect(23901, "tcp")
    print("Public URL:", tcp_tunnel.public_url)
    
    server = SimpleServer()
    server.start()
    
    ngrok.disconnect(tcp_tunnel.public_url)
    ngrok.kill()
    