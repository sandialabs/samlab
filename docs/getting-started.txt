#!/usr/bin/env python
# coding: utf-8

# .. _getting-started:
# 
# # Getting Started
# 
# Let's explore how to integrate Samlab into your workflow.  For this example, we will be training a simple neural network model to smooth waveforms.  That is, if we feed our trained model the noisy green curve in the following plot as input, we want the model to produce a smoothed version of it (the smooth orange curve) as output:

# In[1]:


import numpy
numpy.random.seed(1234)

import toyplot

kernel = numpy.ones(9)
kernel /= numpy.sum(kernel)

input_features = numpy.cumsum(numpy.random.normal(size=(100,)))
output_features = numpy.convolve(input_features, kernel, mode="same")
example = numpy.column_stack((input_features, output_features))


# In[2]:


toyplot.plot(example, width=600, height=250);


# ## Preliminaries
# 
# It's a good idea to turn-on Python's standard logging, as Samlab uses it extensively for informational and debugging output:

# In[3]:


import logging
logging.basicConfig(level=logging.INFO)


# In addition, we need to have a running instance of MongoDB that Samlab will use to store the generated observations.  For production use, you will likely want to setup and administer a shared instance of MongoDB on your own, but for  tutorials and quick tests, Samlab provides a simple way to quickly startup a MongoDB server that stores data in a temporary location:

# In[4]:


import samlab.database
db_server = samlab.database.Server()


# ... note that the data is effectively lost once the temporary server is stopped, so you would not want to use it for real work!
# 
# Now, we can create a database connection to the server:

# In[5]:


database, fs = samlab.database.connect("example", db_server.uri)


# Note that the "example" database is automatically created if it doesn't already exist on the given server.

# ## Data Ingestion
# 
# Before we can create a model, we'll need to generate some training data and put it in the Samlab database.  For this tutorial, we'll start with a function that creates :ref:`observations` at random:

# In[6]:


import numpy
import samlab.serialize

def generate_observation():
    kernel = numpy.ones(9)
    kernel /= numpy.sum(kernel)

    input_features = numpy.cumsum(numpy.random.normal(size=(100,)))
    output_features = numpy.convolve(input_features, kernel, mode="same")

    attributes = {"filter-width": 9, "acknowledgements": "For Bev, and all she does to make life great."}
    content = {
        "input": samlab.serialize.array(input_features),
        "output": samlab.serialize.array(output_features),
        }
    tags = ["example", "smoothing"]
    
    return attributes, content, tags


#  We'll use :func:`samlab.observation.create_many` with our function to generate observations and store them in the database:

# In[7]:


import samlab.observation
with samlab.observation.create_many(database, fs) as observations:
    for i in range(1000):
        attributes, content, tags = generate_observation()
        observations.create(attributes=attributes, content=content, tags=tags)


# Typically, we would load training data from disk or a database, but in this case we are generating input and output feature vectors on the fly using random walks and convolution.  Note that we create one set of input and output feature vectors at a time, and pass them (along with attributes and tags) to Samlab.  This design ensures that we can ingest large numbers of observations even if they don't all fit into memory at once.  In addition, the observation *contents* must all be serializable to the MongoDB database, which is why we use :func:`samlab.serialize.array` to convert our :class:`numpy.ndarray` content to a serializable representation.  There are many functions in :mod:`samlab.serialize` to handle various content data types.

# ## Training
# 
# With our observations stored in the database, we're ready to train our model, which will consist of the following steps:
# 
# * Loading observations.
# * Extracting features and weights.
# * Partitioning the data.
# * Training models.
# * Storing results.

# ### Loading Observations
# 
# First, we'll load observations from the database using :func:`samlab.static.load`:

# In[8]:


import samlab.static
observations, inputs, outputs, weights = samlab.static.load(database)


# The set of four arrays returned - observations, inputs, outputs, and weights - are known in Samlab as :ref:`static-data`.  Collectively, they store the observations retrieved from the database and the input feature vectors, output feature vectors, and weights extracted from those observations, respectively.  For this reason, the lengths of the four arrays are always the same: 

# In[9]:


print(len(observations), len(inputs), len(outputs), len(weights))


# If you examine a subset of the observations array, you will see that it contains observation records from the database:

# In[10]:


observations[0]


# Each record is a subset of the observation that contains its metadata, but not the raw content data.  This ensures that the observation data will fit in memory, while providing the information you will use to extract features from each observation.

