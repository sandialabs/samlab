# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import abc
import glob
import os
import re


class ImageCollection(abc.ABC):
    def __len__(self):
        """Return the number of images in the collection."""
        raise NotImplementedError()

    def get(self, index):
        """Return an image by index.

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


class DirectoryImageCollection(ImageCollection):
    def __init__(self, directory, pattern=".*\.(png|jpg|jpeg)"):
        self._directory = directory
        self._pattern = pattern
        self._update()

    def _update(self):
        paths = []
        pattern = re.compile(self._pattern)
        for root, dirs, files in os.walk(self._directory):
            for filename in files:
                if not pattern.match(filename):
                    continue
                paths.append(os.path.abspath(os.path.join(root, filename)))
        self._paths = paths


    def __len__(self):
        return len(self._paths)


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(directory={self._directory!r}, pattern={self._pattern!r})"


    def get(self, index):
        return self._paths[index]

