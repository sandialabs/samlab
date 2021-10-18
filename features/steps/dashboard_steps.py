# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import os

from behave import *

import samlab.dashboard


@given(u'a running dashboard server')
def step_impl(context):
    def cleanup(dashboard):
        dashboard.stop()

    context.dashboard = samlab.dashboard.Server(config=False, coverage=True, quiet=True)
    context.add_cleanup(cleanup, context.dashboard)
    context.dashboard.ready()
