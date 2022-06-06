
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

from mp4ansi import MP4ansi

import sys
import logging
logger = logging.getLogger(__name__)


class TestMP4ansi(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    def get_client(self):
        process_data = [{'id': 1}, {'id': 2}]
        config = {'key': 'value'}
        return MP4ansi(function=Mock(__name__='mockfunc'), process_data=process_data, config=config)

    @patch('mp4ansi.mp4ansi.MPmq')
    @patch('mp4ansi.mp4ansi.Terminal')
    def test__init_Should_InstantiateTerminal_When_Called(self, terminal_patch, *patches):
        process_data = [{'id': 1}, {'id': 2}]
        config = {'key': 'value'}
        client = MP4ansi(function=Mock(__name__='mockfunc'), process_data=process_data, config=config)
        terminal_patch.assert_called_once_with(len(process_data), config=config, durations={})
        self.assertEqual(client.terminal, terminal_patch.return_value)

    @patch('mp4ansi.mp4ansi.MPmq.get_message')
    def test__get_message_Should_ReturnExpected_When_Match(self, get_message_patch, *patches):
        get_message_patch.return_value = {'offset': None, 'message': '#4-This is the message'}
        client = self.get_client()
        result = client.get_message()
        expected_result = {'offset': 4, 'control': None, 'message': 'This is the message'}
        self.assertEqual(result, expected_result)

    @patch('mp4ansi.mp4ansi.MPmq.get_message')
    def test__get_message_Should_ReturnExpected_When_NoMatch(self, get_message_patch, *patches):
        get_message_patch.return_value = {'offset': None, 'message': 'This is the message'}
        client = self.get_client()
        result = client.get_message()
        expected_result = get_message_patch.return_value
        self.assertEqual(result, expected_result)

    @patch('mp4ansi.mp4ansi.MPmq.get_message')
    def test__get_message_Should_ReturnExpected_When_Offset(self, get_message_patch, *patches):
        get_message_patch.return_value = {'offset': '4', 'message': '#4-This is the message'}
        client = self.get_client()
        result = client.get_message()
        expected_result = get_message_patch.return_value
        self.assertEqual(result, expected_result)

    @patch('mp4ansi.mp4ansi.Terminal')
    def test__process_message_Should_CallExpected_When_Called(self, *patches):
        client = self.get_client()
        client.process_message(4, 'This is the message')
        client.terminal.write_line.assert_called_once_with(4, 'This is the message')

    @patch('mp4ansi.mp4ansi.Terminal')
    def test__process_message_Should_CallExpected_When_Reset(self, *patches):
        client = self.get_client()
        client.process_message(4, 'RESET')
        client.terminal.reset.assert_called_once_with(4)

    @patch('mp4ansi.mp4ansi.Terminal')
    @patch('mp4ansi.mp4ansi.logger')
    def test__process_message_Should_CallExpected_When_NoOffSet(self, logger_patch, *patches):
        client = self.get_client()
        client.process_message(None, 'This is the message')
        logger_patch.warn.assert_called()

    @patch('mp4ansi.mp4ansi.Terminal')
    @patch('mp4ansi.mp4ansi.MPmq.execute_run')
    def test__execute_run_Should_CallExpected_When_Called(self, execute_run_patch, *patches):
        client = self.get_client()
        client.execute_run()
        client.terminal.hide_cursor.assert_called_once_with()
        client.terminal.write_lines.assert_called_once_with()
        execute_run_patch.assert_called_once_with()

    @patch('mp4ansi.mp4ansi.Terminal')
    def test__final_Should_CallExpected_When_Called(self, terminal_patch, *patches):
        client = self.get_client()
        client.final()
        client.terminal.show_cursor.assert_called_once_with()
