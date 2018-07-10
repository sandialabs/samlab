# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

from behave import *

import logging

import nose.tools


@given(u'the iris dataset')
def step_impl(context):
    import samlab.example.iris
    samlab.example.iris.create(context.database, context.fs)

