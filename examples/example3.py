#   -*- coding: utf-8 -*-
import sys
from time import sleep
from random import randint
from essential_generators import DocumentGenerator
from mp4ansi import Terminal


def main(count):
    print('generating random sentences...')
    docgen = DocumentGenerator()
    terminal = Terminal(count)
    terminal.write()
    terminal.cursor(hide=True)
    for _ in range(1000):
        offset = randint(0, count - 1)
        terminal.write_line(offset, docgen.sentence())
        sleep(.01)
    terminal.write()
    terminal.cursor(hide=False)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    else:
        count = 25
    main(count)
