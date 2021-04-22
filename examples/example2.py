from mp4ansi import MP4ansi
import uuid, random, namegenerator, time, logging
logger = logging.getLogger(__name__)

def do_work(*args):
    """ process widgets
    """
    pid = str(uuid.uuid4())
    logger.debug(f'processor id {pid[0:random.randint(8, 30)]}')
    total = random.randint(200, 600)
    logger.debug(f'processing total of {total}')
    for _ in range(total):
        logger.debug(f'processed {namegenerator.gen()}')
        logger.debug('')
        logger.debug('')
        time.sleep(.01)
    return total

process_data = [{} for item in range(8)]
config = {
    'id_regex': r'^processor id (?P<value>.*)$',
    'id_justify': True,
    # 'id_width': 18,
    'progress_bar': {
        'total': r'^processing total of (?P<value>\d+)$',
        'count_regex': r'^processed (?P<value>.*)$',
        # 'progress_message': 'Processing is done!'
    }
}
print('Procesing items...')
MP4ansi(function=do_work, process_data=process_data, config=config).execute()
print(f"Total items processed {sum([item['result'] for item in process_data])}")