# The input and output arrays default to empty values, and the weights array defaults to uniform weights for all observations:

# In[11]:


inputs[:3]


# In[12]:


outputs[:3]


# In[13]:


weights[:3]


# We'll substitute real inputs and outputs in the next section.

# ### Extracting Features and Weights
# 
# Because you can (within reason) store any data you like in an observation, it's up to you to extract the input and output feature vectors that will be used for training.  For an image classification problem, you might store both an original image and a resampled fixed-size image, and use observation tags to store the class.  Or you might use observation attribues to store a regression value.
# 
# In our case, since we explicitly stored the input and output vectors in the observation content, we just need to pull them back out again, using a custom callback function and :func:`samlab.static.map`:

# In[14]:


import samlab.deserialize

def extract_features(observation, input, output, weight):
    input = samlab.deserialize.array(fs, observation["content"]["input"])
    output = samlab.deserialize.array(fs, observation["content"]["output"])
    return input, output, weight


# Our callback function receives one observation (and corresponding input, output, and weight) at a time, returning new input, output, and weight values that may-or-may-not differ from the inputs.  Note that in this case our function overwrites the input and output feature vectors with data from the database, while leaving the weight values unchanged.  Now, we use our callback with :func:`samlab.static.map` to update our static data arrays:

# In[15]:


observations, inputs, outputs, weights = samlab.static.map(
        observations,
        inputs,
        outputs,
        weights,
        extract_features,
    )


# This way of working may seem roundabout to you for our toy problem; however, this approach to feature extraction provides tremendous flexibility: for example, we could have computed the smoothed version of our curve in the `extract_features` callback instead of storing it in the database.  In later examples, we'll see how we can extend this approach to streaming data and data augmentation when we can't fit even our features into memory simultaneously.

# ### Partitioning Data
# 
# For this problem, we will want to partition our observations into a training set to be used for training our model, a validation set that we can use to determine when training should stop, and a test set that we will use to evaluate the performance of our trained model.  To do this, Samlab provides :ref:`partition-generators`, which are functions that return one-or-more partitions for a given set of observations. Each partition includes a label and three arrays of indices that you use to access subsets of your static data, for training, validation, and testing:

# In[16]:


import samlab.train

for partition in samlab.train.random(
        inputs,
        outputs,
        validation_split=0.2,
        test_split=0.5,
        n=1,
    ):
    partition_label, training, validation, testing = partition
    print(partition_label, len(training), len(validation), len(testing))


# Notice in this example that for our 1000 observations we used :func:`samlab.train.random` to generate one partition (```n=1```) that set aside 500 observations (```test_split=0.5```) for testing and 100 of the remaining 500 observations (```validation_split=0.2```) for validation, leaving 400 observations for training.

# ### Training Models
# 
# Now that we have our feature vectors and partitions, we're ready to train a model.  For this example, we'll use a simple Keras neural network to train using our input and output features:

# In[17]:


from tensorflow.contrib import keras

model = keras.models.Sequential()
model.add(keras.layers.Dense(outputs.shape[1], input_shape=(inputs.shape[1],)))
model.compile(loss="mse", optimizer="adam")

history = model.fit(
    inputs[training],
    outputs[training],
    epochs=2000,
    validation_data=(inputs[validation], outputs[validation]),
    verbose=0,
)


# And we can make predictions using our test partition:

# In[18]:


predictions = model.predict(inputs[testing])


# When we spot-check one of our predictions against the ground truth, we see that the blue prediction plot obscures the orange ground truth plot, indicating that our network is performing well:

# In[19]:


import toyplot

canvas, axes, mark = toyplot.plot(inputs[testing][0], width=600, height=300)
axes.plot(outputs[testing][0])
axes.plot(predictions[0]);


# ### Storing Results
# 
# Now that our model has been trained, we're ready to save it to the database for later analysis and re-use.  We can store as much or as little of our results as we like, but we will benefit from saving a few standard artifacts:

# In[20]:


content = {
    "model": samlab.serialize.keras_model(model),
    "observations": samlab.serialize.array([observation["_id"] for observation in observations]),
    "training-indices": samlab.serialize.array(training),
    "training-losses": samlab.serialize.array(history.history["loss"]),
    "validation-indices": samlab.serialize.array(validation),
    "validation-losses": samlab.serialize.array(history.history["val_loss"]),
    "test-indices": samlab.serialize.array(testing),
}


