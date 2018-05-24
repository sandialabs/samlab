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
quickly.


.. _observations:

Observations
------------

Observations are the individual datums that you will use to train and evaluate
your machine learning algorithms.  An observation might be an image, a
timeseries, a text document, or anything else from which you can extract
features.

Each observation has `content`, which is serialized representations of the
underlying data. The content could be an image, an n-dimensional array, a block
of text, or any other data that represents the observation.  Observation
content can store multiple representations, known as `roles`, which allows a
single observation to contain e.g.: a full-sized image and a resampled version,
or a word processing document and text that has been extracted from it. This
makes it convenient to store raw observation data alongside preprocessed
representations that have been optimized for analysis.

In addition to content, each observation includes `created` and `modified`
timestamps, a set of categorical `tags`, and `attributes` that can store
arbitrary metadata.  Tags can be used to label observations for classification,
but they are available for any purpose - you can use tags anywhere you need to
identify subsets in your data, such as setting aside a subset for training, or
keeping track of which observations have been reviewed by a human.  Attributes
allow you to associate any metadata you want with an observation, such as a
value to be used for regression, the time and location where an image was
taken, a hyperlink from which an original document was retrieved, etc.

To load observations into the database, you should use the
:func:`samlab.observation.create_many` function.  Use :func:`samlab.observation.set_tag`
to set and clear per-observation tags using your own criteria.
Use :func:`samlab.observation.resize_images` to scale original images into
versions suitable for machine learning models with fixed-size inputs.


.. _trials:

Trials
------

Trials are the results of your machine learning experiments, stored in the
database. One trial will include zero-to-many newly trained models, along with
a `created` time, categorical `tags`, and metadata `attributes` that can be
used to organize your trials in any way that suits you, much like observations.

Note that a trial can contain more than one model - so a 5 by 2 cross
validation experiment could be stored as a single trial containing ten
models.

Use :func:`samlab.trial.create` to create trials.


.. _models:

Models
------

Models are the individual machine learning models that you train as part of a
trial.  Each model will have `content` that stores a serialized version of the
model (so that you can reload the model to make inferences later), along with
its `created` time, categorical `tags`, and metadata `attributes` that you can
use however you like.  Typically, a model's `attributes` will include the
hyperparameters used to train the model.

Just as observations use `roles` to store multiple representations of a single
observation, models can have multiple `roles` storing different facets of a
trained model.  For example, a typical Samlab model might store a serialized
version of the underlying machine learning model, along with references to the
observations that were used for training, hyperparameters used during training,
performance metrics collected during training, and-so-on.

Use :func:`samlab.model.create` to create models.


.. _trial-generators:

Trial Generators
----------------

A trial generator is a function you create that will generate a single trial.
Typically, a trial generator will load a set of observations from the database,
extract input and output features, partition the data for training, validation,
and test, and train one-or-more models on the data.  Samlab provides simple
components to make this process easy, but it is up to you to decide which steps
are necessary - for example, some problems might require streaming the data to
reduce memory consumption and repeating it for data augmentation, while for
other problems you simply want to load the data and use it directly.

A trial generator function should take a single `parameters` argument as input,
and return a single scalar value as output.  The `parameters` argument will be
a dict containing hyperparameters to be used during training, while the output
value should be a loss function value that can be used for hyperparameter
search.  If a failure occurs during trial generation, the trial generator
should catch any exceptions and return `None`.


.. _inputs:

Inputs
------

Inputs are the per-observation feature vectors that are used for training new
models, and evaluating existing models.  Typically, you will use
:func:`samlab.static.load` to load observations from the database, and
functions such as :func:`samlab.static.map` and :func:`samlab.stream.image_load`
to extract input features from those observations.


.. _outputs:

Outputs
-------

Outputs are the per-observation target values that models are trained to
predict from their :ref:`inputs`.  Typically, you will use
:func:`samlab.static.load` to load observations from the database and
:func:`samlab.static.map` to extract outputs for each observation.  Keep
in mind that outputs can be arbitrary-length vectors - they might be single
values for a regression problem, or they could be multiple "one-hot" values for
a categorical problem, etc.


