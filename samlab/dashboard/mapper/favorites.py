# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with :ref:`favorites`."""

import abc
import json
import logging
import os

log = logging.getLogger(__name__)


class Favorites(abc.ABC):
    def contains(self, otype, oid):
        raise NotImplementedError()

    def create(self, otype, oid, name):
        raise NotImplementedError()

    def delete(self, otype, oid):
        raise NotImplementedError()

    def get(self):
        raise NotImplementedError()


class JSONDiskFavorites(Favorites):
    def __init__(self, storage):
        self._storage = storage
        self._favorites = {}
        if os.path.exists(storage):
            try:
                with open(self._storage, "r") as stream:
                    self._favorites = dict(json.load(stream))
            except Exception as e:
                log.error(f"Uncaught exception: {e}")


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(storage={self._storage!r})"

    def _save(self):
        if not os.path.exists(os.path.dirname(self._storage)):
            os.makedirs(os.path.dirname(self._storage))
        with open(self._storage, "w") as stream:
            json.dump(self._favorites, stream)


    def contains(self, otype, oid):
        return otype in self._favorites and oid in self._favorites[otype]


    def create(self, otype, oid, name):
        """Mark an object as a favorite.

        Parameters
        ----------
        otype: str, required
            Object type.  One of "layouts".
        oid: str, required.
            ID of the object to be favorited.
        name: str, required.
            Human-readable label for the favorite.
        """
        log.debug(f"Create favorite: {otype} {oid} {name}.")

        assert(isinstance(otype, str))
        assert(isinstance(oid, str))
        assert(isinstance(name, str))
        if otype not in self._favorites:
            self._favorites[otype] = {}
        self._favorites[otype][oid] = name
        self._save()


    def delete(self, otype, oid):
        """Un-favorite an object.

        Parameters
        ----------
        otype: str, required
            Object type.  One of "layouts".
        oid: str, required.
            ID of the object to be un-favorited.
        """
        log.debug(f"Delete favorite: {otype} {oid}.")

        assert(isinstance(otype, str))
        assert(isinstance(oid, str))
        if otype in self._favorites:
            if oid in self._favorites[otype]:
                del self._favorites[otype][oid]
                self._save()


    def get(self):
        for otype, oids in self._favorites.items():
            for oid, name in oids.items():
                yield {"otype": otype, "oid": oid, "name": name}

