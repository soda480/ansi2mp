#   -*- coding: utf-8 -*-
from mp4ansi import MP4ansi
import names, random, logging
logger = logging.getLogger(__name__)

TOTAL_ITEMS = 325
TOTAL_NAMES = 5

def do_work(*args):
    total_names = 0
    while True:
        last_name = names.get_last_name()
        logger.debug(f'processor is {last_name}')

        total = random.randint(50, TOTAL_ITEMS)
        logger.debug(f'processing total of {total}')
        for _ in range(total):
            logger.debug(f'processed {names.get_full_name()}')

        total_names += 1  
        if total_names == TOTAL_NAMES:
            # reset alias/id
            logger.debug(f'processor is  ')
            break

        logger.debug('RESET')

    return total

def main():
    process_data = [{} for item in range(8)]
    config = {
        'id_regex': r'^processor is (?P<value>.*)$',
        'progress_bar': {
            'total': r'^processing total of (?P<value>\d+)$',
            'count_regex': r'^processed (?P<value>.*)$',
            'progress_message': 'Finished processing names',
            'max_total': TOTAL_ITEMS,
            'max_completed': TOTAL_NAMES,
            'wtf': True
        }
    }
    print('Procesing names...')
    results = MP4ansi(function=do_work, process_data=process_data, config=config).execute()
    print(f"Total names processed {sum(result for result in results)}")

if __name__ == '__main__':
    main()