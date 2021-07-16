#   -*- coding: utf-8 -*-
from mp4ansi import MP4ansi
import names, random, logging
logger = logging.getLogger(__name__)

def do_work(*args):
    total_names = 0
    while True:
        if total_names >= 5:
            break

        logger.debug('RESET')

        last_name = names.get_last_name()
        logger.debug(f'processor is {last_name}')
        total_names += 1

        total = random.randint(50, 325)
        logger.debug(f'processing total of {total}')
        for _ in range(total):
            logger.debug(f'processed {names.get_full_name()}')

    return total

process_data = [{} for item in range(8)]
config = {
    'id_regex': r'^processor is (?P<value>.*)$',
    'progress_bar': {
        'total': r'^processing total of (?P<value>\d+)$',
        'count_regex': r'^processed (?P<value>.*)$',
        'progress_message': 'Finished processing names',
        'max_digits': 3
    }
}
print('Procesing names...')
MP4ansi(function=do_work, process_data=process_data, config=config).execute()
print(f"Total names processed {sum([item['result'] for item in process_data])}")
