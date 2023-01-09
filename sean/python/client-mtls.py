#!/usr/bin/env python3
import socket
import ssl
import tempfile
import os
import datetime
import threading

from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import utils

from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.x509.oid import NameOID

from cryptography.fernet import Fernet

def create_ssl_cert_and_key():
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

    return key_file, cert_file

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

# Set up a loop to handle messages from the server
def receive_messages(client, cipher):
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

def start_client():
    # Set up the self signed ssl cert and key
    key_file, cert_file = create_ssl_cert_and_key()

    # Set up the client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Wrap the socket in a TLS context
    #context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_NONE
    context.check_hostname = False
    context.load_cert_chain(certfile=cert_file.name, keyfile=key_file.name)
    client = context.wrap_socket(client, server_hostname="localhost")

    # Connect to the server
    client.connect(("localhost", 8000))

    # Get the server's key
    key = client.recv(1024)

    # Create a Fernet cipher object
    cipher = Fernet(key)

    # Set up a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages,args=(client,cipher))
    receive_thread.start()


    # Get the client's nickname
    nickname = input("Enter your nickname: ")
    client.send(cipher.encrypt(nickname.encode("utf-8")))

    # Set up a loop to send messages to the server
    while True:
        # Get a message from the user
        message = input()

        # If the message is "/quit", close the client
        if message == "/quit":
            print("leaving")
            break

        # Encrypt the message and send it to the server
        message = cipher.encrypt(f"{nickname}: {message}\n".encode("utf-8"))
        client.send(message)


    # Close the client's connection
    client.close()

    # Delete the temporary files
    os.unlink(cert_file.name)
    os.unlink(key_file.name)

def main():
    start_client()

if __name__ == "__main__":
    main()
