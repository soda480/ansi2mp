#   -*- coding: utf-8 -*-
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
