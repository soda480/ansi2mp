#   -*- coding: utf-8 -*-
import sys
import logging
from colorama import init as colorama_init
from colorama import Cursor
from mp4ansi.progressbar import ProgressBar

logger = logging.getLogger(__name__)

MAX_LINES = 75
HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'
CLEAR_EOL = '\033[K'


class Terminal():
    """ simple ANSI terminal
        represented internally as a list of dictionaries
        ability to move up or down and print text at specified index
    """
    def __init__(self, number_of_lines, config=None, durations=None, create=True):
        """ class constructor
        """
        logger.debug('executing Terminal constructor')
        self.validate_lines(number_of_lines)
        if not config:
            config = {}
        self.validate_config(config)
        self.config = config
        colorama_init()
        self.current = 0
        self.durations = durations
        if create:
            self.terminal = self.create(number_of_lines)

    def validate_lines(self, number_of_lines):
        """ validate number_of_lines
        """
        if number_of_lines < 0 or number_of_lines > MAX_LINES:
            raise ValueError(f'lines must be between 1-{MAX_LINES}')

    def validate_config(self, config):
        """ validate progress bar
        """
        if 'progress_bar' in config:
            keys = config['progress_bar'].keys()
            required_keys = ['total', 'count_regex']

            if not all(item in keys for item in required_keys):
                raise ValueError(f'progress_bar config does not contain all the required parameters: {required_keys}')

            if not isinstance(config['progress_bar']['total'], (str, int)):
                raise ValueError('progress_bar.total must be an integer or string')

    def create(self, number_of_lines):
        """ return list of dictionaries representing terminal for config
        """
        logger.debug('creating terminal')
        terminal = []
        # zfill = len(str(number_of_lines))

        progress_bar_config = self.config.get('progress_bar', {})

        regex = {
            'total': None,
            'count': progress_bar_config.get('count_regex'),
            'alias': self.config.get('id_regex')
        }
        total = None
        if isinstance(progress_bar_config.get('total'), str):
            regex['total'] = self.config['progress_bar']['total']
        else:
            total = progress_bar_config.get('total')

        for index in range(number_of_lines):
            progress_bar = ProgressBar(
                index,
                total=total,
                fill=progress_bar_config.get('max_digits'),
                regex=regex,
                message=progress_bar_config.get('progress_message'))
            terminal.append(progress_bar)
        return terminal

    def write_line(self, index, text):
        """ write line at index
        """
        self.terminal[index].match(text)
        self.write(index)

    def write(self, index, force=False):
        """ move to index and print terminal line at index
        """
        if sys.stderr.isatty() or force:
            move_char = self.get_move_char(index)
            print(f'{move_char}{CLEAR_EOL}', end='', file=sys.stderr)
            print(self.terminal[index], file=sys.stderr)
            sys.stderr.flush()
            self.current += 1

    def reset(self, index):
        """ reset termnal index
        """
        logger.debug(f'resetting terminal at index {index}')
        self.terminal[index].reset()

    def get_move_char(self, index):
        """ return char to move to index
        """
        move_char = ''
        if index < self.current:
            move_char = self.move_up(index)
        elif index > self.current:
            move_char = self.move_down(index)
        return move_char

    def move_down(self, index):
        """ return char to move down to index and update current
        """
        diff = index - self.current
        self.current += diff
        return Cursor.DOWN(diff)

    def move_up(self, index):
        """ return char to move up to index and update current
        """
        diff = self.current - index
        self.current -= diff
        return Cursor.UP(diff)

    def write_lines(self, add_duration=False, force=False):
        """ write lines to terminal
        """
        logger.debug('writing terminal')
        for index, _ in enumerate(self.terminal):
            if add_duration:
                self.terminal[index].duration = self.durations.get(str(index))
            self.write(index, force=force)

    def show_cursor(self):
        """ show cursor
        """
        if sys.stderr.isatty():
            print(SHOW_CURSOR, end='', file=sys.stderr)

    def hide_cursor(self):
        """ hide cursor
        """
        if sys.stderr.isatty():
            print(HIDE_CURSOR, end='', file=sys.stderr)
