# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging

log = logging.getLogger(__name__)

_mappings = {}


def get_datasets(*, service=None):
    results = set()
    for key in _mappings:
        if isinstance(key, str):
            continue
        else:
            mapping_service, mapping_dataset = key
            if service is not None and service != mapping_service:
                continue
            results.add(mapping_dataset)
    return results


def require_mapper(key):
    if isinstance(key, str):
        if key not in _mappings:
            raise RuntimeError(f"No mapper found for service {key}.")
    else:
        if key not in _mappings:
            service, dataset = key
            raise RuntimeError(f"No mapper found for service {service} dataset {dataset}.")

    return _mappings[key]


def set_mapping(key, mapping):
    log.info(f"Mapping {key} to {mapping}.")
    _mappings[key] = mapping

