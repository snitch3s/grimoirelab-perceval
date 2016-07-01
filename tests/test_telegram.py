# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

import sys
import unittest
import urllib

import httpretty

if not '..' in sys.path:
    sys.path.insert(0, '..')

from perceval.backends.telegram import TelegramBotClient


TELEGRAM_TOKEN = '12345678'
TELEGRAM_UPDATES_URL = 'https://api.telegram.org/bot' + TELEGRAM_TOKEN + '/getUpdates'


def read_file(filename, mode='r'):
    with open(filename, mode) as f:
        content = f.read()
    return content


def setup_http_server():
    """Setup a mock HTTP server"""

    http_requests = []

    telegram_msgs = read_file('data/telegram_messages.json')
    telegram_msgs_next = read_file('data/telegram_messages_next.json')

    def request_callback(method, uri, headers):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(uri).query)

        if 'offset' in params and params['offset'] == '319280321':
            body = telegram_msgs_next
        else:
            body = telegram_msgs

        http_requests.append(httpretty.last_request())

        return (200, headers, body)

    httpretty.register_uri(httpretty.GET,
                           TELEGRAM_UPDATES_URL,
                           responses=[
                                httpretty.Response(body=request_callback)
                           ])

    return http_requests


class TestTelegramBotClient(unittest.TestCase):
    """TelegramBotClient unit tests.

    These tests do not check the body of the response, only if the call
    was well formed and if a response was obtained.
    """
    def test_init(self):
        """Test initialization parameters"""

        client = TelegramBotClient(TELEGRAM_TOKEN)
        self.assertEqual(client.bot_token, TELEGRAM_TOKEN)

    @httpretty.activate
    def test_updates(self):
        """Test updates API call"""

        setup_http_server()

        client = TelegramBotClient(TELEGRAM_TOKEN)

        # Check empty params
        client.updates()

        expected = {}

        req = httpretty.last_request()

        self.assertEqual(req.method, 'GET')
        self.assertRegex(req.path, '/bot12345678/getUpdates')
        self.assertDictEqual(req.querystring, expected)

        # Check request with offset
        client.updates(offset=319280321)

        expected = {
                    'offset' : ['319280321']
                   }

        req = httpretty.last_request()

        self.assertEqual(req.method, 'GET')
        self.assertRegex(req.path, '/bot12345678/getUpdates')
        self.assertDictEqual(req.querystring, expected)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
