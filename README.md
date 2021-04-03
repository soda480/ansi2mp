[![GitHub Workflow Status](https://github.com/soda480/mp4ansi/workflows/build/badge.svg)](https://github.com/soda480/mp4ansi/actions)
[![Code Coverage](https://codecov.io/gh/soda480/mp4ansi/branch/master/graph/badge.svg)](https://codecov.io/gh/soda480/mp4ansi)
[![Code Grade](https://www.code-inspector.com/project/20694/status/svg)](https://frontend.code-inspector.com/project/20694/dashboard)
[![PyPI version](https://badge.fury.io/py/mp4ansi.svg)](https://badge.fury.io/py/mp4ansi)

# mp4ansi #

A simple ANSI-based terminal emulator that provides multi-processing capabilities. MP4ansi will scale execution of a specified function across multiple background processes, where each process is mapped to specific line on the terminal. As the function executes its log messages will automatically be written to the respective line on the terminal. The number of processes along with the arguments to provide each process is specified as a list of dictionaries. The number of elements in the list will dictate the total number of processes to execute (as well as the number of lines in the terminal). The result of each function is written to the respective dictionary element and can be interogated upon completion.

MPansi also supports representing the function execution as a progress bar, you will need to provide an optional config argument containing a dictionary for how to query for the total and count (via regular expressions), see the [examples](https://github.com/soda480/mp4ansi/tree/master/examples) for more detail. 

### Installation ###
```bash
pip install mp4ansi
```

### Examples ###

To run the samples below you need to install the namegenerator module `pip install namegenerator`


A simple mp4ansi example:
```python
from mp4ansi import MP4ansi
import uuid, random, namegenerator, time, logging
logger = logging.getLogger(__name__)

def do_something(*args):
    myid = str(uuid.uuid4()).split('-')[-1]
    logger.debug(f'myid is {myid}')
    for _ in range(random.randint(200, 400)):
        logger.debug(f'{namegenerator.gen()} and {namegenerator.gen()}')
        time.sleep(.01)

process_data = [{} for item in range(24)]
config = {'id_regex': r'^myid is (?P<value>.*)$'}
MP4ansi(function=do_something, process_data=process_data, config=config).execute()
```

Executing the code above results in the following:
![example](https://raw.githubusercontent.com/soda480/mp4ansi/master/docs/images/inline-example.gif)

Serveral [examples](https://github.com/soda480/mp4ansi/tree/master/examples) are included to help introduce the mp4ansi package. Note the functions contained in all the examples are Python functions that have no context about multiprocessing or terminal; they simply perform a function on a given dataset. MP4ansi is a subclass of the `mpcurses` mpcontroller, it takes care of setting up the multiprocessing, configuring the curses screen and maintaining the thread-safe queues that are required for inter-process communication.  Checkout [mpcurses](https://pypi.org/project/mpcurses/) for more information.


#### [example1](https://github.com/soda480/mp4ansi/blob/master/examples/example1.py)
Execute a function that processes a list of random numbers. Execution is demonstrated as a progress bar, each function works on a different set of numbers thus the total is provided as a regular expression for MP4ansi to determine upon execution.
![example1](https://raw.githubusercontent.com/soda480/mp4ansi/master/docs/images/example1.gif)

#### [example2](https://github.com/soda480/mp4ansi/blob/master/examples/example2.py)
Execute a function that calculates prime numbers for a set range of integers. Execution is scaled across 9 different processes where each process computes the primes on a different set of numbers. For example, the first process computes primes for the set 1-10K, second process 10K-20K, third process 20K-30K, etc. The total number of prime numbers is printed.
![example2](https://raw.githubusercontent.com/soda480/mp4ansi/master/docs/images/example2.gif)

#### [example3](https://github.com/soda480/mp4ansi/blob/master/examples/example3.py)
This example demonstrates the `Terminal` class defined within mp4ansi, this script writes random a random sentence to each line of the terminal randomly.
![example3](https://raw.githubusercontent.com/soda480/mp4ansi/master/docs/images/example3.gif)

#### Running the examples ####

Build the Docker image and run the Docker container using the instructions described in the [Development](#development) section. Run the example scripts within the container:

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
