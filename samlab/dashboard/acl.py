# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.


class ForbidAll(object):
    """Access control list strategy that prevents anyone from doing anything."""
    def __call__(self, authorization, requested):
        return False


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}()"


class List(object):
    """Access control list strategy based on lists of usernames."""
    def __init__(self, **permissions):
        self.permissions = permissions

    def __call__(self, authorization, requested):
        if authorization is None:
            return False
        for permission in requested:
            if permission not in self.permissions:
                return False
            if authorization.username not in self.permissions[permission]:
                return False
        return True


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(permissions={self.permissions!r})"


class PermitAll(object):
    """Access control list strategy that allows anyone to do anything.
    """
    def __call__(self, authorization, requested):
        return True


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}()"


