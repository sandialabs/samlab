# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

log = logging.getLogger(__name__)

_backends = {}


def get_datasets(*, service=None):
    results = set()
    for key in _backends:
        if isinstance(key, str):
            continue
        else:
            key_service, key_dataset = key
            if service is not None and service != key_service:
                continue
            results.add(key_dataset)
    return results


def require_backend(key):
    if isinstance(key, str):
        if key not in _backends:
            raise RuntimeError(f"No backend found for service: {key}.")
    else:
        if key not in _backends:
            service, name = key
            raise RuntimeError(f"No backend found for service: {service} name {name}.")

    return _backends[key]


def set_backend(service, backend):
    name = backend.name
    if name:
        log.info(f"Assigning {backend} to service: {service} name: {name}.")
        _backends[(service, name)] = backend
    else:
        log.info(f"Assigning {backend} to service: {service}.")
        _backends[service] = backend

