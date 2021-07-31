#   -*- coding: utf-8 -*-
import sys, random, time
from mp4ansi import ProgressBar

with ProgressBar() as pb:
    pb.alias = 'Super 80s'
    pb.total = random.randint(50, 100)
    for _ in range(pb.total):
        pb.count += 1
        # simulate work
        time.sleep(.09)
# print(pb, file=sys.stdout)