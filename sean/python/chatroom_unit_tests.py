import unittest
import chatroom


class PrintTests(unittest.TestCase):
    def setUp(self):
        self.session_manager = chatroom.SessionManager("session_1")
        self.session = chatroom.Session("one")
        self.client_1 = chatroom.Client("1234")
        self.client_2 = chatroom.Client("5678")

        self.session.attach_client(self.client_1)
        self.session.attach_client(self.client_2)

        self.session_manager.attach_session(self.session)

    def test_print_session_info(self):
        self.assertEqual(str(self.session),"1234 5678")

    def test_print_client_info(self):
        self.assertEqual(str(self.client_1),"1234")
        self.assertEqual(str(self.client_2),"5678")

    def test_print_session_manager_info(self):
        print(self.session_manager)
        self.assertEqual(str(self.session_manager),"session_1 1234 5678")

if __name__ == '__main__':
    unittest.main()
