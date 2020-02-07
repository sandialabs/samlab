# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Integration with Jupyter notebooks."""

import logging

import IPython.display


log = logging.getLogger(__name__)


def gallery(images, row_height="auto"):
    content = []
    content.append("<div style='display: flex; flex-flow: row wrap; text-align: center;'>")
    for image in images:
        content.append(f"<a href='{image}' target='_blank'><figure style='margin: 5px'><image title='{image}' src='{image}' style='height: {row_height}'/></figure></a>")
    content.append("</div>")

    return IPython.display.HTML("".join(content))

