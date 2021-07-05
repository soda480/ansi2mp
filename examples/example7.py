#   -*- coding: utf-8 -*-
from mp4ansi import MP4ansi
import names, random, logging
logger = logging.getLogger(__name__)

def do_work(*args):
    total_names = 0
    while True:
        total_names += 1
        last_name = names.get_last_name()
        logger.debug(f'processor is {last_name}|{str(total_names).zfill(2)}')
        total = random.randint(50, 125)
        logger.debug(f'processing total of {total}')
        for _ in range(total):
            logger.debug(f'processed {names.get_full_name()}')
        logger.debug('RESET')
    return total

process_data = [{} for item in range(8)]
config = {
    'id_regex': r'^processor is (?P<value>.*)$',
    'id_justify': True,
    'id_width': 10,
    'progress_bar': {
        'total': r'^processing total of (?P<value>\d+)$',
        'count_regex': r'^processed (?P<value>.*)$',
        'progress_message': 'Finished processing names'
    }
}
print('Procesing names...')
MP4ansi(function=do_work, process_data=process_data, config=config).execute()
print(f"Total names processed {sum([item['result'] for item in process_data])}")
