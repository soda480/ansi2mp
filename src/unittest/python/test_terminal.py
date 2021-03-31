
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
from mp4ansi.terminal import PROGRESS_BAR_WIDTH
from mp4ansi.terminal import MAX_CHARS
from mp4ansi.terminal import HIDE_CURSOR
from mp4ansi.terminal import SHOW_CURSOR

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
        self.assertEqual(trmnl.lines, 4)
        self.assertEqual(trmnl.zfill, 1)
        self.assertEqual(trmnl.config, {})
        self.assertIsNone(trmnl.current)
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
            Terminal(51)

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
        result = trmnl.create()
        expected_result = [
            {
                'id': '0',
                'text': '',
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
        self.assertTrue(trmnl.terminal[0]['id_matched'])

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
        offset = 3
        text = '-text-'
        trmnl.get_progress_text(offset, text)
        assign_total_patch.assert_called_once_with(offset, text)

    @patch('mp4ansi.Terminal.assign_total')
    def test__get_progress_text_Should_ReturnExpected_When_CountIsEqualToTotal(self, *patches):
        config = {'progress_bar': {'total': 121372, 'count_regex': '-regex-'}}
        trmnl = Terminal(13, config=config)
        offset = 3
        trmnl.terminal[offset]['count'] = 121372
        trmnl.terminal[offset]['total'] = 121372
        text = '-text-'
        trmnl.get_progress_text(offset, text)
        result = trmnl.get_progress_text(offset, text)
        self.assertEqual(result, 'Processing complete')

    @patch('mp4ansi.Terminal.assign_total')
    def test__get_progress_text_Should_IncrementCount_When_CountRegexMatch(self, *patches):
        config = {'progress_bar': {'total': 121372, 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        offset = 3
        trmnl.terminal[offset]['count'] = 41407
        trmnl.terminal[offset]['total'] = 121372
        trmnl.terminal[offset]['modulus'] = round(trmnl.terminal[offset]['total'] / PROGRESS_BAR_WIDTH)
        text = 'processed 41408'
        trmnl.get_progress_text(offset, text)
        self.assertEqual(trmnl.terminal[offset]['count'], 41408)

    @patch('mp4ansi.Terminal.assign_total')
    def test__get_progress_text_Should_IncrementCount_When_Modulus(self, *patches):
        config = {'progress_bar': {'total': 8000, 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        offset = 3
        trmnl.terminal[offset]['count'] = 3999
        trmnl.terminal[offset]['total'] = 8000
        trmnl.terminal[offset]['modulus'] = round(trmnl.terminal[offset]['total'] / PROGRESS_BAR_WIDTH)
        text = 'processed 4000'
        result = trmnl.get_progress_text(offset, text)
        self.assertTrue('Processing' in result)
        self.assertTrue('4000/8000' in result)
        self.assertTrue('50%' in result)

    @patch('mp4ansi.Terminal.assign_total')
    def test__get_progress_text_Should_IncrementCount_When_CountRegexAndCountIsEqualToTotal(self, *patches):
        config = {'progress_bar': {'total': 8001, 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        offset = 3
        trmnl.terminal[offset]['count'] = 8000
        trmnl.terminal[offset]['total'] = 8001
        trmnl.terminal[offset]['modulus'] = round(trmnl.terminal[offset]['total'] / PROGRESS_BAR_WIDTH)
        text = 'processed 8001'
        result = trmnl.get_progress_text(offset, text)
        self.assertTrue('Processing' in result)
        self.assertTrue('8001/8001' in result)
        self.assertTrue('100%' in result)

    @patch('builtins.print')
    @patch('mp4ansi.Terminal.sanitize')
    @patch('mp4ansi.Terminal.move')
    @patch('mp4ansi.Terminal.assign_id')
    def test__write_line_Should_CallAssignId_When_IdRegexAndNotIdMatched(self, assign_id_patch, *patches):
        config = {'id_regex': r'^processor id (?P<value>.*)$'}
        trmnl = Terminal(13, config=config)
        trmnl.current = 0
        offset = 1
        text = 'processor id a1d4d73dce34'
        trmnl.write_line(offset, text, ignore_progress=True)
        assign_id_patch.assert_called_once_with(offset, text)

    @patch('mp4ansi.Terminal.get_progress_text', return_value=None)
    @patch('builtins.print')
    def test__write_line_Should_ReturnAndCallExpected_When_GetProgressTextReturnsNothing(self, print_patch, *patches):
        config = {'progress_bar': {'total': 8001, 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        offset = 3
        text = 'processed 8001'
        result = trmnl.write_line(offset, text)
        self.assertIsNone(result)
        print_patch.assert_not_called()

    @patch('mp4ansi.Terminal.get_progress_text', return_value='something')
    @patch('mp4ansi.Terminal.move')
    @patch('builtins.print')
    def test__write_line_Should_ReturnAndCallExpected_When_GetProgressTextReturnsSomething(self, print_patch, *patches):
        config = {'progress_bar': {'total': 8001, 'count_regex': r'^processed (?P<value>\d+)$'}}
        trmnl = Terminal(13, config=config)
        trmnl.current = 0
        offset = 3
        text = 'processed 8001'
        trmnl.write_line(offset, text)
        print_patch.assert_called()

    @patch('mp4ansi.Terminal.move_up')
    def test__move_Should_ReturnExpected_When_MovingUp(self, move_up_patch, *patches):
        move_up_patch.return_value = Mock(), Mock()
        trmnl = Terminal(13, create=False)
        trmnl.current = 12
        result = trmnl.move(7)
        self.assertEqual(result, move_up_patch.return_value)

    @patch('mp4ansi.Terminal.move_down')
    def test__move_Should_ReturnExpected_When_MovingDown(self, move_down_patch, *patches):
        trmnl = Terminal(13, create=False)
        trmnl.current = 2
        result = trmnl.move(7)
        self.assertEqual(result, move_down_patch.return_value)

    @patch('mp4ansi.Terminal.move_down')
    def test__move_Should_ReturnExpected_When_NotMoving(self, move_down_patch, *patches):
        trmnl = Terminal(13, create=False)
        trmnl.current = 2
        result = trmnl.move(2)
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
    def test__write_Should_CallExpected_When_CurrentIsNone(self, write_line_patch, *patches):
        trmnl = Terminal(3)
        trmnl.write(ignore_progress=True)
        self.assertEqual(len(write_line_patch.mock_calls), 3)
        self.assertEqual(trmnl.current, 0)

    @patch('mp4ansi.Terminal.write_line')
    def test__write_Should_CallExpected_When_CurrentIsNotNone(self, write_line_patch, *patches):
        trmnl = Terminal(3)
        trmnl.current = 0
        trmnl.write(ignore_progress=True)
        self.assertEqual(len(write_line_patch.mock_calls), 3)

    def test__sanitize_Should_ReturnExpected_When_LessThanMaxChars(self, *patches):
        trmnl = Terminal(3, create=False)
        text = 'hello world'
        result = trmnl.sanitize(text)
        self.assertEqual(result, text)

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

    @patch('builtins.print')
    def test__cursor_Should_CallExpected_When_Hide(self, print_patch, *patches):
        trmnl = Terminal(3, create=False)
        trmnl.cursor()
        print_patch.assert_called_once_with(HIDE_CURSOR, end='')

    @patch('builtins.print')
    def test__cursor_Should_CallExpected_When_NoHide(self, print_patch, *patches):
        trmnl = Terminal(3, create=False)
        trmnl.cursor(hide=False)
        print_patch.assert_called_once_with(SHOW_CURSOR, end='')
