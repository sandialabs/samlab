.. image:: ../artwork/samlab.png
  :width: 200px
  :align: right


.. _overview:

Overview
========

Samlab provides a set of tools that you can use to create, monitor, and
analyze your machine learning experiments:

.. _command-line:

Command Line Tools
------------------

*samlab-gputop* provides a colorful, updating display of how hard your GPUs are working.

Dashboard
---------

The Samlab :ref:`dashboard` is a web server providing a graphical user interface for
annotating images, monitoring experiments, and analyzing results.  Unlike comparable
tools (Tensorboard, Visdom, Vott, ...), Samlab adapts to your data instead of forcing
you to store it in databases, binary records, or other organizations.  In most cases,
a Samlab data adapter can be written in fewer lines of code than you'd need to convert
your data to a tool-specific format, and avoids the pitfalls of data duplication.

Interaction
-----------

Samlab functions make it easy to see your experiments' progress, and interrupt an
experiment gracefully, without data loss.

.. _notebook:

Notebooks
---------

Samlab provides convenience functions to simplify displaying data in Jupyter notebooks.

.. _torch:

Torch
-----

Samlab provides convenience functions for working with PyTorch, such as a function to
automatically choose a Torch device based on load, making it easy to run multiple experiments
simultaneously without accidentally selecting the same device.

