# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

from behave import *

import nose.tools
import numpy

import samlab.stream


@given(u'a random array input with shape {}')
def step_impl(context, shape):
    shape = eval(shape)
    context.input = numpy.random.uniform(size=shape)


@given(u'a single value stream generator')
def step_impl(context):
    context.stream_generator = samlab.stream.constant(None, context.input, None, None)


@given(u'an array window generator with shape {} and stride {}')
def step_impl(context, shape, stride):
    shape = eval(shape)
    stride = eval(stride)
    context.stream_generator = samlab.stream.array_window(context.stream_generator, shape=shape, stride=stride)


@when(u'the stream generator is exhausted')
def step_impl(context):
    context.stream_datums = list(context.stream_generator)


@then(u'there will be {} stream datums')
def step_impl(context, count):
    count = eval(count)
    nose.tools.assert_equal(len(context.stream_datums), count)


@then(u'each stream datum input will be an array')
def step_impl(context):
    for observation, input, output, weight in context.stream_datums:
        nose.tools.assert_is_instance(input, numpy.ndarray)


@then(u'each stream datum input array will have shape {}')
def step_impl(context, shape):
    shape = eval(shape)
    for observation, input, output, weight in context.stream_datums:
        nose.tools.assert_equal(input.shape, shape)


