[![GitHub Workflow Status](https://github.com/soda480/mp4ansi/workflows/build/badge.svg)](https://github.com/soda480/mp4ansi/actions)
[![Code Coverage](https://codecov.io/gh/soda480/mp4ansi/branch/main/graph/badge.svg?token=6NTX6LSP7Q)](https://codecov.io/gh/soda480/mp4ansi)
[![Code Grade](https://www.code-inspector.com/project/20694/status/svg)](https://frontend.code-inspector.com/project/20694/dashboard)
[![PyPI version](https://badge.fury.io/py/mp4ansi.svg)](https://badge.fury.io/py/mp4ansi)

# mp4ansi #

A simple ANSI-based terminal emulator that provides multi-processing capabilities. MP4ansi will scale execution of a specified function across multiple background processes, where each process is mapped to specific line on the terminal. As the function executes its log messages will automatically be written to the respective line on the terminal. The number of processes along with the arguments to provide each process is specified as a list of dictionaries. The number of elements in the list will dictate the total number of processes to execute (as well as the number of lines in the terminal). The result of each function is written to the respective dictionary element and can be interogated upon completion.

MPansi also supports representing the function execution as a progress bar, you will need to provide an optional config argument containing a dictionary for how to query for the total and count (via regular expressions), see the [examples](https://github.com/soda480/mp4ansi/tree/master/examples) for more detail.

MP4ansi is a subclass of `mpmq`, see [the mpmq PyPi page](https://pypi.org/project/mpmq/) for more information.

### Installation ###
```bash
pip install mp4ansi
```

### Examples ###

To run the samples below you need to install the namegenerator module `pip install namegenerator`.

A simple mp4ansi example:
```python
from mp4ansi import MP4ansi
import uuid, random, namegenerator, time, logging
logger = logging.getLogger(__name__)

def do_work(*args):
    total = random.randint(200, 600)
    logger.debug(f'processing total of {total}')
    for _ in range(total):
        logger.debug(f'processed {namegenerator.gen()}')
        time.sleep(.01)
    return total

process_data = [{} for item in range(8)]
print('Procesing items...')
MP4ansi(function=do_work, process_data=process_data).execute()
print(f"Total items processed {sum([item['result'] for item in process_data])}")
```

Executing the code above results in the following:
![example](https://raw.githubusercontent.com/soda480/mp4ansi/master/docs/images/inline-example1.gif)

**Note** the function being executed `do_work` has no context about multiprocessing or the terminal; it simply perform a function on a given dataset. MP4ansi takes care of setting up the multiprocessing, setting up the terminal, and maintaining the thread-safe queues that are required for inter-process communication.

Let's update the example to add an identifer for each process and to show execution as a progress bar. To do this we need to provide additonal configuration via the optional `config` parameter. Configuration is supplied as a dictionary; `id_regex` instructs how to query the identifer from the log messages, `id_justify` will right justify the identifer to make things look nice. For the progress bar, we need to specify `total` and `count_regex` to instruct how to query the total and when to count when an item is processed respectively. The value for these settings are specified as regular expressions and will match the function log messages, thus we need to ensure our function has log statements for these.

```python
from mp4ansi import MP4ansi
import uuid, random, namegenerator, time, logging
logger = logging.getLogger(__name__)

def do_work(*args):
    pid = str(uuid.uuid4())
    logger.debug(f'processor id {pid[0:random.randint(8, 30)]}')
    total = random.randint(200, 600)
    logger.debug(f'processing total of {total}')
    for _ in range(total):
        logger.debug(f'processed {namegenerator.gen()}')
        time.sleep(.01)
    return total

process_data = [{} for item in range(8)]
config = {
    'id_regex': r'^processor id (?P<value>.*)$',
    'id_justify': True,
    'progress_bar': {
        'total': r'^processing total of (?P<value>\d+)$',
        'count_regex': r'^processed (?P<value>.*)$'}}
print('Procesing items...')
MP4ansi(function=do_work, process_data=process_data, config=config).execute()
print(f"Total items processed {sum([item['result'] for item in process_data])}")
```

Executing the code above results in the following:
![example](https://raw.githubusercontent.com/soda480/mp4ansi/master/docs/images/inline-example2.gif)

More [examples](https://github.com/soda480/mp4ansi/tree/master/examples) are included to demonstrate the mp4ansi package. To run the examples, build the Docker image and run the Docker container using the instructions described in the [Development](#development) section.

To run the example scripts within the container:

```bash
python examples/example#.py
```

### Development ###

Clone the repository and ensure the latest version of Docker is installed on your development server.


Build the Docker image:
```sh
docker image build \
-t \
mp4ansi:latest .
```

Run the Docker container:
```sh
docker container run \
--rm \
-it \
-v $PWD:/mp4ansi \
mp4ansi:latest \
/bin/sh
```

Execute the build:
```sh
pyb -X
```
