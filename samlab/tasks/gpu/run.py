# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import os

import samlab.tasks.gpu

key = "SAMLAB_QUEUE_NAME"

if key in os.environ:
    queue = samlab.tasks.gpu.Queue(os.environ[key]).queue

