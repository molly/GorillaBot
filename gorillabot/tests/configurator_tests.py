import unittest
from configure import Configurator
import json


class TestConfigurator(unittest.TestCase):

    def testGetConfiguration(self):
        class MockConfigurator(Configurator):


            def __init__(self):
                super(MockConfigurator, self).__init__()
                self.config_name = "testConf"
                self.mock_answers = {"Unique name for this configuration: ": self.config_name,
                                     "Nick": "MockBot",
                                     "Ident": "MockIdent",
                                     "Realname": "Mock Real Name",
                                     "Channel(s)": "#quanticle",
                                     "Bot operator(s)": "quanticle",
                                     "Server password (optional)": "",
                                     "YouTube API key (optional)": "",
                                     "Forecast.io API key (optional)": "",
                                     "Server": "localhost",
                                     "Authenticate with NickServ (y/n)": "n"}
                self.config = {}
                self.prompts = []

            def prompt(self, field, default=None, hidden=False):
                self.prompts.append(field)
                if field in self.mock_answers.keys():
                    return self.mock_answers[field]
                else:
                    raise AttributeError("Field not found: " + field)

            def reset(self):
                pass

            def get_settings(self):
                return {}

            def save_config(self, new_settings):
                self.config = new_settings

            def verify(self, settings, name):
                return True

        mockConfigurator = MockConfigurator()
        mockConfigurator.create_new()
        self.assertTrue("Server" in mockConfigurator.prompts)
        self.assertEqual(mockConfigurator.config[mockConfigurator.config_name]["server"], "localhost")
        self.assertTrue("Authenticate with NickServ (y/n)" in mockConfigurator.prompts)
        self.assertFalse(mockConfigurator.config[mockConfigurator.config_name]["nickserv_auth"])
