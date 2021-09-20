# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

mappings = {}

def require_mapping(key):
    if key not in mappings:
        raise RuntimeError(f"Unknown mapping: {key}")
    return mappings[key]
