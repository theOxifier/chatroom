#!/usr/bin/env python3
import socket
import ssl
import threading
import tempfile
import os
import datetime

from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import utils

from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID

from cryptography.fernet import Fernet

# Generate a self-signed certificate and private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "My Company"),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])
cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    public_key
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    # Our certificate will be valid for 10 days
    datetime.datetime.utcnow() + datetime.timedelta(days=10)
).add_extension(
    x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
    critical=False,
    # Sign our certificate with our private key
).sign(private_key, hashes.SHA256(), default_backend())

# Save the certificate and private key to temporary files
cert_file = tempfile.NamedTemporaryFile(delete=False)
cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
cert_file.close()
key_file = tempfile.NamedTemporaryFile(delete=False)
key_file.write(private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
))
key_file.close()


# Generate a key for the Fernet cipher
key = Fernet.generate_key()

# Create a Fernet cipher object
cipher = Fernet(key)

# Set up the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Wrap the socket in a TLS context
context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile=cert_file.name, keyfile=key_file.name)
server = context.wrap_socket(server, server_side=True)

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
    nickname = cipher.decrypt(client.recv(1024)).decode("utf-8")

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
        client_thread = threading.Thread(target=handle_client, args=(client,))
        client_thread.start()

# Start the server
start_server()

# Delete the temporary files
os.unlink(cert_file.name)
os.unlink(key_file.name)
