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


    def bboxes(self, index):
        """Return a list of bounding box annotations for an image.

        Parameters
        ----------
        index: int, required
            Index of the image.

        Returns
        -------
        bboxes: :class:`list`
            Sequence of :class:`dict`, one per bounding box.
            Each dict *must* have "left", "top", "width", "height",
            "category", and "color" keys.
        """
        return []


    @property
    def categories(self):
        """Return a list of existing categories for the collection.

        Returns
        -------
        categories: :class:`list`
            Sequence of :class:`str`, one per category, with a
            unique category name.
        """
        return []


    @abc.abstractmethod
    def get(self, index):
        """Return an image.

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


    def metadata(self, index):
        return {}


    @abc.abstractproperty
    @property
    def name(self):
        raise NotImplementedError()


    def put_bboxes(self, index, bboxes):
        return False


    def put_tags(self, index, tags):
        return False


    @property
    def service(self):
        return "image-collection"


    def tags(self, index):
        return []


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


    @property
    def categories(self):
        categories = self._coco.loadCats(self._coco.getCatIds())
        return sorted([category["name"] for category in categories])


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
        return sorted(list(result))


class Directory(ImageCollection):
    def __init__(self, *, name, root, pattern=".*\.(png|jpg|jpeg|PNG|JPG|JPEG)"):
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


    def get(self, index):
        return self._paths[index]


    @property
    def name(self):
        return self._name


    def tags(self, index):
        path = os.path.relpath(self._paths[index], self._root)
        tag = os.path.dirname(path)
        return [tag] if tag else []


class ImageNet(ImageCollection):
    def __init__(self, *, name, root, split):
        self._name = name
        self._root = root
        self._split = split
        self._update()

    def _update(self):
        import torchvision.datasets
        self._dataset = torchvision.datasets.ImageNet(root=self._root, split=self._split)


    def __len__(self):
        return len(self._dataset)


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(root={self._root!r}, split={self._split!r})"


    def get(self, index):
        image, category_index = self._dataset.imgs[index]
        return image


    @property
    def name(self):
        return self._name


    def tags(self, index):
        image, category_index = self._dataset.imgs[index]
        categories = self._dataset.classes[category_index]
        return sorted(list(categories))


