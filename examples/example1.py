#   -*- coding: utf-8 -*-  
import sys
import uuid
import logging
from time import sleep
from random import randint
from mp4ansi import MP4ansi

logger = logging.getLogger(__name__)


def configure_logging():
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('example1.log')
    file_formatter = logging.Formatter("%(asctime)s %(processName)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    rootLogger.addHandler(file_handler)


def get_process_data(count):
    process_data = []
    for _ in range(count):
        process_data.append({
            'uuid': str(uuid.uuid4()).split('-')[0]
            })
    return process_data


def do_something(*args):
    uuid = args[0]['uuid']
    logger.debug(f'processor id {uuid}')
    total = randint(1000, 9000)
    logger.debug(f'processing total of {total}')
    for index in range(total):
        logger.debug(f'processed {index}')
        sleep(.001)
    return total


def get_total_processed(process_data):
    total = 0
    for process in process_data:
        total += process['result']
    return total


def main(count):
    configure_logging()
    process_data = get_process_data(count)
    config = {
        'id_regex': r'^processor id (?P<value>.*)$',
        'progress_bar': {
            'total': r'^processing total of (?P<value>\d+)$',
            'count_regex': r'^processed (?P<value>\d+)$'
        }
    }

    print('Processing...')
    mp4ansi = MP4ansi(function=do_something, process_data=process_data, config=config)
    mp4ansi.execute()
    # print(mp4ansi.terminal.move_up(0), end='')
    # mp4ansi = MP4ansi(function=do_something, process_data=process_data, config=config)
    # mp4ansi.execute()
    print(f'Total processed: {get_total_processed(process_data)}')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    else:
        count = 10
    main(count)
