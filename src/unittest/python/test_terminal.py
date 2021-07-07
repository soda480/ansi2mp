
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

from mp4ansi import Terminal
from mp4ansi.terminal import MAX_LINES
from mp4ansi.terminal import PROGRESS_BAR_WIDTH
from mp4ansi.terminal import MAX_CHARS
from mp4ansi.terminal import HIDE_CURSOR
from mp4ansi.terminal import SHOW_CURSOR
from mp4ansi.terminal import ID_WIDTH

import sys
import logging
logger = logging.getLogger(__name__)


class TestTerminal(unittest.TestCase):

    def setUp(self):
        """
        """
        pass

    def tearDown(self):
        """
        """
        pass

    @patch('mp4ansi.Terminal.validate_lines')
    @patch('mp4ansi.Terminal.validate_config')
    @patch('mp4ansi.terminal.colorama_init')
    @patch('mp4ansi.Terminal.create')
    def test__init__Should_SetAttributes_When_Called(self, create_patch, *patches):
        trmnl = Terminal(4)
        self.assertEqual(trmnl.config, {})
        self.assertEqual(trmnl.current, 0)
        self.assertEqual(trmnl.terminal, create_patch.return_value)

    @patch('mp4ansi.Terminal.validate_config')
    @patch('mp4ansi.terminal.colorama_init')
    @patch('mp4ansi.Terminal.create')
    def test__validate_lines_Should_RaiseValueError_When_LinesLessThanZero(self, *patches):
        with self.assertRaises(ValueError):
            Terminal(-1)

    @patch('mp4ansi.Terminal.validate_config')
    @patch('mp4ansi.terminal.colorama_init')
    @patch('mp4ansi.Terminal.create')
    def test__validate_lines_Should_RaiseValueError_When_GreaterThanMaxLines(self, *patches):
        with self.assertRaises(ValueError):
            Terminal(MAX_LINES + 1)

    @patch('mp4ansi.Terminal.validate_lines')
    @patch('mp4ansi.terminal.colorama_init')
    def test__validate_config_Should_RaiseValueError_When_NotRequiredKeys(self, *patches):
        config = {'progress_bar': {'key1': 'value1'}}
        with self.assertRaises(ValueError):
            Terminal(4, config=config, create=False)

    @patch('mp4ansi.Terminal.validate_lines')
    @patch('mp4ansi.terminal.colorama_init')
    def test__validate_config_Should_RaiseValueError_When_InvalidProgressBarTotal(self, *patches):
        config = {'progress_bar': {'total': [], 'count_regex': '-regex-'}}
        with self.assertRaises(ValueError):
            Terminal(4, config=config, create=False)

    @patch('mp4ansi.Terminal.validate_lines')
    @patch('mp4ansi.Terminal.validate_config')
    @patch('mp4ansi.terminal.colorama_init')
    def test__create_Should_ReturnExpected_When_Called(self, *patches):
        config = {'progress_bar': {'total': 10, 'count_regex': '-regex-'}}
        trmnl = Terminal(1, create=False, config=config)
        result = trmnl.create(1)
        expected_result = [
            {
                'id': '',
                'text': '',
                'index': '0',
                'count': 0,
                'modulus_count': 0,
                'total': None
            }
        ]
        self.assertEqual(result, expected_result)

    def test__assign_id_Should_SetExpected_When_Matched(self, *patches):
        config = {'id_regex': r'^id is (?P<value>.*)$'}
        trmnl = Terminal(1, config=config)
        trmnl.assign_id(0, 'id is abcd123')
        self.assertEqual(trmnl.terminal[0]['id'], 'abcd123')

    def test__assign_id_Should_SetExpected_When_MatchedGreaterThanIdWidth(self, *patches):
        config = {'id_regex': r'^id is (?P<value>.*)$'}
        trmnl = Terminal(1, config=config)
        trmnl.assign_id(0, 'id is The longest word in any given language depends on the word formation rules of each specific language.')
        self.assertEqual(trmnl.terminal[0]['id'], 'The longest word in any given language depends on the word formation rules of each specific langu...')

    def test__assign_id_Should_NotSet_When_NotMatched(self, *patches):
        config = {'id_regex': r'^id is (?P<value>.*)$'}
        trmnl = Terminal(1, config=config)
        trmnl.terminal[0]['id_matched'] = False
        trmnl.assign_id(0, 'this is a message')
        self.assertFalse(trmnl.terminal[0]['id_matched'])

    def test__assign_total_Should_SetExpected_When_TotalIsStr(self, *patches):
        config = {'progress_bar': {'total': r'^total is (?P<value>\d+)$', 'count_regex': '-regex-'}}
        trmnl = Terminal(1, config=config)
        trmnl.assign_total(0, 'total is 121372')
        self.assertEqual(trmnl.terminal[0]['total'], 121372)

    def test__assign_total_Should_SetExpected_When_TotalIsStrNoMatch(self, *patches):
        config = {'progress_bar': {'total': r'^total is (?P<value>\d+)$', 'count_regex': '-regex-'}}
        trmnl = Terminal(1, config=config)
        trmnl.terminal[0]['total'] = None
        trmnl.assign_total(0, 'this is a message')
        self.assertIsNone(trmnl.terminal[0]['total'])

    def test__assign_total_Should_SetExpected_When_TotalIsInt(self, *patches):
        config = {'progress_bar': {'total': 121372, 'count_regex': '-regex-'}}
        trmnl = Terminal(1, config=config)
        trmnl.assign_total(0, 'some message')
        self.assertEqual(trmnl.terminal[0]['total'], 121372)
        self.assertEqual(trmnl.terminal[0]['modulus'], round(121372 / PROGRESS_BAR_WIDTH))

    def test__assign_total_Should_SetExpected_When_ComputedModulusIsZero(self, *patches):
        config = {'progress_bar': {'total': 10, 'count_regex': '-regex-'}}
        trmnl = Terminal(1, config=config)
        trmnl.assign_total(0, 'some message')
        self.assertEqual(trmnl.terminal[0]['modulus'], 1)

    @patch('mp4ansi.Terminal.assign_total')
    def test__get_progress_text_Should_CallAssignTotal_When_NoTotal(self, assign_total_patch, *patches):
        config = {'progress_bar': {'total': 121372, 'count_regex': '-regex-'}}
        trmnl = Terminal(13, config=config)
        index = 3
        text = '-text-'
        trmnl.get_progress_text(index, text)
        assign_total_patch.assert_called_once_with(index, text)

    @patch('mp4ansi.Terminal.assign_total')
    def test__get_progress_text_Should_ReturnExpected_When_CountIsEqualToTotal(self, *patches):
        config = {'progress_bar': {'total': 121372, 'count_regex': '-regex-'}}
        durations = {'3': '0:03:23'}
        trmnl = Terminal(13, config=config, durations=durations)
        index = 3
        trmnl.terminal[index]['count'] = 121372
        trmnl.terminal[index]['total'] = 121372
        text = '-text-'
        trmnl.get_progress_text(index, text)
        result = trmnl.get_progress_text(index, text)
        self.assertEqual(result, 'Processing complete')

    @patch('mp4ansi.Terminal.assign_total')
    def test__get_progress_text_Should_IncrementCount_When_CountRegexMatch(self, *patches):
        config = {'progress_bar': {'total': 121372, 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        index = 3
        trmnl.terminal[index]['count'] = 41407
        trmnl.terminal[index]['total'] = 121372
        trmnl.terminal[index]['modulus'] = round(trmnl.terminal[index]['total'] / PROGRESS_BAR_WIDTH)
        text = 'processed 41408'
        trmnl.get_progress_text(index, text)
        self.assertEqual(trmnl.terminal[index]['count'], 41408)

    @patch('mp4ansi.Terminal.assign_total')
    def test__get_progress_text_Should_IncrementCount_When_Modulus(self, *patches):
        config = {'progress_bar': {'total': 8000, 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        index = 3
        trmnl.terminal[index]['count'] = 3999
        trmnl.terminal[index]['total'] = 8000
        trmnl.terminal[index]['modulus'] = round(trmnl.terminal[index]['total'] / PROGRESS_BAR_WIDTH)
        text = 'processed 4000'
        result = trmnl.get_progress_text(index, text)
        self.assertTrue('Processing' in result)
        self.assertTrue('4000/8000' in result)
        self.assertTrue('50%' in result)

    @patch('mp4ansi.Terminal.assign_total')
    def test__get_progress_text_Should_IncrementCount_When_CountRegexAndCountIsEqualToTotal(self, *patches):
        config = {'progress_bar': {'total': 8001, 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        index = 3
        trmnl.terminal[index]['count'] = 8000
        trmnl.terminal[index]['total'] = 8001
        trmnl.terminal[index]['modulus'] = round(trmnl.terminal[index]['total'] / PROGRESS_BAR_WIDTH)
        text = 'processed 8001'
        result = trmnl.get_progress_text(index, text)
        self.assertTrue('Processing' in result)
        self.assertTrue('8001/8001' in result)
        self.assertTrue('100%' in result)

    @patch('mp4ansi.Terminal.assign_total', return_value=True)
    def test__get_progress_text_Should_ReturnExpected_When_TotalAssigned(self, *patches):
        config = {'progress_bar': {'total': r'^total is (?P<value>\d+)$', 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        index = 3
        trmnl.terminal[index]['count'] = 0
        text = 'total is 8001'
        result = trmnl.get_progress_text(index, text)
        self.assertTrue('Processing' in result)
        self.assertTrue('0%' in result)

    @patch('mp4ansi.Terminal.assign_total', return_value=False)
    def test__get_progress_text_Should_ReturnExpected_When_TotalNotAssigned(self, *patches):
        config = {'progress_bar': {'total': r'^total is (?P<value>\d+)$', 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        index = 3
        trmnl.terminal[index]['count'] = 0
        text = 'total is 8001'
        result = trmnl.get_progress_text(index, text)
        self.assertIsNone(result)

    @patch('mp4ansi.Terminal.sanitize')
    def test__get_matched_text_Should_ReturnExpected_When_Match(self, sanitize_patch, *patches):
        config = {'id_regex': r'^processor id (?P<value>.*)$', 'text_regex': '^some-text$'}
        trmnl = Terminal(13, config=config)
        result = trmnl.get_matched_text('some-text')
        sanitize_patch.assert_called_once_with('some-text')
        self.assertEqual(result, sanitize_patch.return_value)

    def test__get_matched_text_Should_ReturnExpected_When_NoMatch(self, *patches):
        config = {'id_regex': r'^processor id (?P<value>.*)$', 'text_regex': '^some-text$'}
        trmnl = Terminal(13, config=config)
        result = trmnl.get_matched_text('some-other-text')
        self.assertIsNone(result)

    @patch('mp4ansi.Terminal.write')
    @patch('mp4ansi.Terminal.assign_id')
    def test__write_line_Should_CallAssignId_When_IdRegexAndNotIdMatched(self, assign_id_patch, *patches):
        config = {'id_regex': r'^processor id (?P<value>.*)$'}
        trmnl = Terminal(13, config=config, durations={'1': '0:01:23'})
        index = 1
        text = 'some text'
        trmnl.write_line(index, text)
        assign_id_patch.assert_called_once_with(index, text)

    @patch('mp4ansi.Terminal.get_progress_text', return_value='something')
    @patch('mp4ansi.Terminal.write')
    def test__write_line_Should_ReturnAndCallExpected_When_GetProgressTextReturnsSomething(self, write_patch, *patches):
        config = {'progress_bar': {'total': 8001, 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        index = 3
        text = 'processed 8001'
        trmnl.write_line(index, text)
        write_patch.assert_called()

    @patch('mp4ansi.Terminal.sanitize')
    @patch('mp4ansi.Terminal.write')
    def test__write_line_Should_ReturnAndCallExpected_When_NoProgressBar(self, write_patch, sanitize_patch, *patches):
        trmnl = Terminal(13)
        index = 3
        text = 'processed 8001'
        trmnl.write_line(index, text)
        write_patch.assert_called()
        sanitize_patch.assert_called_once_with(text)

    @patch('mp4ansi.Terminal.get_progress_text', return_value=None)
    @patch('mp4ansi.Terminal.write')
    @patch('mp4ansi.Terminal.assign_id')
    def test__write_line_Should_CallExpected_When_IdAssignedProgressBar(self, assign_id_patch, write_patch, *patches):
        config = {'id_regex': r'^processor id (?P<value>.*)$', 'progress_bar': {'total': 8001, 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        index = 1
        text = 'processor id 121372'
        trmnl.write_line(index, text)
        assign_id_patch.assert_called_once_with(index, text)
        write_patch.assert_called()

    @patch('mp4ansi.Terminal.sanitize')
    @patch('mp4ansi.Terminal.write')
    def test__write_line_Should_ReturnAndCallExpected_When_PrintTextAndAddDuration(self, write_patch, sanitize_patch, *patches):
        sanitize_patch.return_value = '--sanitized-text--'
        trmnl = Terminal(13, durations={'3': '0:01:23'})
        index = 3
        text = 'processed 8001'
        trmnl.write_line(index, text, add_duration=True)
        write_patch.assert_called()
        self.assertEqual(write_patch.mock_calls[0][1][2], f'{sanitize_patch.return_value} - 0:01:23')
        sanitize_patch.assert_called_once_with(text)

    @patch('mp4ansi.Terminal.sanitize')
    @patch('mp4ansi.Terminal.get_matched_text')
    @patch('mp4ansi.Terminal.write')
    def test__write_line_Should_ReturnAndCallExpected_When_TextRegex(self, write_patch, get_matched_text, *patches):
        config = {'id_regex': r'^processor id (?P<value>.*)$', 'text_regex': '^some-regex$'}
        trmnl = Terminal(13, config=config)
        index = 1
        text = 'processor id 121372'
        trmnl.write_line(index, text)
        get_matched_text.assert_called_once_with(text)
        write_patch.assert_called()

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('mp4ansi.Terminal.get_move_char')
    @patch('builtins.print')
    def test__write_Should_CallExpected_When_NoText(self, print_patch, get_move_char_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        trmnl = Terminal(13, create=False)
        trmnl.current = 0
        index = 3
        trmnl.write(index, None, None)
        print_patch.assert_called_once_with(get_move_char_patch.return_value, file=stderr_patch)

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('mp4ansi.Terminal.get_move_char')
    @patch('builtins.print')
    def test__write_Should_CallExpected_When_Text(self, print_patch, get_move_char_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        trmnl = Terminal(13, create=True)
        trmnl.current = 0
        index = 3
        id_ = '123456'
        text = 'hello world'
        trmnl.write(index, id_, text)
        self.assertEqual(len(print_patch.mock_calls), 2)

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__write_Should_CallExpected_When_Notty(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        trmnl = Terminal(13, create=True)
        trmnl.current = 0
        index = 3
        id_ = '123456'
        text = 'hello world'
        trmnl.write(index, id_, text)
        print_patch.assert_not_called()

    @patch('mp4ansi.Terminal.move_up')
    def test__get_move_char_Should_ReturnExpected_When_MovingUp(self, move_up_patch, *patches):
        move_up_patch.return_value = Mock(), Mock()
        trmnl = Terminal(13, create=False)
        trmnl.current = 12
        result = trmnl.get_move_char(7)
        self.assertEqual(result, move_up_patch.return_value)

    @patch('mp4ansi.Terminal.move_down')
    def test__get_move_char_Should_ReturnExpected_When_MovingDown(self, move_down_patch, *patches):
        trmnl = Terminal(13, create=False)
        trmnl.current = 2
        result = trmnl.get_move_char(7)
        self.assertEqual(result, move_down_patch.return_value)

    @patch('mp4ansi.Terminal.move_down')
    def test__get_move_char_Should_ReturnExpected_When_NotMoving(self, move_down_patch, *patches):
        trmnl = Terminal(13, create=False)
        trmnl.current = 2
        result = trmnl.get_move_char(2)
        self.assertEqual(result, '')

    @patch('mp4ansi.terminal.Cursor.DOWN')
    def test__move_down_Should_CallExpected_When_Called(self, down_patch, *patches):
        trmnl = Terminal(13, create=False)
        trmnl.current = 2
        result = trmnl.move_down(7)
        self.assertEqual(result, down_patch.return_value)
        self.assertEqual(trmnl.current, 7)

    @patch('mp4ansi.terminal.Cursor.UP')
    def test__move_up_Should_ReturnExpected_When_Called(self, up_patch, *patches):
        trmnl = Terminal(13, create=False)
        trmnl.current = 12
        result = trmnl.move_up(7)
        self.assertEqual(result, up_patch.return_value)
        self.assertEqual(trmnl.current, 7)

    @patch('mp4ansi.Terminal.write_line')
    def test__write_lines_Should_CallExpected_When_CurrentIsNone(self, write_line_patch, *patches):
        trmnl = Terminal(3)
        trmnl.write_lines()
        self.assertEqual(len(write_line_patch.mock_calls), 3)
        self.assertEqual(trmnl.current, 0)

    @patch('mp4ansi.Terminal.write_line')
    def test__write_lines_Should_CallExpected_When_CurrentIsNotNone(self, write_line_patch, *patches):
        trmnl = Terminal(3)
        trmnl.current = 0
        trmnl.write_lines()
        self.assertEqual(len(write_line_patch.mock_calls), 3)

    def test__sanitize_Should_ReturnExpected_When_LessThanMaxChars(self, *patches):
        trmnl = Terminal(3, create=False)
        text = 'hello world'
        result = trmnl.sanitize(text)
        self.assertEqual(result, text.ljust(MAX_CHARS))

    def test__sanitize_Should_ReturnExpected_When_GreaterThanMaxChars(self, *patches):
        trmnl = Terminal(3, create=False)
        text = 'hello' * 40
        result = trmnl.sanitize(text)
        expected_result = f'{text[0:MAX_CHARS - 3]}...'
        self.assertEqual(result, expected_result)

    def test__sanitize_Should_ReturnExpected_When_NoText(self, *patches):
        trmnl = Terminal(3, create=False)
        text = ''
        result = trmnl.sanitize(text)
        self.assertEqual(result, text)

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__hide_cursor_Should_CallExpected_When_Called(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        trmnl = Terminal(3, create=False)
        trmnl.hide_cursor()
        print_patch.assert_called_once_with(HIDE_CURSOR, end='', file=stderr_patch)

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__hide_cursor_Should_CallExpected_When_NoAtty(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        trmnl = Terminal(3, create=False)
        trmnl.hide_cursor()
        print_patch.assert_not_called()

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__show_cursor_Should_CallExpected_When_Called(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        trmnl = Terminal(3, create=False)
        trmnl.show_cursor()
        print_patch.assert_called_once_with(SHOW_CURSOR, end='', file=stderr_patch)

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__show_cursor_Should_CallExpected_When_NoAtty(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        trmnl = Terminal(3, create=False)
        trmnl.show_cursor()
        print_patch.assert_not_called()

    def test__get_id_width_Should_ReturnDefault_When_NoIdWidthInConfig(self, *patches):
        trmnl = Terminal(3, create=False, config={'id_regex': 'regex'})
        result = trmnl.get_id_width()
        self.assertEqual(result, ID_WIDTH)

    def test__get_id_width_Should_ReturnConfigIdWidth_When_IdWidthInConfig(self, *patches):
        trmnl = Terminal(3, create=False, config={'id_regex': 'regex', 'id_width': 20})
        result = trmnl.get_id_width()
        self.assertEqual(result, 20)

    def test__get_id_width_Should_ReturnDefaultIdWidth_When_IdWidthInConfigExceedsDefault(self, *patches):
        trmnl = Terminal(3, create=False, config={'id_regex': 'regex', 'id_width': ID_WIDTH + 1})
        result = trmnl.get_id_width()
        self.assertEqual(result, ID_WIDTH)

    @patch('mp4ansi.Terminal.assign_id', return_value=None)
    def test__get_identifier_Should_ReturnExpected_When_AssignIdNone(self, *patches):
        trmnl = Terminal(1, create=False, config={'id_regex': 'regex'})
        trmnl.terminal = [{'id': '--id--'}]
        identifier, assigned = trmnl.get_identifier(0, 'text')
        self.assertFalse(assigned)

    def test__reset_Should_CallExpected_When_ProgressBar(self, *patches):
        config = {'progress_bar': {'total': 10, 'count_regex': '-count-regex-'}}
        trmnl = Terminal(4, config=config)
        trmnl.terminal[2]['count'] = 10
        trmnl.terminal[2]['text'] = 'some text'
        trmnl.reset(2)
        self.assertEqual(trmnl.terminal[2]['count'], 0)
        self.assertEqual(trmnl.terminal[2]['text'], '')

    def test__reset_Should_CallExpected_When_NoProgressBar(self, *patches):
        trmnl = Terminal(4)
        trmnl.terminal[2]['text'] = 'some text'
        trmnl.reset(2)
        self.assertEqual(trmnl.terminal[2]['text'], '')
