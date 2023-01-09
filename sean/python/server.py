import socket
import threading

from cryptography.fernet import Fernet

# Generate a key for the Fernet cipher
key = Fernet.generate_key()

# Create a Fernet cipher object
cipher = Fernet(key)

# Set up the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 8000))
server.listen()
print("Listening for connections on port 8000...")

# Set up a list to store connected clients
clients = []

# A function to broadcast messages to all clients
def broadcast(message):
    for client in clients:
        client.send(message)

# A function to handle messages from a client
def handle_client(client):
    # Get the client's nickname
    nickname = client.recv(1024).decode("utf-8")

    # Add the client to the list of connected clients
    clients.append(client)

    # Send a message to the client to confirm that they are connected
    message = f"Welcome to the chat, {nickname}!\n"
    client.send(cipher.encrypt(message.encode("utf-8")))

    # Broadcast a message to all clients to notify them of the new connection
    message = f"{nickname} has joined the chat!\n"
    broadcast(cipher.encrypt(message.encode("utf-8")))

    # Set up a loop to handle messages from the client
    while True:
        try:
            # Receive a message from the client
            message = client.recv(1024)

            # If the message is empty, the client has disconnected
            if not message:
                break

            # Decrypt the message and broadcast it to all clients
            message = cipher.decrypt(message).decode("utf-8")
            broadcast(cipher.encrypt(f"{nickname}: {message}\n".encode("utf-8")))
        except:
            # If there is an error, the client has disconnected
            break

    # Remove the client from the list of connected clients
    clients.remove(client)

    # Broadcast a message to all clients to notify them of the disconnection
    broadcast(cipher.encrypt(f"{nickname} has left the chat\n".encode("utf-8")))

    # Close the client's connection
    client.close()

# Set up a loop to accept new connections
def start_server():
    while True:
        client, address = server.accept()
        print(f"Connected to {address[0]}:{address[1]}")
        client.send(key)
        client.send(cipher.encrypt("Enter your nickname: ".encode("utf-8")))
        # Start a new thread to handle the client
        client_thread = threading.Thread(target=handle_client, args=(client))
        client_thread.start()

def main():
    start_server()

if __name__ == "__main__":
    main()
