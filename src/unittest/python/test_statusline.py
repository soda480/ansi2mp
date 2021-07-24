
# Copyright (c) 2021 Intel Corporation

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#      http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from mock import patch
from mock import call
from mock import Mock
from mock import MagicMock

from mp4ansi.statusline import StatusLine
from mp4ansi.statusline import MAX_CHARS
from mp4ansi.statusline import FILL

import sys
import logging
logger = logging.getLogger(__name__)


class TestStatusLine(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('mp4ansi.statusline.colorama_init')
    @patch('mp4ansi.statusline.StatusLine._get_fill')
    def test__init_Should_SetDefaults_When_Called(self, get_fill_patch, *patches):
        status_line = StatusLine(0)
        self.assertEqual(status_line.index, 0)
        self.assertEqual(status_line.regex, {})
        self.assertIsNone(status_line.duration)
        self.assertEqual(status_line.text, '')
        self.assertEqual(status_line.fill, get_fill_patch.return_value)

    @patch('mp4ansi.statusline.colorama_init')
    @patch('mp4ansi.statusline.StatusLine._get_fill')
    def test__init_Should_SetAttributes_When_AttributesPassed(self, get_fill_patch, *patches):
        status_line = StatusLine(0, fill=2, regex={'key': 'value'})
        self.assertEqual(status_line.index, 0)
        self.assertEqual(status_line.regex, {'key': 'value'})
        self.assertIsNone(status_line.duration)
        self.assertEqual(status_line.text, '')
        self.assertEqual(status_line.fill, get_fill_patch.return_value)

    @patch('mp4ansi.statusline.colorama_init')
    @patch('mp4ansi.statusline.StatusLine._get_fill')
    def test__str_Should_ReturnExpected_When_Called(self, *patches):
        status_line = StatusLine(0)
        result = str(status_line)
        self.assertEqual(result, '\x1b[1m\x1b[33m\x1b[40m0\x1b[0m: ')

    @patch('mp4ansi.statusline.colorama_init')
    @patch('mp4ansi.statusline.StatusLine._get_fill')
    def test__str_Should_ReturnExpected_When_Duration(self, *patches):
        status_line = StatusLine(0)
        status_line.duration = '00:01:23'
        result = str(status_line)
        self.assertEqual(result, '\x1b[1m\x1b[33m\x1b[40m0\x1b[0m:  - 00:01:23')

    @patch('mp4ansi.statusline.colorama_init')
    @patch('mp4ansi.statusline.StatusLine._get_fill')
    def test__pass_Should_DoNothing_When_Called(self, *patches):
        status_line = StatusLine(0)
        status_line.reset()

    @patch('mp4ansi.statusline.colorama_init')
    @patch('mp4ansi.statusline.StatusLine._get_fill')
    @patch('mp4ansi.statusline.StatusLine._sanitize')
    def test__match_Should_SetText_When_Regex(self, sanitize_patch, *patches):
        status_line = StatusLine(0, regex={'text': 'hello world'})
        status_line.match('hello world')
        self.assertEqual(status_line.text, sanitize_patch.return_value)

    @patch('mp4ansi.statusline.colorama_init')
    @patch('mp4ansi.statusline.StatusLine._get_fill')
    @patch('mp4ansi.statusline.StatusLine._sanitize')
    def test__match_Should_SetText_When_NoRegex(self, sanitize_patch, *patches):
        status_line = StatusLine(0)
        status_line.match('hello world')
        self.assertEqual(status_line.text, sanitize_patch.return_value)

    def test__sanitize_Should_ReturnExpected_When_LessThanMaxChars(self, *patches):
        text = 'hello world'
        result = StatusLine._sanitize(text)
        self.assertEqual(result, text.ljust(MAX_CHARS))

    def test__sanitize_Should_ReturnExpected_When_GreaterThanMaxChars(self, *patches):
        text = 'hello' * 40
        result = StatusLine._sanitize(text)
        expected_result = f'{text[0:MAX_CHARS - 3]}...'
        self.assertEqual(result, expected_result)

    def test__sanitize_Should_ReturnExpected_When_NoText(self, *patches):
        text = ''
        result = StatusLine._sanitize(text)
        self.assertEqual(result, text)

    def test__get_fill_Should_ReturnExpected_When_NoData(self, *patches):
        result = StatusLine._get_fill(None)
        expected_result = {'index': FILL}
        self.assertEqual(result, expected_result)

    def test__get_fill_Should_ReturnExpected_When_Data(self, *patches):
        result = StatusLine._get_fill({'max_index': 203})
        expected_result = {'index': 3}
        self.assertEqual(result, expected_result)
