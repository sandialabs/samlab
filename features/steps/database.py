# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

from behave import *

import datetime

import nose.tools
import samlab.database


@given(u'a database named {}')
def step_impl(context, dbname):
    context.database, context.fs = samlab.database.connect(dbname, context.database_server.uri)


@given(u'a collection named {}')
def step_impl(context, name):
    context.collection = context.database[name]


@then(u'there will be a collection named {}')
def step_impl(context, name):
    context.collection = context.database[name]


@then(u'the collection length will be {}')
def step_impl(context, length):
    nose.tools.assert_equal(context.collection.count(), int(length))


@then(u'each document will contain a {} field')
def step_impl(context, field):
    for document in context.collection.find():
        nose.tools.assert_in(field, document)


@then(u'each document will contain an {} field')
def step_impl(context, field):
    for document in context.collection.find():
        nose.tools.assert_in(field, document)


@then(u'each document {} field will equal {}')
def step_impl(context, field, value):
    value = eval(value)
    for document in context.collection.find():
        nose.tools.assert_in(field, document)
        nose.tools.assert_equal(value, document[field])


@then(u'each content field will contain an {role} role with content-type {type}')
def step_impl(context, role, type):
    role = eval(role)
    type = eval(type)

    for document in context.collection.find():
        nose.tools.assert_in(role, document["content"])
        nose.tools.assert_equal(type, document["content"][role]["content-type"])


@then(u'each content field will contain a {role} role with content-type {type}')
def step_impl(context, role, type):
    role = eval(role)
    type = eval(type)

    for document in context.collection.find():
        nose.tools.assert_in(role, document["content"])
        nose.tools.assert_equal(type, document["content"][role]["content-type"])

