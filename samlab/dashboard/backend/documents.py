# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import abc
import glob
import logging
import os
import re

import watchdog.events
import watchdog.observers

from samlab.dashboard.service.notify import emit

log = logging.getLogger(__name__)


class DocumentCollection(abc.ABC):
    @abc.abstractmethod
    def __len__(self):
        """Return the number of documents in the collection."""
        raise NotImplementedError() # pragma: no cover


    @abc.abstractmethod
    def get(self, index):
        """Return a document by index.

        Parameters
        ----------
        index: int, required
            The index of the image to return.

        Returns
        -------
        image: :class:`str` or :class:`numpy.ndarray`
            If :class:`str`, the filesystem path of the image.
        """
        raise NotImplementedError() # pragma: no cover


    @abc.abstractproperty
    @property
    def name(self):
        raise NotImplementedError() # pragma: no cover


    @property
    def service(self):
        return "document-collection"


class Directory(DocumentCollection, watchdog.events.FileSystemEventHandler):
    def __init__(self, *, name, root, pattern=".*\.(html|txt)"):
        self._name = name
        self._root = root
        self._pattern = pattern
        self._re_pattern = re.compile(pattern)
        self._observer = watchdog.observers.Observer()
        self._observer.schedule(self, self._root, recursive=True)
        self._observer.start()
        self.reload()


    def __len__(self):
        return len(self._paths)


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(root={self._root!r}, pattern={self._pattern!r})"


    def _match(self, path):
        return self._re_pattern.match(path)


    def get(self, index):
        return self._paths[index]


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
        paths = []
        pattern = re.compile(self._pattern)
        for root, dirs, files in os.walk(self._root):
            for filename in files:
                if not self._match(filename):
                    continue
                paths.append(os.path.abspath(os.path.join(root, filename)))
        self._paths = sorted(paths)

        log.info(f"{self.__class__.__name__} loaded {len(self)} documents from {self._root}.")

        emit("service-changed", {"service": "document-collection", "name": self._name})
