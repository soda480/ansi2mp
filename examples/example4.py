#   -*- coding: utf-8 -*-  
import sys
import logging
from time import sleep

from mp4ansi import MP4ansi
# from mp4ansi import MPcontroller

logger = logging.getLogger(__name__)


def is_prime(num):
    if num == 1:
        return False
    for i in range(2, num):
        if (num % i) == 0:
            return False
            break
    else:
        return True


def check_primes(data, shared_data):
    primes = []
    range_split = data['range'].split('-')
    lower = int(range_split[0])
    upper = int(range_split[1]) + 1
    logger.info(f"finding prime numbers in range {data['range']}")
    logger.debug(f'checking total of {upper - lower} numbers')
    for number in range(lower, upper):
        logger.debug(f'checking {str(number).zfill(6)}/{str(range_split[1]).zfill(6)}')
        if is_prime(number):
            logger.info(f'{number} is prime')
            primes.append(number)
    return primes

def configure_logging():
    """ configure logging
    """
    rootLogger = logging.getLogger()
    # must be set to this level so handlers can filter from this level
    rootLogger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('example2.log')
    file_formatter = logging.Formatter("%(asctime)s %(processName)s [%(funcName)s] %(levelname)s %(message)s")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    rootLogger.addHandler(file_handler)


def main():
    # configure_logging()
    process_data = [
        {'range': '00001-10000'},
        {'range': '10001-20000'},
        {'range': '20001-30000'},
        {'range': '30001-40000'},
        {'range': '40001-50000'},
        {'range': '50001-60000'},
        {'range': '60001-70000'},
        {'range': '70001-80000'},
        {'range': '80001-90000'}] # ,
        # {'range': '90001-100000'}]
    config = {
        'id_regex': r'^INFO: finding prime numbers in range (?P<value>.*)$',
        'progress_bar': {
            # 'total': r'^checking total of (?P<value>\d+) numbers$',
            'total': 10000,
            'count_regex': r'^checking (?P<value>\d+)/\d+$',
            'max_total': 90000
        }
    }

    # mp4ansi = MPcontroller(function=check_primes, process_data=process_data)
    mp4ansi = MP4ansi(function=check_primes, process_data=process_data, config=config)
    print('Computing prime numbers...')
    results = mp4ansi.execute()

    total_primes = 0
    for result in results:
        total_primes += len(result)
    print(f'Total number of primes is: {total_primes}')


if __name__ == '__main__':

    main()
