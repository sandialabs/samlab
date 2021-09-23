# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

from behave import *
import nose.tools
import numpy.testing


@given(u'a reservoir object with size {} and seed {}')
def step_impl(context, size, seed):
    size = eval(size)
    seed = eval(seed)
    context.reservoir = samlab.web.app.handlers.timeseries.Reservoir(size=size, seed=seed)


@when(u'the sequence {} is added to the reservoir')
def step_impl(context, sequence):
    for item in eval(sequence):
        context.reservoir.append(item)


@then(u'the reservoir length should match {}')
def step_impl(context, length):
    length = eval(length)
    nose.tools.assert_equal(len(context.reservoir), length)


@then(u'the reservoir should contain {}')
def step_impl(context, result):
    result = eval(result)
    numpy.testing.assert_array_equal(numpy.array(context.reservoir), result)


