import socket
import threading
import os  # ✅ For Render environment variable support

# ✅ Get port from Render or use default for local testing
PORT = int(os.environ.get("PORT", 12345))
HOST = '0.0.0.0'  # Bind to all interfaces (important for Render)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []

# ✅ Broadcast message to all connected clients
def broadcast(message):
    for client in clients[:]:  # Copy to avoid issues during iteration
        try:
            client.send(message)
        except (BrokenPipeError, ConnectionResetError):
            clients.remove(client)
            client.close()

# ✅ Handle messages from a specific client
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            if client in clients:
                index = clients.index(client)
                client.close()
                clients.remove(client)
                nickname = nicknames[index]
                broadcast(f'{nickname} left!'.encode('utf-8'))
                nicknames.remove(nickname)
                break

# ✅ Accept and manage new clients
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        try:
            # Ask for nickname
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')

            # ✅ Prevent HTTP traffic from breaking the socket server
            if nickname.startswith(('GET', 'HEAD', 'POST')):
                print("Ignored an HTTP request.")
                client.close()
                continue

            clients.append(client)
            nicknames.append(nickname)

            print(f"Nickname is {nickname}")
            broadcast(f'{nickname} joined!'.encode('utf-8'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        except Exception as e:
            print(f"Error during client connection: {e}")
            client.close()

# ✅ Start the server
print(f"Server started and listening on {HOST}:{PORT}")
receive()

