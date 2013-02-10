import re
import urllib
import urllib2
import json

from hamper.interfaces import ChatPlugin


class Bitly(ChatPlugin):
    name = 'bitly'
    priority = 2

    # Regex is taken from:
    # http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    regex = ur"""
    (                       # Capture 1: entire matched URL
      (?:
        (?P<prot>https?://)     # http or https protocol
        |                       #   or
        www\d{0,3}[.]           # "www.", "www1.", "www2." ... "www999."
        |                           #   or
        [a-z0-9.\-]+[.][a-z]{2,4}/  # looks like domain name
                                    # followed by a slash
      )
      (?:                                  # One or more:
        [^\s()<>]+                         # Run of non-space, non-()<>
        |                                  # or
        \(([^\s()<>]+|(\([^\s()<>]+\)))*\) # balanced parens, up to 2 levels
      )+
      (?:                                  # End with:
        \(([^\s()<>]+|(\([^\s()<>]+\)))*\) # balanced parens, up to 2 levels
        |                                  # or
        [^\s`!()\[\]{};:'".,<>?]           # not a space or one of
                                           # these punct chars
      )
    )
    """

    def setup(self, factory):
        self.regex = re.compile(self.regex, re.VERBOSE | re.IGNORECASE | re.U)
        self.api_url = 'https://api-ssl.bitly.com/v3/'
        self.username = factory.config['bitly']['login']
        self.api_key = factory.config['bitly']['api_key']
        # If an exclude value is found in the url it will not be shortened
        self.excludes = ['imgur.com', 'github.com', 'pastebin.com']
        # Make sure they've configured the bitly config values.
        try:
            self.username = factory.config['bitly']['login']
            self.api_key = factory.config['bitly']['api_key']
        except KeyError:
            print ('\nTo use the bitly plugin you need to set your bitly login'
                   '\nand api_key in your config file.\n'
                   'Example:\n'
                   'bitly:\n'
                   "    login: '123456789000'\n"
                   "    api_key: '1234678901234567890123467890123456'\n")
            quit()

    def message(self, bot, comm):
        match = self.regex.search(comm['message'])
        # Found a url
        if match:
            # base url isn't % encoded, python 2.7 doesn't do this well, and I
            # couldn't figure it out.
            long_url = match.group(0)

            # Only shorten urls which are longer than a bitly url (12 chars)
            if len(long_url) <= 12:
                return False

            # Don't shorten url's which are in the exclude list
            for item in self.excludes:
                if item in long_url.lower():
                    return False

            # Bitly requires a valid URI
            if not match.group('prot'):
                long_url = 'http://' + long_url

            # Get the short URL
            shorten_data = self.shorten(bot, long_url)
            short_url = shorten_data['data']['url']

            # with the short URL get the title of the page
            info = self.info(bot, short_url=short_url)
            title = info['data']['info'][0]['title']
            if title:
                bot.reply(comm, "{url} - Title: {title}"
                          .format(url=short_url, title=title))
            else:
                bot.reply(comm, "{nick}'s url: {url}"
                          .format(nick=comm['user'], url=short_url))

        # Always let the other plugins run
        return False

    def shorten(self, bot, long_url):
        """Given a long URL, returns a bitly short URL"""
        params = {'login': self.username, 'apiKey': self.api_key,
                  'longUrl': long_url}

        url = self.api_url + 'shorten'
        data = urllib.urlencode(params)

        req = urllib2.Request(url, data=data)
        response = urllib2.urlopen(req)
        json_data = json.load(response)

        return json_data

    def info(self, bot, hash=None, short_url=None):
        params = {'login': self.username, 'apiKey': self.api_key}
        if hash:
            params.update({'hash': hash})
        if short_url:
            params.update({'shortUrl': short_url})

        url = self.api_url + 'info'
        data = urllib.urlencode(params)
        url += '?' + data

        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        json_data = json.load(response)

        return json_data

bitly = Bitly()
