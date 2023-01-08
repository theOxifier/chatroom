import socket
import threading

from cryptography.fernet import Fernet

# Set up the client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 8000))

# Get the key from the server
key = client.recv(1024)

# Create a Fernet cipher object
cipher = Fernet(key)

# Get the user's nickname
nickname = input(cipher.decrypt(client.recv(1024)).decode("utf-8"))

# Send the user's nickname to the server
client.send(nickname.encode("utf-8"))

# Set up a loop to handle messages from the server
def receive_messages():
    while True:
        try:
            # Receive a message from the server
            message = client.recv(1024)

            # If the message is empty, the server has disconnected
            if not message:
                print("Server disconnected")
                client.close()
                break

            # Decrypt the message and print it
            message = cipher.decrypt(message).decode("utf-8")
            print(message)
        except:
            # If there is an error, the server has disconnected
            print("Server disconnected")
            client.close()
            break

# Set up a thread to receive messages from the server
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# Set up a loop to send messages to the server
while True:
    # Get a message from the user
    message = input()

    # If the message is "/quit", close the client
    if message == "/quit":
        break

    # Encrypt the message and send it to the server
    message = cipher.encrypt(f"{nickname}: {message}\n".encode("utf-8"))
    client.send(message)

# Close the client's connection
client.close()
