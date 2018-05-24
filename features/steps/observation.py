# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

from behave import *

import nose.tools
import numpy
import samlab.observation
import samlab.serialize


@given(u'a sample observation generator')
def step_impl(context):
    def observation_generator():
        for i in range(3):
            yield {
                "content": {
                    "array": samlab.serialize.array(numpy.arange(5)),
                    "string": samlab.serialize.string("Hello, World!"),
                    },
                "tags": ["a", "b"],
                "attributes": {"c": "d"},
                }
    context.observation_generator = observation_generator()


@when(u'the generator is used for ingestion')
def step_impl(context):
    samlab.observation.ingest(context.observation_generator, context.database)

