#   -*- coding: utf-8 -*-
from mp4ansi import MP4ansi
import random, names, logging
logger = logging.getLogger(__name__)

def do_work(*args):
    total = random.randint(50, 100)
    logger.debug(f'processing total of {total}')
    for _ in range(total):
        logger.debug(f'processed {names.get_full_name()}')
    return total

def main():
    process_data = [{} for item in range(8)]
    print('Procesing names...')
    results = MP4ansi(function=do_work, process_data=process_data).execute()
    print(f"Total names processed {sum(result for result in results)}")

if __name__ == '__main__':
    main()
