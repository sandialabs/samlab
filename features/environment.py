# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os

import samlab.database

logging.basicConfig(level=logging.INFO)


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
db_dir = os.path.join(root_dir, "features", "db")


def before_all(context):
    context.database_server = samlab.database.Server(dbpath=db_dir, reset=True, quiet=True)


def after_all(context):
    context.database_server.stop()
