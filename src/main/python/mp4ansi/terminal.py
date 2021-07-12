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

MAX_LINES = 75
MAX_CHARS = 120
HIDE_CURSOR = '\x1b[?25l'
SHOW_CURSOR = '\x1b[?25h'
CLEAR_EOL = '\033[K'
PROGRESS_TICKER = chr(9632)  # ■
PROGRESS_BAR_WIDTH = 50
ID_WIDTH = 100
MAX_DIGITS = 3


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
        zfill = len(str(number_of_lines))
        for index in range(number_of_lines):
            item = {
                'id': '',
                'text': '',
                'index': str(index).zfill(zfill),
            }
            # progress bar requires additional metadata
            if self.config.get('progress_bar'):
                item['count'] = 0
                item['modulus_count'] = 0
                item['total'] = None
                item['text'] = self.determine_progress_text(0, 0, None)
            terminal.append(item)
        return terminal

    def get_id_width(self):
        """ return id width
        """
        id_width = self.config.get('id_width', ID_WIDTH)
        if id_width > ID_WIDTH:
            id_width = ID_WIDTH
        return id_width

    def assign_id(self, index, text):
        """ assign id for index using id_regex from config
        """
        regex_id = self.config['id_regex']
        match_id = re.match(regex_id, text)
        if match_id:
            value = match_id.group('value')
            if len(value) > ID_WIDTH:
                value = f'{value[0:ID_WIDTH - 3]}...'
            self.terminal[index]['id'] = value
            return value

    def assign_total(self, index, text):
        """ assign total for index using total from config
        """
        total_assigned = False
        if isinstance(self.config['progress_bar']['total'], str):
            regex_total = self.config['progress_bar']['total']
            match_total = re.match(regex_total, text)
            if match_total:
                self.terminal[index]['total'] = int(match_total.group('value'))
                total_assigned = True
        else:
            self.terminal[index]['total'] = self.config['progress_bar']['total']

        if self.terminal[index]['total']:
            self.terminal[index]['modulus'] = round(self.terminal[index]['total'] / PROGRESS_BAR_WIDTH)
            # in case total less than progress bar width then lets set modulus to 1 to avoid divide by zero
            if self.terminal[index]['modulus'] == 0:
                self.terminal[index]['modulus'] = 1
        return total_assigned

    def get_identifier(self, index, text):
        """ return tuple identifier and boolean indicating if it was assigned
        """
        assigned = False
        if self.config.get('id_regex'):
            if self.assign_id(index, text) is not None:
                assigned = True
        return self.terminal[index]['id'], assigned

    def get_progress_text(self, index, text):
        """ process progress bar
        """
        progress_text = self.terminal[index]['text']
        total_assigned = False
        if not self.terminal[index]['total']:
            total_assigned = self.assign_total(index, text)
            if total_assigned:
                progress_text = self.determine_progress_text(self.terminal[index]['modulus_count'], self.terminal[index]['count'], self.terminal[index]['total'])
        else:
            if self.terminal[index]['count'] == self.terminal[index]['total']:
                progress_text = self.config.get('progress_bar', {}).get('progress_message', 'Processing complete')
            else:
                regex_count = self.config['progress_bar']['count_regex']
                match_count = re.match(regex_count, text)
                if match_count:
                    self.terminal[index]['count'] += 1
                    self.terminal[index]['modulus_count'] = round(round(self.terminal[index]['count'] / self.terminal[index]['total'], 2) * PROGRESS_BAR_WIDTH)
                    progress_text = self.determine_progress_text(self.terminal[index]['modulus_count'], self.terminal[index]['count'], self.terminal[index]['total'])
        return progress_text

    def get_matched_text(self, text):
        """ return matched text
        """
        text_to_print = None
        text_regex = self.config['text_regex']
        if re.match(text_regex, text):
            text_to_print = self.sanitize(text)
        return text_to_print

    def add_duration(self, index, text, add_duration):
        """ append duration to text if add duration and text is not None
        """
        text_to_print = text
        if add_duration and text_to_print is not None:
            duration = self.durations.get(str(index), '')
            text_to_print += f" - {duration}"
        return text_to_print

    def write_line(self, index, text, add_duration=False, force=False):
        """ write line at index
        """
        identifier, identifer_assigned = self.get_identifier(index, text)
        if self.config.get('progress_bar'):
            text_to_print = self.get_progress_text(index, text)
            if not text_to_print and identifer_assigned:
                # ensure id is written to terminal when it is assigned
                text_to_print = ''
        elif self.config.get('text_regex'):
            text_to_print = self.get_matched_text(text)
        else:
            text_to_print = self.sanitize(text)

        text_to_print = self.add_duration(index, text_to_print, add_duration)

        id_to_print = f"{Style.BRIGHT + Fore.YELLOW + Back.BLACK}{identifier}{Style.RESET_ALL}"
        self.write(index, id_to_print, text_to_print, force=force)

    def write(self, index, id_to_print, text_to_print, force=False):
        """ move to index and write identifier and text
        """
        if sys.stderr.isatty() or force:
            move_char = self.get_move_char(index)
            if text_to_print is None:
                print(move_char, file=sys.stderr)
            else:
                self.terminal[index]['text'] = text_to_print
                print(f'{move_char}{CLEAR_EOL}', end='', file=sys.stderr)
                index_to_print = f"{Style.BRIGHT + Fore.YELLOW + Back.BLACK}{self.terminal[index]['index']}{Style.RESET_ALL}"
                print(f"{index_to_print}: {text_to_print} {id_to_print}", file=sys.stderr)
            sys.stderr.flush()
            self.current += 1

    def reset(self, index):
        """ reset termnal index
        """
        logger.debug(f'resetting terminal at index {index}')
        self.terminal[index]['text'] = ''
        if self.config.get('progress_bar'):
            self.terminal[index]['count'] = 0
            self.terminal[index]['modulus_count'] = 0
            self.terminal[index]['total'] = None

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
        for index, item in enumerate(self.terminal):
            self.write_line(index, item['text'], add_duration=add_duration, force=force)

    def sanitize(self, text):
        """ sanitize text
        """
        if text:
            text = text.splitlines()[0]
            if len(text) > MAX_CHARS:
                text = f'{text[0:MAX_CHARS - 3]}...'
            else:
                text = text.ljust(MAX_CHARS)
        return text

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

    def determine_progress_text(self, modulus_count, count, total):
        """ determine progress bar text
        """
        max_digits = self.config['progress_bar'].get('max_digits', MAX_DIGITS)
        if total:
            percentage = str(round((count / total) * 100))
            indicator = f'{count}/{total}'
        else:
            percentage = '0'
            indicator = '#/#'
        percentage = percentage.rjust(3)
        indicator_padding = max_digits * 2 + 1  # 2 sets of digits and 1 for the divider
        indicator = indicator.ljust(indicator_padding)
        progress = PROGRESS_TICKER * modulus_count
        padding = ' ' * (PROGRESS_BAR_WIDTH - modulus_count)
        progress_text = f"Processing |{progress}{padding}| {Style.BRIGHT}{percentage}%{Style.RESET_ALL} {indicator}"
        return progress_text
