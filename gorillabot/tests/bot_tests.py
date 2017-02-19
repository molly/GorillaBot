import unittest
from socket import socket
import logging

from bot import Bot
from configure import Configurator


class MockSocket(socket):
    def __init__(self):
        super(MockSocket, self).__init__()
        self.address = ""
        self.port = ""
        self.messages = []

    def connect(self, address):
        self.address = address[0]
        self.port = address[1]

    def settimeout(self, timeout):
        pass

    def sendall(self, data, flags=None):
        self.messages.append(data)

    def get_messages(self):
        return self.messages


class MockLogger(logging._loggerClass):
    def __init__(self):
        super(MockLogger, self).__init__("Test")

    def debug(self, msg, *args, **kwargs):
        pass

    def info(self, msg, *args, **kwargs):
        pass

    def error(self, msg, *args, **kwargs):
        pass


class TestBot(unittest.TestCase):
    def testConnectToConfiguredServer(self):
        class MockBot(Bot):
            def initialize(self, configurator):
                self.configuration_name = configurator.configure()
                self.configuration = configurator.get_settings()
                self.logger = MockLogger()

            def _get_socket(self):
                return MockSocket()

            def update_configuration(self, updated_configuration):
                pass

        class MockConfigurator(Configurator):
            def configure(self):
                return "test_config"

            def get_settings(self):
                return {"server": "localhost",
                        "password": None,
                        "nick": "test_bot",
                        "ident": "test_bot",
                        "realname": "test_bot",
                        "nickserv_auth": False,
                        "chans": []}

        bot = MockBot()
        mock_configurator = MockConfigurator()
        bot.initialize(mock_configurator)
        bot.connect()
        self.assertEqual(bot.socket.address, "localhost")

    def testNickServConfiguration_NoAuth(self):
        class MockBot(Bot):
            def __init__(self):
                super(MockBot, self).__init__()
                self.sent_messages = []

            def initialize(self):
                self.configuration_name = "test_config"
                self.configuration = {"server": "localhost",
                                      "password": None,
                                      "nick": "test_bot",
                                      "ident": "test_bot",
                                      "realname": "test_bot",
                                      "nickserv_auth": False,
                                      "chans": []}
                self.logger = MockLogger()

            def _get_socket(self):
                return MockSocket()

            def send(self, message, hide=False):
                self.sent_messages.append(message)

            def get_sent_messages(self):
                return self.sent_messages

            def update_configuration(self, updated_configuration):
                pass

        bot = MockBot()
        bot.initialize()
        bot.connect()
        sent_messages = bot.get_sent_messages()
        nickserv_messages = [x for x in sent_messages if x.startswith("PRIVMSG NickServ")]
        self.assertLess(len(nickserv_messages), 1)

    def test_NickServConfiguration_Auth(self):
        class MockBot(Bot):
            def __init__(self):
                super(MockBot, self).__init__()
                self.sent_messages = []

            def initialize(self):
                self.configuration_name = "test_config"
                self.configuration = {"server": "localhost",
                                      "password": None,
                                      "nick": "test_bot",
                                      "ident": "test_bot",
                                      "realname": "test_bot",
                                      "nickserv_auth": True,
                                      "chans": []}
                self.logger = MockLogger()

            def _get_socket(self):
                return MockSocket()

            def send(self, message, hide=False):
                self.sent_messages.append(message)

            def get_sent_messages(self):
                return self.sent_messages

            def update_configuration(self, updated_configuration):
                pass

        bot = MockBot()
        bot.initialize()
        bot.connect()
        sent_messages = bot.get_sent_messages()
        nickserv_messages = [x for x in sent_messages if x.startswith("PRIVMSG NickServ")]
        self.assertEqual(len(nickserv_messages), 1, "Did not send a message to nickserv")
