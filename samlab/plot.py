# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import tensorflow.contrib.keras as keras
import numpy
import sklearn.metrics
import toyplot


def roc_curve(axes, labels, predictions):
    fpr, tpr, threshold = sklearn.metrics.roc_curve(labels, predictions, drop_intermediate=True)
    axes.x.label.text = "False positive rate"
    axes.y.label.text = "True positive rate"
    mark = axes.plot(fpr, tpr)
    return mark


def gradient_ascent(input_image, layer, index, width, height, step=1.0, regularization=0.8, iterations=100):
    def normalize(x):
        # utility function to normalize a tensor by its L2 norm
        return x / (keras.backend.sqrt(keras.backend.mean(keras.backend.square(x))) + 1e-5)

    loss = keras.backend.mean(layer.output[:, :, :, index])
    grads = keras.backend.gradients(loss, input_image)[0]
    grads = normalize(grads)
    iterate = keras.backend.function([input_image], [loss, grads])

    losses = []
    image = numpy.random.normal(size=(1, width, height, 3))
    for i in range(iterations):
        loss_value, grads_value = iterate([image])
        image += grads_value * step
        image *= regularization
        losses.append(loss_value)
    losses = numpy.array(losses)

    image -= image.mean()
    image /= (image.std() + 1e-5)
    image *= 0.1
    image += 0.5
    image = numpy.clip(image, 0, 1)
    image *= 255
    image = numpy.clip(image, 0, 255).astype("uint8")

    return image[0], losses


def training(completed, trial, yscale="log"):
    min_loss = trial["result"]["min-loss"]
    max_accuracy = trial["result"]["max-accuracy"]

    training_losses = completed.get_array(trial, "training-losses")
    validation_losses = completed.get_array(trial, "validation-losses")
    test_losses = completed.get_array(trial, "test-losses")

    training_accuracies = completed.get_array(trial, "training-accuracies")
    validation_accuracies = completed.get_array(trial, "validation-accuracies")
    test_accuracies = completed.get_array(trial, "test-accuracies")

    canvas = toyplot.Canvas(width=800, height=400)
    axes = canvas.cartesian(grid=(1, 2, 0), xlabel="Epoch", ylabel="Loss", yscale=yscale)

    legend = []
    legend.append(("Training", axes.plot(training_losses)))
    legend.append(("Validation", axes.plot(validation_losses)))
    legend.append(("Test", axes.plot(test_losses)))
    axes.vlines([min_loss, max_accuracy], color=["lightgray"])

    axes = canvas.cartesian(grid=(1, 2, 1), xlabel="Epoch", ylabel="Accuracy", ymin=0, ymax=1)
    axes.plot(training_accuracies)
    axes.plot(validation_accuracies)
    axes.plot(test_accuracies)
    axes.vlines([min_loss, max_accuracy], color=["lightgray"])

    canvas.legend(legend, corner=("right", 50, 50, 60))

    return canvas


def series(completed, keys, label=None):
    if label is None:
        label = "/".join(keys)

    palette = toyplot.color.Palette()

    canvas = toyplot.Canvas(width=1000, height=300)
    axes1 = canvas.cartesian(grid=(1, 4, 0, 1, 0, 3), xlabel="Trial", ylabel=label, palette=palette)
    axes2 = canvas.cartesian(grid=(1, 4, 0, 1, 3, 1), xlabel=label, ylabel="Test Accuracy", palette=palette)

    series = completed.get_series(keys)
    if not issubclass(series.dtype.type, numpy.number):
        try:
            series = numpy.ma.masked_where(series == None, series).astype("float")
        except:
            dictionary, series = numpy.unique(series, return_inverse=True)
            axes1.y.ticks.locator = toyplot.locator.Explicit(labels=dictionary)
            axes2.x.ticks.locator = toyplot.locator.Explicit(labels=dictionary)

    axes1.scatterplot(series)

    smooth_color = palette[0]
    smooth_color["r"] *= 0.6
    smooth_color["g"] *= 0.6
    smooth_color["b"] *= 0.6

    width = 20
    window = numpy.ones(width) / width # Window chosen to be "comparable to" 10-fold cross validation.
    smooth = numpy.convolve(series, window, mode="valid")
    axes1.plot(numpy.arange(width / 2, len(smooth) + width / 2), smooth, color=smooth_color)

    axes1.hlines(series.mean(), style={"stroke-width": 1, "stroke-dasharray": "2,3"})

    exp_key = completed.get_series(["exp_key"])
    boundaries = exp_key[:-1] != exp_key[1:]
    boundaries = numpy.flatnonzero(boundaries) + 1
    axes1.vlines(boundaries, style={"stroke-width": 1, "stroke-dasharray": "2,3"})

    axes2.scatterplot(series, completed.get_series(["result", "max-accuracy-test-accuracy"]), opacity=0.5)

    return canvas
