# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import mimetypes

def lookup_extension(mime_type):
    if mime_type == "image/jpeg":
        return ".jpg"
    return mimetypes.guess_extension(mime_type)


def lookup_type(path):
    return mimetypes.guess_type(path)[0]