.. _weights:

Weights
-------

Weights are per-observation scalar values that can be used to alter how much
influence the given observation will have during training.


.. _static-data:

Static Data
-----------

Static data is a collection of four arrays containing :ref:`observations`,
:ref:`inputs`, :ref:`outputs`, and :ref:`weights` that can be used for training
models.  Note that the lengths of the four arrays must always be the same,
since each observation is mapped to one input vector, one output vector, and
one weight.

The :func:`samlab.static.load` function returns static data containing
observations, null inputs and outputs, and uniform weights. Use
:func:`samlab.static.map` to extract input and output vectors or adjust the
weights in static data using your own custom logic.  The :func:`samlab.static.log_outputs`
function logs information about the distribution of output features (typically for
classification problems) in static data.


.. _partition-generators:

Partition Generators
--------------------

Partition generators are functions that you use to partition your data into
training, validation, and test subsets.  Partition generators take
:ref:`static-data` as input and produces arrays of training, validation, and
test indices as output.  You then use those indices to access subsets of the
original data.

Samlab provides partition generators for stratified sampling
(:func:`samlab.train.stratify`) and cross validation
(:func:`samlab.train.k_fold`), or you can create your own custom partition
generators.  For example, you might create a custom partition generator to
partition data based on tags in your observations, or by thresholding a value
in the observation attributes, or by any other criteria of your choosing.  You
will want to use :func:`samlab.train.log_partition` to see useful information
about how your data was partitioned at runtime.

Partition generators are specified so that they can produce more than one
partition - for example: :func:`samlab.train.k_fold` with default parameters will
produce ten partitions for 5x2 cross validation.  So you will typically iterate
over the partitions returned by a partition generator, and train one model for
each::

    for partition in samlab.train.k_fold(inputs, outputs):
        train_a_model(inputs, outputs, partition)


.. _streaming-data:

Streaming Data
--------------

For many problems, loading every input vector into memory at once may be too
expensive, such as when your input vectors are images or video.  Or, there may
be times when you wish to augment your data by introducing variations on the
original observations without actually storing them in the database, as is common
when training image classification networks.  In both cases, the solution is to
convert :ref:`static-data` into streaming data.  With streaming data, the inputs,
outputs, and weights for each observation can be computed on-the-fly using generator
expressions that return one (observation, input, output, weight) tuple at-a-time.

Use the :func:`samlab.static.stream` function to convert :ref:`static-data`
into streaming data. After conversion, :func:`samlab.stream.image_load` loads an instance
of :class:`PIL.Image.Image` for each observation in a stream,
:func:`samlab.stream.image_transform` applies random transformations suitable for
augmentation to the images, and :func:`samlab.stream.image_to_array` converts the images
to feature vectors ready for training.


.. _model-generators:

Model Generators
----------------

Model generators are functions provided by Samlab that train a single machine
learning model.  Use them in your trial generator implementation, or write your
own custom code to train a model.  Currently, Samlab provides the
:func:`samlab.model.fine_tune_vgg16` model generator.


.. _hyperparameter-search:

Hyperparameter Search
---------------------

Typically, once you've written your own :ref:`trial generator <trial-generators>`,
you'll simply call it yourself to generate a new trial.  However, you may also
want to call it repeatedly to perform a hyperparameter search. While you could
implement the search yourself, Samlab provides functionality to use your trial
generator with existing hyperparameter search libraries.  For example, the
:func:`samlab.hyperopt.adapter` function can be used to wrap your trial
generator for use with `hyperopt.fmin`.


.. _manager:

Samlab Manager
--------------

The Samlab manager is a web server providing a graphical user interface for
viewing and modifying existing observations, trials, and models.  Using a web
browser, you can search for observations, trials, and models by their labels
and attributes, edit tags and attributes, provide ground-truth labels for
newly-acquired observations, explore trained models using inteeractive
visualizations, and more.
