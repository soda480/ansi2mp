#   -*- coding: utf-8 -*-
import re
import sys
import math
import logging
from colorama import init as colorama_init
from colorama import Style
from colorama import Fore
from colorama import Back
from colorama import Cursor

logger = logging.getLogger(__name__)

MAX_LINES = 50
MAX_CHARS = 120
HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'
CLEAR_EOL = '\033[K'
PROGRESS_TICKER = '='
PROGRESS_BAR_WIDTH = 50


class Terminal():
    """ simple ANSI terminal
        represented internally as a list of dictionaries
        ability to move up or down and print text at different offsets
    """
    def __init__(self, lines, config=None, create=True):
        """ class constructor
        """
        logger.debug('executing Terminal constructor')
        self.validate_lines(lines)
        self.lines = lines
        self.zfill = len(str(lines))

        if not config:
            config = {}
        self.validate_config(config)
        self.config = config

        colorama_init()

        self.current = None
        if create:
            self.terminal = self.create()

    def validate_lines(self, lines):
        """ validate lines
        """
        if lines < 0 or lines > MAX_LINES:
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

    def create(self):
        """ return list of dictionaries representing terminal for config
        """
        logger.debug('creating terminal')
        terminal = []
        for index in range(self.lines):
            item = {
                'id': str(index).zfill(self.zfill),
                'text': ''
            }
            if self.config.get('progress_bar'):
                item['count'] = 0
                item['modulus_count'] = 0
                item['total'] = None
            terminal.append(item)
        return terminal

    def assign_id(self, offset, text):
        """ assign id for offset using id_regex from config
        """
        regex_id = self.config['id_regex']
        match_id = re.match(regex_id, text)
        if match_id:
            self.terminal[offset]['id'] = match_id.group('value')
            self.terminal[offset]['id_matched'] = True

    def assign_total(self, offset, text):
        """ assign total for offset using total from config
        """
        if isinstance(self.config['progress_bar']['total'], str):
            regex_total = self.config['progress_bar']['total']
            match_total = re.match(regex_total, text)
            if match_total:
                self.terminal[offset]['total'] = int(match_total.group('value'))
        else:
            self.terminal[offset]['total'] = self.config['progress_bar']['total']

        if self.terminal[offset]['total']:
            self.terminal[offset]['modulus'] = round(self.terminal[offset]['total'] / PROGRESS_BAR_WIDTH)
            # in case total less than progress bar width then lets set total to 1 to avoid divide by zero
            if self.terminal[offset]['modulus'] == 0:
                self.terminal[offset]['modulus'] = 1

    def get_progress_text(self, offset, text):
        """ process progress bar
        """
        if not self.terminal[offset]['total']:
            self.assign_total(offset, text)

        regex_count = self.config['progress_bar']['count_regex']
        match_count = re.match(regex_count, text)
        if match_count:
            self.terminal[offset]['count'] += 1

            modulus = self.terminal[offset]['count'] % self.terminal[offset]['modulus']
            if modulus == 0:
                self.terminal[offset]['modulus_count'] += 1
                progress = PROGRESS_TICKER * self.terminal[offset]['modulus_count']

                padding = ' ' * (PROGRESS_BAR_WIDTH - self.terminal[offset]['modulus_count'])
                percentage = round((self.terminal[offset]['count'] / self.terminal[offset]['total']) * 100)
                rjust = (len(str(self.terminal[offset]['total'])) * 2) + 4
                indicator = f"{self.terminal[offset]['count']}/{self.terminal[offset]['total']}".rjust(rjust)
                return f"Processing |{Style.DIM}{progress}>{padding}| {Style.BRIGHT}{percentage}%{Style.RESET_ALL} {indicator}"

            else:
                if self.terminal[offset]['count'] == self.terminal[offset]['total']:
                    progress = PROGRESS_TICKER * PROGRESS_BAR_WIDTH
                    percentage = round((self.terminal[offset]['count'] / self.terminal[offset]['total']) * 100)
                    rjust = (len(str(self.terminal[offset]['total'])) * 2) + 4
                    indicator = f"{self.terminal[offset]['count']}/{self.terminal[offset]['total']}".rjust(rjust)
                    return f"Processing |{progress}>| {Style.BRIGHT}{percentage}%{Style.RESET_ALL} {indicator}"

        if self.terminal[offset]['count'] == self.terminal[offset]['total']:
            return 'Processing complete'

    def write_line(self, offset, text, ignore_progress=False):
        """ write text at offset
        """
        if self.config.get('id_regex') and not self.terminal[offset].get('id_matched', False):
            self.assign_id(offset, text)

        if not ignore_progress and self.config.get('progress_bar'):
            text_to_display = self.get_progress_text(offset, text)
            if not text_to_display:
                return
        else:
            text_to_display = self.sanitize(text)

        id_to_display = f"{Style.BRIGHT + Fore.YELLOW + Back.BLACK}{self.terminal[offset]['id']}{Style.RESET_ALL}"

        line = f"[{id_to_display}]: {text_to_display}"
        self.terminal[offset]['text'] = text_to_display
        # logger.info(f'line: {line}')

        move_char = self.move(offset)
        print(f'{move_char}{CLEAR_EOL}', end='')
        print(line)
        self.current += 1

    def move(self, offset):
        """ return move to offset
        """
        char = ''
        if offset < self.current:
            char = self.move_up(offset)
        elif offset > self.current:
            char = self.move_down(offset)
        return char

    def move_down(self, offset):
        """ return down to offset
        """
        diff = offset - self.current
        self.current += diff
        return Cursor.DOWN(diff)

    def move_up(self, offset):
        """ return up to offset
        """
        diff = self.current - offset
        self.current -= diff
        return Cursor.UP(diff)

    def write(self, ignore_progress=False):
        """ write lines to screen
        """
        logger.debug('writing terminal')
        if self.current is None:
            self.current = 0
        for offset, item in enumerate(self.terminal):
            self.write_line(offset, item['text'], ignore_progress=ignore_progress)

    def sanitize(self, text):
        """ sanitize text
        """
        if text:
            text = text.splitlines()[0]
            if len(text) > MAX_CHARS:
                return f'{text[0:MAX_CHARS - 3]}...'
        return text

    def cursor(self, hide=True):
        """ show or hide cursor
        """
        if hide:
            print(HIDE_CURSOR, end='')
        else:
            print(SHOW_CURSOR, end='')
