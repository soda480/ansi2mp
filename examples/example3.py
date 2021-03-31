#   -*- coding: utf-8 -*-
from time import sleep
from random import randint
from essential_generators import DocumentGenerator
from mp4ansi import Terminal

print('Generating random sentences...')
docgen = DocumentGenerator()
sentence = docgen.sentence()
terminal = Terminal(25)
terminal.write()
count = 0
while True:
    offset = randint(0, 24)
    terminal.write_line(offset, sentence)
    sleep(.01)
    count += 1
    if count > 1000:
        break
    sentence = docgen.sentence()

terminal.write()
