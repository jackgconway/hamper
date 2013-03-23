

class MockBot(object):
    """
    Simulates the bot and allow inspecting the results,
    for use in the test cases.
    """

    def __init__(self):
        self.last_reply = None

    def reply(self, cmd, msg):
        self.last_reply = msg


def create():
    """convenience function to return a MockBot instance"""
    return MockBot()
