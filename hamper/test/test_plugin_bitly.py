import unittest
import MockBot
from hamper.plugins.bitly import Bitly

class MockBitly(object):
    """
    Mock responses from the Bitly API for easy testing.
    """
    def __init__(self):
        self.fake_shorty = 'http://bit.ly/5h0rT'
        self.fake_title = None

    def shorten(self, long_url):
        return self.fake_shorty

    def get_title(self, short_url):
        return self.fake_title

class BitlyTest(unittest.TestCase):
    """
    Test suite for hamper.plugins.bitly
    """
    def setUp(self):
        self.bot = MockBot.create()

        # fake Bitly.setup for testing:
        self.plug = Bitly()
        self.plug.excludes = []
        self.plug.api = MockBitly()

    def test_link_already_short(self):
        self.plug.message(self.bot, {
            'user': 'shorty',
            'message': 'http://shorty.com'})
        self.assertEquals(None, self.bot.last_reply)

    def test_link_no_title(self):
        self.plug.message(self.bot, {
            'user': 'spammy',
            'message': 'http://spammyspamspam.com/'})
        self.assertEquals(
            "spammy's url: http://bit.ly/5h0rT",
            self.bot.last_reply)

    def test_link_with_title(self):
        self.plug.api.fake_title = "The /r/LearnProgramming Mentoring Community"
        self.plug.message(self.bot, {
            'user': 'someone',
            'message': 'have you seen http://reddit.com/r/lpmc/?'})
        self.assertEquals(
            "someone's url: http://bit.ly/5h0rT - Title: The /r/LearnProgramming Mentoring Community",
            self.bot.last_reply)

if __name__ == "__main__":
    unittest.main()