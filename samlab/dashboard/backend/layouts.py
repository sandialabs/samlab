# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import abc
import hashlib
import json
import logging
import os

log = logging.getLogger(__name__)


class Layouts(abc.ABC):
    @abc.abstractmethod
    def get(self, *, lid):
        raise NotImplementedError()


    @property
    def name(self):
        return None


    @abc.abstractmethod
    def put(self, *, content):
        raise NotImplementedError()


    @property
    def service(self):
        return "layouts"


class JSONFile(Layouts):
    def __init__(self, storage):
        self._storage = storage
        self._layouts = {}
        if os.path.exists(storage):
            try:
                with open(self._storage, "r") as stream:
                    self._layouts = json.load(stream)
            except Exception as e:
                log.error(f"Uncaught exception: {e}")


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(storage={self._storage!r})"


    def _save(self):
        if not os.path.exists(os.path.dirname(self._storage)):
            os.makedirs(os.path.dirname(self._storage))
        with open(self._storage, "w") as stream:
            json.dump(self._layouts, stream, indent=2, sort_keys=True)


    def get(self, *, lid):
        if lid in self._layouts:
            return self._layouts[lid]
        return None


    def put(self, *, content):
        if not isinstance(content, list):
            raise ValueError(f"Layout content must be a list, received {type(content)}.")

        lid = hashlib.md5(json.dumps(content, separators=(",",":"), indent=None, sort_keys=True).encode("utf-8")).hexdigest()

        if lid not in self._layouts:
            self._layouts[lid] = content
            self._save()

        return lid
