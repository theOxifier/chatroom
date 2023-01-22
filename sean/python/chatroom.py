# Describe how things should work
'''
Two people/groups of people want to talk to each other on an encrypted messaging service.
They want to be able to go to a website. Search for each other's name and initiate a chat.

* for now as soon as the chat is over the history is lost.

* Any one can initiate the close of communication and the end and lost of the chat.

* clients can leave chat with out closing the chat, if they choose.


'''
class SessionManager():
    def __init__(self):
        self.session_id_list = {}
        pass

    def __str__(self):
        pass

    def create_session(self):
        pass

    def destroy_session(self):
        pass

class Session():
    def __init__(self):
        self.client_list = []
        pass

    def __str__(self):
        client_ids = []
        for client in self.client_list:
           client_ids.append(str(client)) 
        return f"{client_ids}"

    def attach_client(self,client):
        self.client_list.append(client)
    
    def detach_client(self,client):
        self.client_list.append(client)

class Client():
    def __init__(self, client_id):
        self.client_id = client_id # unique random string
        pass

    def __str__(self):
        return f"{self.client_id}"

def main():
    client_1 = Client("1234")
    client_2 = Client("1235")
    session_1 = Session()
    session_1.attach_client(client_1)
    session_1.attach_client(client_2)

if __name__ == "__main__":
    main()
