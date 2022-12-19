# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Backends to integrate Limbo datasets with the dashboard.
"""

import hashlib

import samlab.dashboard.backend.images


class ImageCollection(samlab.dashboard.backend.images.ImageCollection):
    """:any:`ImageCollection` backend for visualizing a :ref:`specification` dataset in the Samlab Dashboard.

    Parameters
    ----------
    name: :class:`str`, required
        Unique identifier for this backend instance.
    dataset: :class:`limbo.data.Dataset`, required
        Limbo dataset to be visualized.
    readonly: :class:`bool`, optional
        If :any:`True`, no changes to the dataset will be allowed.
        Includes changes to bounding boxes and tags.
    """
    def __init__(self, *, name, dataset, readonly=True):
        self._name = name
        self._dataset = dataset
        self._readonly = readonly


    def __len__(self):
        return len(self._dataset)


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(name={self._name!r}, dataset={self._dataset!r}, readonly={self._readonly})"


    def bboxes(self, index):
        """Return bounding box annotations applied to the image with the given index.

        Parameters
        ----------
        index: :class:`int`, required
            Index of the image.

        Returns
        -------
        bboxes: :class:`list` of :class:`dict`
            Sequence of bounding boxes.  Each box is a dict containing "left",
            "top", "width", "height", "category", and "color" values.  The
            bounding box position and size values are measured in absolute
            pixels.  The color value is a string containing a CSS-compatible
            color specification.
        """
        colors = ["red", "orange", "yellow", "green", "cyan", "blue", "purple"]
        sample = self._dataset[index]
        results = []
        for annotation in sample.metadata.get("annotations", []):
            if "bbox" not in annotation:
                continue

            left, top, width, height = annotation["bbox"]
            category = annotation["category"] or ""
            color_index = int(hashlib.sha256(category.encode("utf8")).hexdigest(), 16) % len(colors)
            color = colors[color_index]
            results.append({"left": left, "top": top, "width": width, "height": height, "category": category, "color": color, "username": None})
        return results


    def get(self, index):
        """Return the image with the given index.

        Parameters
        ----------
        index: :class:`int`, required
            Index of the image.

        Returns
        -------
        image: :class:`str`
            Absolute filesystem path of the image.
        """
        sample = self._dataset[index]
        return sample.image_path


    def metadata(self, index):
        """Return metadata for the image with the given index.

        Parameters
        ----------
        index: :class:`int`, required
            Index of the image.

        Returns
        -------
        metadata: :class:`dict`
            JSON-compatible, arbitrarily-nested dict of metadata information.
        """
        sample = self._dataset[index]
        return sample.metadata


    @property
    def name(self):
        """Unique identifier for this instance."""
        return self._name


    def put_bboxes(self, index, bboxes):
        """Set bounding box annotations for the image with the given index.

        Note that this overrides all bounding box annotations for the image.

        Parameters
        ----------
        index: :class:`int`, required
            Index of the image.
        bboxes: :class:`list` of :class:`dict`, required
            List of bounding boxes.  See :any:`bboxes` for details.

        Returns
        -------
        updated: :class:`bool`
            :any:`True` if the changes were saved, otherwise :any:`False`.
        """
        if self._readonly:
            return False
        sample = self._dataset[index]
        bboxes = [{"bbox":[bbox["left"], bbox["top"], bbox["width"], bbox["height"]], "bbox_mode":"XYWH_ABS", "category": bbox["category"]} for bbox in bboxes]
        not_bboxes = [annotation for annotation in sample.metadata["annotations"] if "bbox" not in annotation]
        sample.update_metadata({"annotations": bboxes + not_bboxes})
        return True


    def put_tags(self, index, tags):
        """Set tags for the image with the given index.

        Note that this overrides all tag annotations for the image.

        Parameters
        ----------
        index: :class:`int`, required
            Index of the image.
        tags: :class:`list` of :class:`str`, required
            List of categories that will apply to the image as a whole.

        Returns
        -------
        updated: :class:`bool`
            :any:`True` if the changes were saved, otherwise :any:`False`.
        """
        if self._readonly:
            return False
        sample = self._dataset[index]
        tags = [{"category": str(tag)} for tag in tags]
        not_tags = [annotation for annotation in sample.metadata["annotations"] if "bbox" in annotation or "contours" in annotation]
        sample.update_metadata({"annotations": tags + not_tags})
        return True


    def tags(self, index):
        """Return tags for the image with the given index.

        Parameters
        ----------
        index: :class:`int`, required
            Index of the image.

        Returns
        -------
        tags: :class:`list` of :class:`str`
            Sequence of categories that apply to the image as a whole.
        """
        sample = self._dataset[index]
        annotations = sample.metadata.get("annotations", [])
        annotations = [annotation for annotation in annotations if "bbox" not in annotation]
        annotations = [annotation for annotation in annotations if "contours" not in annotation]
        return sorted(list({annotation["category"] for annotation in annotations}))

