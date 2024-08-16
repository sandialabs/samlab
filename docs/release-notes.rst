.. image:: ../artwork/samlab.png
  :width: 200px
  :align: right

.. _release-notes:

Release Notes
=============

Samlab 0.4.0 - August 16th, 2024
--------------------------------

Because there has been a proliferation of machine learning development
platforms, we are removing the Samlab Dashboard to focus on computer vision
model analysis. The new `samlab deepvis` command generates browser-based
analyses of popular models and datasets inspired by the proprietary "OpenAI
Microscope". Alternatively, you can use the `samlab.deepvis` module to
programmatically generate analyses for custom models and datasets.

Samlab 0.3.1 - August 16th, 2024
--------------------------------

* Final Samlab version that includes the Dashboard.

Samlab 0.3.0 - October 25th, 2021
---------------------------------

* Timeseries widget resizes plots to fit the window.
* Better logging during config-file loading.
* Reduced boilerplate and improved layout for all widgets.
* Added panning and zooming to the images widget.
* Removed all jquery and jquery-ui dependencies.
* Add an affordance for dragging widgets.
* Timeseries are organized by key instead of index, and multiple timeseries can be displayed in one widget.
* Timeseries can be selected using regular expressions.
* Timeseries use consistent colors for each series.
* Timeseries have positionable legends.
* Added selenium-based regression tests.
* Restore active widget tracking, which was broken.
* Add an option to ignore config files at startup.
* Moved dashboard web server code into a separate module.
* Fixed problems collecting code coverage stats.
* Added a menu control and improved consistency throughout the UI.
* Mouse input extends outside the image boundary when creating bounding boxes.
* Made it harder to accidentally create tiny bounding boxes.
* Added client API to simplify writing documents and timeseries to disk.
* Added options for explicit and automatic timeseries widget updating.
* Cleaned-up keyboard shortcuts.

Samlab 0.2.0 - October 13th, 2021
---------------------------------

* Complete rewrite of the dashboard server, replacing the MongoDB storage with a more flexible system of backend data adapters - now, Samlab adjusts to work with your data, instead of the other way around.

Samlab 0.1.0 - May 24th, 2018
-----------------------------

* Initial Release
