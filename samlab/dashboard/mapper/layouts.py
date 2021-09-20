# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import hashlib
import json
import logging
import os

log = logging.getLogger(__name__)


class JSONDiskLayouts(object):
    def __init__(self, storage):
        self._storage = storage
        self._layouts = {}
        if os.path.exists(storage):
            try:
                with open(self._storage, "r") as stream:
                    self._layouts = json.load(stream)
            except Exception as e:
                log.error(f"Uncaught exception: {e}")


    def _save(self):
        with open(self._storage, "w") as stream:
            json.dump(self._layouts, stream)



    def get(self, *, lid):
        if lid in self._layouts:
            return self._layouts[lid]
        return None


    def store(self, *, content):
        if not isinstance(content, list):
            raise ValueError(f"Layout content must be a list, received {type(content)}.")

        lid = hashlib.md5(json.dumps(content, separators=(",",":"), indent=None, sort_keys=True).encode("utf-8")).hexdigest()

        if lid not in self._layouts:
            self._layouts[lid] = content
            self._save()

        return lid
