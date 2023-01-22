import unittest
import chatroom


class PrintTests(unittest.TestCase):
    def setUp(self):
        self.client = chatroom.Client("1234")
        self.session = chatroom.Session()
        client_1 = chatroom.Client("1234")
        client_2 = chatroom.Client("5678")
        self.session.attach_client(client_1)
        self.session.attach_client(client_2)
        print(self.session)

    def test_print_session_info(self):
        print(self.session)
        self.assertEqual(str(self.session),str(["1234","5678"]))

    def test_print_client_info(self):
        self.assertEqual(str(self.client),"1234")

    def test_print_session_manager_info(self):
#        self.assertEqual(str(client),"1234")
        pass

if __name__ == '__main__':
    unittest.main()
