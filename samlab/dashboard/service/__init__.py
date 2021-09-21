# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

_mappings = {}

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
    _mappings[key] = mapping
