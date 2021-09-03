# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Integration with Jupyter notebooks."""

import logging

import IPython.display


log = logging.getLogger(__name__)


def gallery(paths, captions=None, row_height="auto"):
    if captions is None:
        captions = [None] * len(paths)

    content = []
    content.append("<div style='display: flex; flex-flow: row wrap; text-align: center;'>")
    for path, caption in zip(paths, captions):
        content.append(f"<a href='{path}' target='_blank'>")
        content.append(f"<figure style='margin: 5px'>")
        content.append(f"<image title='{path}' src='{path}' style='height: {row_height}'/>")
        if caption:
            content.append(f"<figcaption>{caption}</figcaption>")
        content.append(f"</figure>")
        content.append(f"</a>")
    content.append("</div>")

    return IPython.display.HTML("".join(content))


class Progress(object):
    """Display a graphical progress bar while iterating over a sequence."""
    def __init__(self, desc=None, unit=None):
        import tqdm.notebook
        self._progress = tqdm.notebook.tqdm(desc=desc, unit=unit)

    def __call__(self, iterable, desc=None, unit=None):
        self._progress.reset(total=len(iterable))
        if desc is not None:
            self._progress.set_description(desc, refresh=False)
        if unit is not None:
            self._progress.unit = unit
        self._progress.refresh()

        for item in iterable:
            yield item

            self._progress.update(1)
            self._progress.refresh()

