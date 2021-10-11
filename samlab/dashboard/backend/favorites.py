# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import abc
import json
import logging
import os

from samlab.dashboard import socketio


log = logging.getLogger(__name__)


class Favorites(abc.ABC):
    @abc.abstractmethod
    def create(self, service, name, label):
        """Mark an item as a favorite.

        Parameters
        ----------
        service: str, required
            Service type.
        name: str, required.
            Service name of the item to be favorited.
        label: str, required.
            Human-readable label for the favorite.
        """
        raise NotImplementedError()


    @abc.abstractmethod
    def delete(self, service, name):
        """Un-favorite an item.

        Parameters
        ----------
        service: str, required
            Service type.
        name: str, required.
            Service name of the item to be un-favorited.
        """
        raise NotImplementedError()


    @abc.abstractmethod
    def get(self):
        """Return a sequence of favorites."""
        raise NotImplementedError()


    @property
    def name(self):
        """Return the name of this backend."""
        return None


    @property
    def service(self):
        """Return the service type implemented by this backend."""
        return "favorites"


class JSONFile(Favorites):
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


    def create(self, service, name, label):
        log.debug(f"Create favorite: {service} {name} {label}.")

        assert(isinstance(service, str))
        assert(isinstance(name, str))
        assert(isinstance(label, str))
        if service not in self._favorites:
            self._favorites[service] = {}
        message = "favorite-changed" if name in self._favorites[service] else "favorite-created"
        self._favorites[service][name] = label
        self._save()
        socketio.emit(message, {"service": service, "name": name, "label": label})


    def delete(self, service, name):
        log.debug(f"Delete favorite: {service} {name}.")

        assert(isinstance(service, str))
        assert(isinstance(name, str))
        if service in self._favorites:
            if name in self._favorites[service]:
                del self._favorites[service][name]
                self._save()
                socketio.emit("favorite-deleted", {"service": service, "name": name})


    def get(self):
        results = []
        for service, names in self._favorites.items():
            for name, label in names.items():
                results.append({"service": service, "name": name, "label": label})
        results = sorted(results, key=lambda f: (f["service"], f["label"], f["name"]))
        return results
