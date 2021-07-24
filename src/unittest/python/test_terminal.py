
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
        term = Terminal(4)
        self.assertEqual(term.config, {})
        self.assertEqual(term.current, 0)
        self.assertEqual(term.terminal, create_patch.return_value)

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

    @patch('mp4ansi.terminal.ProgressBar')
    def test__create_progress_bars_Should_ReturnExpected_When_TotalIsStr(self, *patches):
        term = Terminal(10, create=False, config={'progress_bar': {'total': '--regex--', 'count_regex': '--regex--'}})
        result = term.create_progress_bars(10)
        self.assertTrue(len(result), 10)

    @patch('mp4ansi.terminal.ProgressBar')
    def test__create_progress_bars_Should_ReturnExpected_When_TotalIsInt(self, *patches):
        term = Terminal(10, create=False, config={'progress_bar': {'total': 100, 'count_regex': '--regex--'}})
        result = term.create_progress_bars(10)
        self.assertTrue(len(result), 10)

    @patch('mp4ansi.terminal.StatusLine')
    def test__create_status_lines_Should_ReturnExpected_When_Called(self, *patches):
        term = Terminal(10, create=False)
        result = term.create_status_lines(10)
        self.assertTrue(len(result), 10)

    @patch('mp4ansi.terminal.Terminal.create_progress_bars')
    def test__create_Should_CallAndReturnExpected_When_ProgressBar(self, create_progress_bars_patch, *patches):
        term = Terminal(10, create=False, config={'progress_bar': {'total': 100, 'count_regex': '--regex--'}})
        result = term.create(10)
        self.assertEqual(result, create_progress_bars_patch.return_value)

    @patch('mp4ansi.terminal.Terminal.create_status_lines')
    def test__create_Should_CallAndReturnExpected_When_NoProgressBar(self, create_status_lines_patch, *patches):
        term = Terminal(10, create=False)
        result = term.create(10)
        self.assertEqual(result, create_status_lines_patch.return_value)

    @patch('mp4ansi.Terminal.get_move_char')
    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__write_Should_CallExpected_When_Tty(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        term = Terminal(13, create=True)
        term.current = 0
        term.write(3)
        self.assertEqual(len(print_patch.mock_calls), 2)
        self.assertEqual(term.current, 1)

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__write_Should_CallExpected_When_Notty(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        term = Terminal(13, create=True)
        term.current = 0
        term.write(3)
        print_patch.assert_not_called()
        self.assertEqual(term.current, 0)

    @patch('mp4ansi.Terminal.get_move_char')
    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__write_Should_CallExpected_When_NoTtyButForce(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        term = Terminal(13, create=True)
        term.current = 0
        term.write(3, force=True)
        self.assertEqual(len(print_patch.mock_calls), 2)
        self.assertEqual(term.current, 1)

    @patch('mp4ansi.Terminal.write')
    def test__write_line_Should_CallExpected_When_Called(self, write_patch, *patches):
        term = Terminal(13, create=True)
        term.write_line(4, '--some-text--')
        write_patch.assert_called_once_with(4)

    @patch('mp4ansi.Terminal.write')
    def test__write_lines_Should_CallExpected_When_Called(self, write_patch, *patches):
        term = Terminal(3)
        term.write_lines()
        self.assertEqual(len(write_patch.mock_calls), 3)

    @patch('mp4ansi.Terminal.write')
    def test__write_lines_Should_CallExpected_When_AddDuration(self, write_patch, *patches):
        trmnl = Terminal(3, durations={'0': 'd1', '1': 'd2', '2': 'd3'})
        trmnl.current = 0
        trmnl.write_lines(add_duration=True)
        self.assertEqual(len(write_patch.mock_calls), 3)

    @patch('mp4ansi.terminal.StatusLine')
    def test__reset_Should_CallExpected_When_Called(self, *patches):
        term = Terminal(3)
        term.reset(1)
        term.terminal[1].reset.assert_called_once()

    @patch('mp4ansi.Terminal.move_up')
    def test__get_move_char_Should_ReturnExpected_When_MovingUp(self, move_up_patch, *patches):
        move_up_patch.return_value = Mock(), Mock()
        term = Terminal(13, create=False)
        term.current = 12
        result = term.get_move_char(7)
        self.assertEqual(result, move_up_patch.return_value)

    @patch('mp4ansi.Terminal.move_down')
    def test__get_move_char_Should_ReturnExpected_When_MovingDown(self, move_down_patch, *patches):
        term = Terminal(13, create=False)
        term.current = 2
        result = term.get_move_char(7)
        self.assertEqual(result, move_down_patch.return_value)

    @patch('mp4ansi.Terminal.move_down')
    def test__get_move_char_Should_ReturnExpected_When_NotMoving(self, move_down_patch, *patches):
        term = Terminal(13, create=False)
        term.current = 2
        result = term.get_move_char(2)
        self.assertEqual(result, '')

    @patch('mp4ansi.terminal.Cursor.DOWN')
    def test__move_down_Should_CallExpected_When_Called(self, down_patch, *patches):
        term = Terminal(13, create=False)
        term.current = 2
        result = term.move_down(7)
        self.assertEqual(result, down_patch.return_value)
        self.assertEqual(term.current, 7)

    @patch('mp4ansi.terminal.Cursor.UP')
    def test__move_up_Should_ReturnExpected_When_Called(self, up_patch, *patches):
        term = Terminal(13, create=False)
        term.current = 12
        result = term.move_up(7)
        self.assertEqual(result, up_patch.return_value)
        self.assertEqual(term.current, 7)

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__hide_cursor_Should_CallExpected_When_Called(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        term = Terminal(3, create=False)
        term.hide_cursor()
        print_patch.assert_called_once_with(HIDE_CURSOR, end='', file=stderr_patch)

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__hide_cursor_Should_CallExpected_When_NoAtty(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        term = Terminal(3, create=False)
        term.hide_cursor()
        print_patch.assert_not_called()

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__show_cursor_Should_CallExpected_When_Called(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        term = Terminal(3, create=False)
        term.show_cursor()
        print_patch.assert_called_once_with(SHOW_CURSOR, end='', file=stderr_patch)

    @patch('mp4ansi.terminal.sys.stderr')
    @patch('builtins.print')
    def test__show_cursor_Should_CallExpected_When_NoAtty(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        term = Terminal(3, create=False)
        term.show_cursor()
        print_patch.assert_not_called()
