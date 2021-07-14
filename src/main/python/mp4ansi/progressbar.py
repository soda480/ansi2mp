import re
import logging

from colorama import init as colorama_init
from colorama import Style
from colorama import Fore
from colorama import Back
from colorama import Cursor

logger = logging.getLogger(__name__)

TICKER = chr(9632)  # ■
PROGRESS_WIDTH = 50
ALIAS_WIDTH = 100
FILL = 2


class ProgressBar(object):
    """ Progress Bar implementation
    """

    def __init__(self, index, total=None, fill=None, regex=None, message=None):
        """ class constructor
        """
        colorama_init()

        if not fill:
            fill = FILL
        self.fill = fill

        if not regex:
            regex = {}
        self.regex = regex

        self.message = message
        self.complete = False

        self.index = index
        self.alias = ''
        self.total = total
        self._modulus_count = 0
        self._reset = 0
        # avoid __setattr__ for setting count value
        self.__dict__['count'] = 0
        logger.debug('initializtion complete')

    def __str__(self):
        """ return string interpretation of class instance
        """
        bright_yellow = Style.BRIGHT + Fore.YELLOW + Back.BLACK
        _index = f"{bright_yellow}{str(self.index).zfill(2)}{Style.RESET_ALL}"
        _alias = f"{bright_yellow}{self.alias}{Style.RESET_ALL}"
        _progress = self._get_progress()
        _reset = ''
        if self._reset:
            _reset = f'{bright_yellow}[{str(self._reset).zfill(2)}] '
        return f"{_index}: {_progress} {_reset}{_alias}"

    def __setattr__(self, name, value):
        """ set class instance attributes
        """
        if name == 'count' and self.total is None:
            return
        super(ProgressBar, self).__setattr__(name, value)
        if name == 'count':
            self._modulus_count = round(round(self.count / self.total, 2) * PROGRESS_WIDTH)
        # restrict total - can only be set once if previous value is null
        # implement reset
        # restrict index
        # restrict _modulus_count

    def reset(self):
        """ reset progress bar
        """
        logger.debug('resetting progress bar')
        self.alias = ''
        self.total = None
        self.complete = False
        self._modulus_count = 0
        # avoid __setattr__ for setting count value
        self.__dict__['count'] = 0
        self._reset += 1

    def match(self, text):
        """ call match functions and return on first success
        """
        functions = [self._match_total, self._match_alias, self._match_count]
        for function in functions:
            if function(text):
                break

    def _match_total(self, text):
        """ set total if text matches total regex
        """
        match = None
        if self.total is None:
            regex = self.regex.get('total')
            if regex:
                match = re.match(regex, text)
                if match:
                    self.total = int(match.group('value'))
        return match

    def _match_alias(self, text):
        """ set alias if text matches alias regex
        """
        match = None
        regex = self.regex.get('alias')
        if regex:
            match = re.match(regex, text)
            if match:
                value = match.group('value')
                if len(value) > ALIAS_WIDTH:
                    value = f'{value[0:ALIAS_WIDTH - 3]}...'
                self.alias = value
        return match

    def _match_count(self, text):
        """ increment count if text matches count regex
        """
        match = None
        regex = self.regex.get('count')
        if regex:
            match = re.match(regex, text)
            if match:
                self.count += 1
        return match

    def _get_progress(self):
        """ return progress text
        """
        if self.complete:
            progress = 'Processing complete'
            if self.message:
                progress = self.message
        else:
            if self.total:
                _percentage = str(round((self.count / self.total) * 100))
                indicator = f'{str(self.count).zfill(self.fill)}/{str(self.total).zfill(self.fill)}'
                if self.count == self.total:
                    self.complete = True
            else:
                _percentage = '0'
                # 2 sets of digits and 1 for the divider
                indicator = '#' * self.fill + '/' + '#' * self.fill

            bar = TICKER * self._modulus_count
            padding = ' ' * (PROGRESS_WIDTH - self._modulus_count)
            percentage = _percentage.rjust(3)
            progress = f"Processing |{bar}{padding}| {Style.BRIGHT}{percentage}%{Style.RESET_ALL} {indicator}"
        return progress
