# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import abc
import glob
import logging
import os

log = logging.getLogger(__name__)


class ImageCollection(abc.ABC):
    def __len__(self):
        raise NotImplementedError()

    def get(self, *, index):
        raise NotImplementedError()


class DirectoryImageCollection(ImageCollection):
    def __init__(self, directory):
        self._directory = directory
        self._paths = []


    def __len__(self):
        return len(self._paths)


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(directory={self._directory!r})"


    def get(self, *, index):
        return self._paths[index]

