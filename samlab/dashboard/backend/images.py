# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import abc
import glob
import hashlib
import os
import re


class ImageCollection(abc.ABC):
    @abc.abstractmethod
    def __len__(self):
        """Return the number of images in the collection."""
        raise NotImplementedError()


    @abc.abstractmethod
    def bboxes(self, index):
        raise NotImplementedError()


    @abc.abstractmethod
    def get(self, index):
        """Return an image by index.

        Parameters
        ----------
        index: int, required
            The index of the image to return.

        Returns
        -------
        image: :class:`str`
            If :class:`str`, the filesystem path of the image.
        """
        raise NotImplementedError()


    @abc.abstractmethod
    def metadata(self, index):
        raise NotImplementedError()


    @abc.abstractproperty
    @property
    def name(self):
        raise NotImplementedError()


    @property
    def service(self):
        return "image-collection"


    @abc.abstractmethod
    def tags(self, index):
        raise NotImplementedError()


class COCO(ImageCollection):
    def __init__(self, *, name, annotations, images):
        self._name = name
        self._annotations = annotations
        self._images = images
        self._update()


    def _update(self):
        import pycocotools.coco
        self._coco = pycocotools.coco.COCO(self._annotations)
        self._indices = self._coco.getImgIds()


    def __len__(self):
        return len(self._indices)


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(annotations={self._annotations!r}, images={self._images!r})"


    def bboxes(self, index):
        colors = ["red", "orange", "yellow", "green", "cyan", "blue", "purple"]

        results = []
        annotations = self._coco.loadAnns(self._coco.getAnnIds(imgIds=self._indices[index]))
        for annotation in annotations:
            if "bbox" in annotation:
                category = self._coco.loadCats(annotation["category_id"])[0]["name"]
                color_index = int(hashlib.sha256(category.encode("utf8")).hexdigest(), 16) % len(colors)
                color = colors[color_index]
                left, top, width, height = annotation["bbox"]
                results.append({"left": left, "top": top, "width": width, "height": height, "category": category, "color": color, "username": None})
        return results

    def get(self, index):
        image = self._coco.loadImgs(self._indices[index])[0]
        return os.path.join(self._images, image["file_name"])


    def metadata(self, index):
        image = self._coco.loadImgs(self._indices[index])[0]
        return image


    @property
    def name(self):
        return self._name


    def tags(self, index):
        result = set()
        annotations = self._coco.loadAnns(self._coco.getAnnIds(imgIds=self._indices[index]))
        for annotation in annotations:
            category = self._coco.loadCats(annotation["category_id"])[0]
            result.add(category["name"])
        return list(result)


class Directory(ImageCollection):
    def __init__(self, *, name, root, pattern=".*\.(png|jpg|jpeg)"):
        self._name = name
        self._root = root
        self._pattern = pattern
        self._update()


    def _update(self):
        paths = []
        pattern = re.compile(self._pattern)
        for root, dirs, files in os.walk(self._root):
            for filename in files:
                if not pattern.match(filename):
                    continue
                paths.append(os.path.abspath(os.path.join(root, filename)))
        self._paths = paths


    def __len__(self):
        return len(self._paths)


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(root={self._root!r}, pattern={self._pattern!r})"


    def bboxes(self, index):
        return []


    def get(self, index):
        return self._paths[index]


    def metadata(self, index):
        return {}


    @property
    def name(self):
        return self._name


    def tags(self, index):
        path = os.path.relpath(self._paths[index], self._root)
        tag = os.path.dirname(path)
        return [tag] if tag else []

