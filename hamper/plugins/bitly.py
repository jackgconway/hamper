import re
import urllib
import urllib2
import json

from hamper.interfaces import ChatPlugin

class BitlyAPI(object):
    """
    This class does the actual work of communicating with bit.ly
    """
    def __init__(self, username, api_url, api_key):
        self.username = username
        self.api_url = api_url
        self.api_key = api_key

    def _query(self, method, path, **kwargs):
        """
        Send an HTTP Request to the bitly API
        """
        params = {'login': self.username, 'apiKey': self.api_key }
        params.update(kwargs)
        url = self.api_url + path

        if 'get' == method:
            url += '?' + urllib.urlencode(params)
            data = None
        elif 'post' == method:
            data = urllib.urlencode(params)
        else:
            raise ValueError('Invalid Method')

        req = urllib2.Request(url, data=data)
        response = urllib2.urlopen(req)
        return json.load(response)

    def shorten(self, long_url):
        """
        Given a long URL, returns a bitly short URL
        """
        result = self._query('post', 'shorten', longUrl=long_url)
        return result['data']['url']

    def info(self, short_url):
        """
        Given a short_url, return all information bitly provides
        """
        params = {'shortUrl': short_url}
        return self._query('get', 'info', **params)

    def get_title(self, short_url):
        """
        Given a shortened url, return the title.
        """
        return self.info(short_url=short_url)['data']['info'][0]['title']



class Bitly(ChatPlugin):
    """
    Plugin to add URL-Shortening via http://bit.ly/
    """
    name = 'bitly'
    priority = 2

    # Regex is taken from:
    # http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    regex = re.compile(ur"""
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
    """, re.VERBOSE | re.IGNORECASE | re.U)

    def setup(self, factory):
        try:
            self.api = BitlyAPI(
                username=factory.config['bitly']['login'],
                api_url='https://api-ssl.bitly.com/v3/',
                api_key=factory.config['bitly']['api_key'])
        except KeyError:
            print ('\nTo use the bitly plugin you need to set your bitly login'
                   '\nand api_key in your config file.\n'
                   'Example:\n'
                   'bitly:\n'
                   "    login: '123456789000'\n"
                   "    api_key: '1234678901234567890123467890123456'\n")
            quit()

        # If an exclude value is found in the url it will not be shortened
        self.excludes = ['imgur.com', 'github.com', 'pastebin.com']


    def message(self, bot, comm):
        match = self.regex.search(comm['message'])
        # Found a url
        if match:
            # base url isn't % encoded, python 2.7 doesn't do this well, and I
            # couldn't figure it out.
            long_url = match.group(0)

            # Only shorten urls which are longer than a bitly url
            # (20 chars, including the http:// prefix)
            if len(long_url) <= 20:
                return False

            # Don't shorten url's which are in the exclude list
            for item in self.excludes:
                if item in long_url.lower():
                    return False

            # Bitly requires a valid URI
            if not match.group('prot'):
                long_url = 'http://' + long_url

            short_url = self.api.shorten(long_url)
            title = self.api.get_title(short_url)

            template = "{nick}'s url: {url}"
            if title:
                template += " - Title: {title}"

            msg = template.format(
                nick=comm['user'], url=short_url, title=title)
            bot.reply(comm, msg)

        # Always let the other plugins run
        return False

bitly = Bitly()
