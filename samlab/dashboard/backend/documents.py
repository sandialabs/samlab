# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import abc
import glob
import os
import re


class DocumentCollection(abc.ABC):
    @abc.abstractmethod
    def __len__(self):
        """Return the number of images in the collection."""
        raise NotImplementedError()


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
        raise NotImplementedError()


    @abc.abstractmethod
    def tags(self, index):
        raise NotImplementedError()


class Directory(DocumentCollection):
    def __init__(self, root, pattern=".*\.(html|txt)"):
        self._root = root
        self._pattern = pattern
        self._update()


    def _update(self):
        paths = []
        pattern = re.compile(self._pattern)
        for root, dirs, files in os.walk(self._root):
            for filename in files:
                if not pattern.match(filename):
                    continue
                paths.append(os.path.abspath(os.path.join(root, filename)))
        self._paths = paths


    def __len__(self):
        return len(self._paths)


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(root={self._root!r}, pattern={self._pattern!r})"


    def get(self, index):
        return self._paths[index]


    def tags(self, index):
        return []
