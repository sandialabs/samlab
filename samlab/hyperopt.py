# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with `Hyperopt <https://github.com/hyperopt/hyperopt>`_."""

from __future__ import absolute_import, division, print_function, unicode_literals

import hyperopt

def adapter(function):
    """Wrap a trial generator function for use with `Hyperopt <https://github.com/hyperopt/hyperopt>`_.

    Parameters
    ----------
    function: the ref:`trial-generator` to be wrapped.

    Returns
    -------
    wrapped: callable
        A wrapped version of `function` that can be optimized using Hyperopt.
    """
    def implementation(parameters):
        loss = function(parameters)
        if loss is None:
            return {"status": hyperopt.STATUS_FAIL}
        else:
            return {"loss": loss, "status": hyperopt.STATUS_OK}

    return implementation
