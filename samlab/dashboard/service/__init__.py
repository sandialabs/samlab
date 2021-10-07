# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

log = logging.getLogger(__name__)

_backends = {}


def require_backend(service, name=None):
    if service not in _backends:
        raise RuntimeError(f"No backend found for service: {service}.")
    if name not in _backends[service]:
        raise RuntimeError(f"No backend found for service: {service} name: {name}.")
    return _backends[service][name]


def register_backend(backend):
    service = backend.service
    name = backend.name
    if service not in _backends:
        _backends[service] = {}
    if name in _backends[service]:
        log.warning(f"Overwriting {service}/{name} {_backends[service][name]} with {backend}.")
    _backends[service][name] = backend
    log.info(f"Registered {backend} as {service}/{name}.")

