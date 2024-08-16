.. image:: ../artwork/samlab.png
  :width: 200px
  :align: right

.. _installation:

Installation
============

Samlab
------

To install the latest stable version of Samlab and its dependencies, use `pip`::

    $ pip install samlab

... following that, you'll be able to use all of Samlab's features.

Documentation
-------------

We assume that you'll normally access this documentation online, but if you want
a local copy on your own computer, do the following:

Install Samlab along with all of the dependencies needed to build the documentation:

    $ pip install samlab[doc]

Next, do the following to download a tarball to the current directory
containing all of the Samlab source code, which includes the documentation::

    $ pip download samlab --no-binary=:all: --no-deps

Now, you can extract the tarball contents and build the documentation (adjust the
following for the version you downloaded)::

    $ tar xzvf samlab-0.4.0.tar.gz
    $ cd samlab-0.4.0/docs
    $ make html


