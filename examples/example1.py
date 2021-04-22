from mp4ansi import MP4ansi
import uuid, random, namegenerator, time, logging
logger = logging.getLogger(__name__)

def do_work(*args):
    total = random.randint(400, 600)
    logger.debug(f'processing total of {total}')
    for _ in range(total):
        logger.debug(f'processed {namegenerator.gen()}')
        time.sleep(.01)
    return total

process_data = [{} for item in range(8)]
print('Procesing items...')
MP4ansi(function=do_work, process_data=process_data).execute()
print(f"Total items processed {sum([item['result'] for item in process_data])}")
