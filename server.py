import socket
import threading

# Create server socket
import os

# Get the port from the environment variable provided by Render
port = int(os.environ.get("PORT", 12345))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", port))  # Bind to the dynamic port
server.listen()

clients = []
nicknames = []

# Broadcast message to all clients
def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except (BrokenPipeError, ConnectionResetError):
            # Remove the client if an error occurs
            clients.remove(client)


# Handle individual client messages
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left!'.encode('utf-8'))
            nicknames.remove(nickname)
            break

# Accept new connections
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        try:
            # Prompt client for nickname
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')

            # Ignore HTTP requests (they often start with 'GET' or 'HEAD')
            if nickname.startswith('GET') or nickname.startswith('HEAD') or nickname.startswith('POST'):
                print("Ignored an HTTP request.")
                client.close()
                continue

            clients.append(client)
            print(f"Nickname is {nickname}")
            broadcast(f'{nickname} joined!'.encode('utf-8'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        except Exception as e:
            print(f"Error during receiving client: {e}")
            client.close()

