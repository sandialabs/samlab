.. image:: ../artwork/samlab.png
  :width: 200px
  :align: right


.. _overview:

Overview
========

Samlab provides a set of specifications and components that you can use to manage
machine learning experiments:


.. _database:

Database
--------

Samlab stores all of its data in a MongoDB database for efficient indexing and
retrieval.  You must have a running MongoDB instance and open a connection to
it using :func:`samlab.database.connect` before using the rest of the Samlab
API.  You can use :class:`samlab.database.Server` to get MongoDB up-and-running
quickly.  Note that Samlab requires MongoDB 3.6 or later.


.. _observations:

Observations
------------

Observations are the individual datums that you will use to train and evaluate
your machine learning algorithms.  An observation might be an image, a
timeseries, a text document, a video, or anything else from which you can
extract features.

Each observation includes `content`, which is one-or-more serialized
representations of the underlying data. The content could be an image, an
n-dimensional array, a block of text, a video, or any other data that
represents the observation.  Observation content can include multiple
representations, which allows a single observation to contain e.g.: a
full-sized image and a resampled version, or a word processing document and
text that has been extracted from it. This makes it convenient to store raw
observation data alongside preprocessed representations that have been
optimized for analysis.

In addition to content, each observation includes `created` and `modified`
timestamps, a set of categorical `tags`, and `attributes` that can store
arbitrary metadata.  Tags are an obvious choice to label observations for
classification, but they are available for any purpose - you can use tags
anywhere you need to identify subsets in your data, such as setting aside a
subset for training, or keeping track of which observations have been manually
reviewed by a human.  Attributes allow you to associate any metadata you want
with an observation, such as a value to be used for regression, the time and
location where an image was taken, a hyperlink from which an original document
was retrieved, a set of regions-of-interest in an image or video, etc.

To load observations into the database, use :func:`samlab.observation.create` or
:func:`samlab.observation.create_many`.  Use :func:`samlab.observation.set_tag`
to set and clear per-observation tags using your own criteria.
Use :func:`samlab.observation.resize_images` to scale original images into
versions suitable for machine learning artifacts with fixed-size inputs.


.. _experiments:

Experiments
-----------

Experiments contain the results of your machine learning experiments, stored in the
database. One experiment will include zero-to-many artifacts, along with
a `created` time, categorical `tags`, and metadata `attributes` that can be
used to organize your experiments in any way that suits you, much like observations.

Note that experiments can contain `content`, too.

Use :func:`samlab.experiment.create` to create experiments.


.. _artifacts:

Artifacts
------

Artifacts are the individual machine learning artifacts that you train as part of a
experiment.  Each artifact will have `content` that stores serialized representations of the
artifact (so that you can reload the artifact to make inferences later), along with
its `created` time, categorical `tags`, and metadata `attributes` that you can
use however you like.  Typically, a artifact's `attributes` will include the
hyperparameters used to train the artifact.

Just as observations can store multiple representations of a single
observation, artifacts can store different facets of a trained artifact.  For
example, a typical Samlab artifact might store a serialized version of the
underlying machine learning artifact, along with references to the observations
that were used for training, hyperparameters used during training, performance
metrics collected during training, and-so-on.

Use :func:`samlab.artifact.create` to create artifacts.


.. _server:

Samlab Server
-------------

The Samlab server is a web server providing a graphical user interface for
viewing and modifying existing observations, experiments, and artifacts.  Using
a web browser, you can search for them by their labels and attributes, edit
tags and attributes, provide ground-truth labels for newly-acquired
observations, explore your experiments using interactive visualizations, and
more.
