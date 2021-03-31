#   -*- coding: utf-8 -*-
import re
import logging

from .terminal import Terminal
from mpcurses import MPcontroller
from queue import Empty
from time import sleep

logger = logging.getLogger(__name__)


class MP4ansi(MPcontroller):
    """ a subclass of mpcurses.MPcontroller providing multi-processing (MP) capabilities for a simple ANSI terminal
        setup simple ANSI terminal for all processes to be executed
        write log messages from executing functions to respective lines on ANSI terminal
        add ability to represent execution using progress bar
    """
    def __init__(self, *args, **kwargs):
        logger.debug('executing MP4ansi constructor')
        config = kwargs.pop('config', None)
        super(MP4ansi, self).__init__(*args, **kwargs)
        self.terminal = Terminal(len(self.process_data), config=config)

    def get_message(self):
        """ return message from top of message queue
            override parent class method
        """
        message = super(MP4ansi, self).get_message()
        if not message['offset']:
            # if parent get_message returned no offset then parse it from the message
            match = re.match(r'^#(?P<offset>\d+)-(?P<message>.*)$', message['message'])
            if match:
                return {
                    'offset': match.group('offset'),
                    'control': None,
                    'message': match.group('message')
                }
        return message

    def process_non_control_message(self, offset, message):
        """ process non-control message
            override parent class method
        """
        self.terminal.write_line(int(offset), message)

    def execute_run(self):
        """ write terminal and hide cursor then execute run
            override parent class method
        """
        self.terminal.cursor(hide=True)
        self.terminal.write(ignore_progress=True)
        super(MP4ansi, self).execute_run()

    def final(self):
        """ move down to last offset and enable cursor
            override parent class method
        """
        # move_down = self.terminal.move_down(self.terminal.lines - 1)
        # print(move_down)
        self.terminal.write(ignore_progress=True)
        self.terminal.cursor(hide=False)

    def update_result(self):
        """ update process data with result
        """
        sleep(1)
        logger.debug(f'the result queue size is: {self.result_queue.qsize()}')
        super(MP4ansi, self).update_result()
