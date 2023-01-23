# Describe how things should work
'''
Two people/groups of people want to talk to each other on an encrypted messaging service.
They want to be able to go to a website. Search for each other's name and initiate a chat.

* for now as soon as the chat is over the history is lost.

* Any one can initiate the close of communication and the end and lost of the chat.

* clients can leave chat with out closing the chat, if they choose.


'''
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

class Session():
    def __init__(self, session_id):
        self.client_list = []
        self.session_id = session_id
        pass

    def __str__(self):
        return ' '.join(map(str,self.client_list))

    def attach_client(self, client):
        self.client_list.append(client)
    
    def detach_client(self, client):
        self.client_list.append(client)

class Client():
    def __init__(self, client_id):
        self.client_id = client_id
        pass

    def __str__(self):
        return str(self.client_id)

def main():
    pass
#    client_1 = Client("1234")
#    client_2 = Client("1235")
#    session_1 = Session()
#    session_1.attach_client(client_1)
#    session_1.attach_client(client_2)

if __name__ == "__main__":
    main()
