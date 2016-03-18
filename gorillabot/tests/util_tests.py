import unittest
from plugins import util

def fake_getter(request):
    fake_data = open("tests/testdata/url_test.html", 'rb')
    return fake_data

class FakeLogger:
    def info(self, message):
        pass

class FakeBot:
    def __init__(self):
        self.header = {"User-Agent": "FaketyFakeFake (http://example.com/this_is_so_fake)"}
        self.logger = FakeLogger()

class FakeMessage:
    def __init__(self):
        self.bot = FakeBot()


class UtilTest(unittest.TestCase):

    def test_get_url(self):
        m = FakeMessage()
        data = util.get_url(m, "http://example.com", title=True, get_fn=fake_getter)
        self.assertEqual(len(data.encode('utf-8')), 5000, "Got more than 5000 bytes of data")