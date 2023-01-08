#!/usr/bin/env python3
import socket
import ssl
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

# Set up the client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

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

# Get the client's nickname
client.send(cipher.encrypt(input("Enter your nickname: ").encode("utf-8")))

# Set up a loop to handle messages from the server
while True:
    message = client.recv(1024)
    if not message:
        break
    message = cipher.decrypt(message).decode("utf-8")
    print(message, end="")

# Close the client's connection
client.close()

# Delete the temporary files
os.unlink(cert_file.name)
os.unlink(key_file.name)
