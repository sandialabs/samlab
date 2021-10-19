# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging
import sys

import coverage

def before_all(context):
    context.coverage = coverage.Coverage(auto_data=True, config_file=False, data_suffix=False, include="samlab*")
    context.coverage.start()

def after_all(context):
    try:
        context.coverage.stop()
        context.coverage.combine()
        context.coverage.report()
        context.coverage.html_report(directory=".cover")
        context.coverage.save()
    except coverage.CoverageException as e:
        pass
