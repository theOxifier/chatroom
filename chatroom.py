# Describe how things should work
'''
Two people/groups of people want to talk to each other on an encrypted messaging service.
They want to be able to go to a website. Search for each other's name and initiate a chat.

* for now as soon as the chat is over the history is lost.

* Any one can initiate the close of communication and the end and lost of the chat.

* clients can leave chat with out closing the chat, if they choose.
'''
import socketserver
import socket
import sys

class SessionManager():
    def __init__(self, id):
        self.session_list = []
        self.id = id

    def __str__(self):
        return f"{self.id} {' '.join(map(str,self.session_list))}"

    def attach_session(self, session_id):
        self.session_list.append(session_id)

    def destroy_session(self, session_id):
        self.session_list.remove(session_id)

'''

'''
class ConnectionHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        while True:
            # self.request is the TCP socket connected to the client
            self.data = self.request.recv(1024).strip()

            # If the data is empty, the client has disconnected
            if not self.data:
                break

            print("{} wrote:".format(self.client_address[0]))
            print(self.data)

            # just send back the same data
            self.request.sendall(self.data)

class Session():
    def __init__(self, session_id):
        self.client_list = []
        self.session_id = session_id
        self.server_address = "localhost"
        self.server_port = "15555"

    def __str__(self):
        return ' '.join(map(str,self.client_list))

    def start_session(self):
        '''
        Setup a tcp server and start listening for clients
        Things to add eventually
        * tls setup 
        '''
        HOST, PORT = "localhost", 9999

        # Create the server, binding to localhost on port 9999
        with socketserver.TCPServer((HOST, PORT),ConnectionHandler) as server:
            # Activate the server; this will keep running until you
            # interrupt the program with Ctrl-C
            server.serve_forever()

    def attach_client(self, client):
        self.client_list.append(client)
    
    def detach_client(self, client):
        self.client_list.append(client)

class Client():
    def __init__(self, client_id):
        self.client_id = client_id

    def __str__(self):
        return str(self.client_id)
        
    def client_session(self):
        HOST, PORT = "localhost", 9999
        data = " ".join(self.client_id)
    
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Connect to server and send data
            sock.connect((HOST, PORT))
            while True:
                # Create a socket (SOCK_STREAM means a TCP socket)
                #sock.sendall(bytes(data + "\n", "utf-8"))
                sock.send(bytes(input("msg: "), "utf-8"))

                # Receive data from the server and shut down
                received = str(sock.recv(1024), "utf-8")

                print("Sent:     {}".format(data))
                print("Received: {}".format(received))
    #def receive_messages(client):
    #    while True:
    #        try:
    #            # Receive a message from the server
    #            message = client.recv(1024)
    
    #            # If the message is empty, the server has disconnected
    #            if not message:
    #                print("Server disconnected")
    #                client.close()
    #                break
    #               
    #            # Decrypt the message and print it
    #            message = message.decode("utf-8")
    #            print(message)
    #        except:
    #            # If there is an error, the server has disconnected
    #            print("Server disconnected")
    #            client.close()
    #            break

def main():
    pass
#    client_1 = Client("1234")
#    client_2 = Client("1235")
#    session_1.attach_client(client_1)
#    session_1.attach_client(client_2)
    session_1 = Session("4321")
    session_1.start_session()

if __name__ == "__main__":
    main()
