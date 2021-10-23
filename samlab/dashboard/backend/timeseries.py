# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import abc
import glob
import logging
import os
import re

import numpy
import watchdog.events
import watchdog.observers

from samlab.dashboard.service.notify import emit

log = logging.getLogger(__name__)


class TimeseriesCollection(abc.ABC):
    @abc.abstractmethod
    def __len__(self):
        """Return the number of timeseries in the collection."""
        raise NotImplementedError() # pragma: no cover


    @abc.abstractmethod
    def get(self, key):
        """Return a timeseries by key.

        Parameters
        ----------
        index: :class:`str`, required
            The key of the timeseries to return.

        Returns
        -------
        timeseries: :class:`numpy.ndarray`
            Numpy array containing timeseries fields.
        """
        raise NotImplementedError() # pragma: no cover


    @abc.abstractmethod
    def keys(self):
        raise NotImplementedError() # pragma: no cover


    @abc.abstractproperty
    @property
    def name(self):
        raise NotImplementedError() # pragma: no cover


    @property
    def service(self):
        return "timeseries-collection"


class Directory(TimeseriesCollection, watchdog.events.FileSystemEventHandler):
    def __init__(self, *, name, root, pattern=".*\.(csv|CSV)"):
        self._name = name
        self._root = root
        self._pattern = pattern
        self._re_pattern = re.compile(pattern)
        self._observer = watchdog.observers.Observer()
        self._observer.schedule(self, self._root, recursive=True)
        self._observer.start()
        self.reload()


    def __len__(self):
        return len(self._items)


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(root={self._root!r}, pattern={self._pattern!r})"


    def _match(self, path):
        return self._re_pattern.match(path)


    def get(self, key):
        data = numpy.loadtxt(self._items[key], skiprows=1, delimiter=",", dtype=str)
        if data.ndim < 2:
            return None

        if data.shape[1] == 1:
            return {
                "values": data[:,0].astype(numpy.float64),
                }
        elif data.shape[1] == 2:
            return {
                "timestamps": data[:,0].astype(numpy.float64),
                "values": data[:,1].astype(numpy.float64),
                }
        elif data.shape[1] == 3:
            return {
                "indices": data[:,0].astype(numpy.int64),
                "timestamps": data[:,1].astype(numpy.float64),
                "values": data[:,2].astype(numpy.float64),
            }
        elif data.shape[1] == 4:
            return {
                "indices": data[:,0].astype(numpy.int64),
                "timestamps": data[:,1].astype(numpy.float64),
                "values": data[:,2].astype(numpy.float64),
                "markers": data[:,3],
            }
        return None


    def keys(self):
        return self._items.keys()


    @property
    def name(self):
        return self._name


    def on_any_event(self, event):
        if event.is_directory:
            return
        if not self._match(event.src_path):
            return
        self.reload()


    def reload(self):
        log.info(f"{self.__class__.__name__}.reload")

        paths = []
        pattern = re.compile(self._pattern)
        for root, dirs, files in os.walk(self._root):
            for filename in files:
                if not self._match(filename):
                    continue
                paths.append(os.path.abspath(os.path.join(root, filename)))

        self._items = {os.path.relpath(os.path.splitext(path)[0], self._root) : path for path in sorted(paths)}

        emit("service-changed", {"service": "timeseries-collection", "name": self._name})