# ... in this case saving `model` allows us to analyze it and use it in the future to make new predictions, while `observations`, `training-indices`, `validation-indices`, and `test-indices` can be used to recreate the data used during training if necessary.  `training-losses` and `validation-losses` are commonly used in visualization to understand how successful the training process was and whether there was overfitting.
# 
# By saving these standard artifacts, tools like the :ref:`samlab-manager` can be used to perform sophisticated analysis and post processing of experiment results.

# Samlab requires that we explicitly store our experiment using a :ref:`Samlab trial <trials>`, and the models we created as a :ref:`Samlab model <models>`:

# In[21]:


import samlab.trial
trial = samlab.trial.create(
    database,
    fs,
    name="Example trial",
    attributes={"height":1.88, "location": "USA"},
    tags=["examples", "smoothing"],
)


# In[22]:


import samlab.model
model = samlab.model.create(
    database,
    fs,
    trial,
    name=partition_label,
    content=content,
    attributes={"quality": 2.3},
    tags=["examples", "smoothing", "production"],
)


# ## Samlab Manager
# 
# Before we shut-down our temporary database server, let's take a quick look through the database using the :ref:`samlab-manager`.  Like the temporary database server, Samlab provides an easy way to run the Samlab Manager web server:

# In[23]:


import samlab.manager
manager = samlab.manager.Server(database_name=database.name, database_uri=db_server.uri, database_replica_set=db_server.replica_set)


# This starts an instance of Samlab Manager, connected to the same database we used to store our results.
# 
# Now, we can open a web browser to see the Samlab Manager user interface:
# 
#     manager.open_browser()
# 
# ![](samlab-manager-1.png)
# 
# Samlab Manager provides a *dashboard* with *widgets* that you can add, rearrange, resize, and delete in any way that you like.  By default, the *Trials widget* is open, which displays a list of trials stored in the database, such as the trial we just saved.  Use the *Operations Menu* to open an *Observations widget*:
# 
# ![](samlab-manager-2.png)
# 
# The Observations widget displays all of the observations stored in the database that we created earlier (1000), provides controls for choosing an observation, and displays the data ("input" and "output") stored in the currently-visible observation (it also displays the attributes and tags stored with the observation):
# 
# ![](samlab-manager-3.png)
# 
# If our observations contained image data, the images themselves would be displayed.  Note that you could use the Observations widget operations menu to make changes to the current observation:
# 
# ![](samlab-manager-4.png)
# 
# But for now, we'll move-on.  Click the close button in the upper-right-hand corner of the Observations widget to remove it, and select the trial that we created earlier using the *Trials widget*:
# 
# ![](samlab-manager-5.png)
# 
# A *Trial widget* opens, displaying the trial's name, attributes and tags:
# 
# ![](samlab-manager-6.png)
# 
# You can use the Trial widget operations menu to make changes to the trial.  You can also open the model we created as part of the trial:
# 
# ![](samlab-manager-7.png)
# 
# The *Model widget* opens, and displays the attributes and tags associated with the model:
# 
# ![](samlab-manager-8.png)
# 
# Using the Model widget operations menu, we can display a model-specific visualization.  In this case, let's see how the model's loss function evolved during training:
# 
# ![](samlab-manager-9.png)
# 
# The *Training Loss widget* opens, and provides an interactive visualization.  Note that storing standard artifacts with a model is what makes this visualization possible (depending on the size of your web browser window, you may have to scroll to show the newly-opened widget):
# 
# ![](samlab-manager-10.png)
# 
# Let's look directly at some of the model content.  Notice that the *Model widget* includes a list of entries for each of the content roles we stored in the model.  Let's open the *model* content:
# 
# ![](samlab-manager-11.png)
# 
# The *Model Content widget* opens, and you can see that - because Samlab detects that this is a Keras model - it can display a description of the model layers:
# 
# ![](samlab-manager-12.png)
# 
# That's it for now; keep in mind that Samlab Manager provides a large and growing set of visualizations and analyses for your data.

# ## Cleanup
# 
# Now, we just need to cleanup the servers we started at the beginning of this exercise.  Stop the Samlab Manager server first:

# In[24]:


manager.stop()


# Finally, stop the temporary database server:

# In[25]:


db_server.stop()

