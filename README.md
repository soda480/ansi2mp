# mp4ansi #
[![GitHub Workflow Status](https://github.com/soda480/mp4ansi/workflows/build/badge.svg)](https://github.com/soda480/mp4ansi/actions)
[![Code Coverage](https://codecov.io/gh/soda480/mp4ansi/branch/main/graph/badge.svg?token=6NTX6LSP7Q)](https://codecov.io/gh/soda480/mp4ansi)
[![Code Grade](https://www.code-inspector.com/project/20694/status/svg)](https://frontend.code-inspector.com/project/20694/dashboard)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-green)](https://pypi.org/project/bandit/)
[![PyPI version](https://badge.fury.io/py/mp4ansi.svg)](https://badge.fury.io/py/mp4ansi)
[![python](https://img.shields.io/badge/python-3.6-teal)](https://www.python.org/downloads/)


A simple ANSI-based terminal that provides various capabilities for showing off and/or scaling out your programs execution. MP4ansi is an abstraction of multiprocessing that leverages both the Terminal and ProgressBar. See the [examples](https://github.com/soda480/mp4ansi/tree/master/examples) for more detail.

## Installation ##
```bash
pip install mp4ansi
```

## Examples ##

Various [examples](https://github.com/soda480/mp4ansi/tree/master/examples) are included to demonstrate the mp4ansi package. To run the examples, build the Docker image and run the Docker container using the instructions described in the [Development](#development) section.

### `MP4ansi`

MP4ansi will scale execution of a specified function across multiple background processes, where each process is mapped to specific line on the terminal. As the function executes its log messages will automatically be written to the respective line on the terminal. The number of processes along with the arguments to provide each process is specified as a list of dictionaries. The number of elements in the list will dictate the total number of processes to execute (as well as the number of lines in the terminal). The result of each function is written to the respective dictionary element and can be interogated upon completion. 

MP4ansi is a subclass of `mpmq`, see the [mpmq](https://pypi.org/project/mpmq/) for more information.

Here is a simple example:

```python
from mp4ansi import MP4ansi
import random, names, logging
logger = logging.getLogger(__name__)

def do_work(*args):
    total = random.randint(50, 100)
    logger.debug(f'processing total of {total}')
    for _ in range(total):
        logger.debug(f'processed {names.get_full_name()}')
    return total

process_data = [{} for item in range(8)]
print('Procesing names...')
MP4ansi(function=do_work, process_data=process_data).execute()
print(f"Total names processed {sum([item['result'] for item in process_data])}")
```

Executing the code above ([example1](https://github.com/soda480/mp4ansi/tree/master/examples/example1.py)) results in the following:
![example](https://raw.githubusercontent.com/soda480/mp4ansi/master/docs/images/example1.gif)

**Note** the function being executed `do_work` has no context about multiprocessing or the terminal; it simply perform a function on a given dataset. MP4ansi takes care of setting up the multiprocessing, setting up the terminal, and maintaining the thread-safe queues that are required for inter-process communication.

Let's update the example to add a custom identifer for each process and to show execution as a progress bar. To do this we need to provide additonal configuration via the optional `config` parameter. Configuration is supplied as a dictionary; `id_regex` instructs how to query for the identifer from the log messages. For the progress bar, we need to specify `total` and `count_regex` to instruct how to query for the total and for when to count that an item has been processed. The value for these settings are specified as regular expressions and will match the function log messages, thus we need to ensure our function has log statements for these. If each instance of your function executes on a static data range then you can specify total as an `int`, but in this example the data range is dynamic, i.e. each process will execute on varying data ranges.

```python
from mp4ansi import MP4ansi
import names, random, logging
logger = logging.getLogger(__name__)

def do_work(*args):
    logger.debug(f'processor is {names.get_last_name()}')
    total = random.randint(50, 125)
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
        'progress_message': 'Finished processing names'}}
print('Procesing names...')
MP4ansi(function=do_work, process_data=process_data, config=config).execute()
print(f"Total names processed {sum([item['result'] for item in process_data])}")
```

Executing the code above ([example2](https://github.com/soda480/mp4ansi/tree/master/examples/example2.py)) results in the following:
![example](https://raw.githubusercontent.com/soda480/mp4ansi/master/docs/images/example2.gif)

### `Terminal`

The package also exposes a `Terminal` class if you wish to consume the terminal capabilities without executing background processes. Here is an example for how to do that:
```python
from mp4ansi import Terminal
from essential_generators import DocumentGenerator
import time, random

print('generating random sentences...')
count = 15
docgen = DocumentGenerator()
terminal = Terminal(count)
terminal.write_lines()
terminal.hide_cursor()
for _ in range(800):
    index = random.randint(0, count - 1)
    terminal.write_line(index, docgen.sentence())
    time.sleep(.01)
terminal.write_lines(force=True)
terminal.show_cursor()
```

Executing the code above ([example5](https://github.com/soda480/mp4ansi/tree/master/examples/example5.py)) results in the following:
![example](https://raw.githubusercontent.com/soda480/mp4ansi/master/docs/images/example5.gif)

## Development ##

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
