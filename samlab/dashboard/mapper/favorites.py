# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Functionality for working with :ref:`favorites`."""

def create(database, otype, oid, name):
    """Mark an object as a favorite.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    otype: str, required
        Object type.  One of "observations", "experiments", "artifacts", or "layouts".
    oid: str, required.
        ID of the object to be favorited.
    name: str, required.
        Human-readable label for the favorite.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(otype, str))
    assert(isinstance(oid, str))
    assert(isinstance(name, str))

    database.favorites.update_many({"otype": otype, "oid": oid}, {"$set": {"otype": otype, "oid": oid, "name": name}}, upsert=True)


def delete(database, otype, oid):
    """Un-favorite an object.

    Parameters
    ----------
    database: database object returned by :func:`samlab.database.connect`, required
    otype: str, required
        Object type.  One of "observations", "experiments", "artifacts", or "layouts".
    oid: str, required.
        ID of the object to be un-favorited.
    """
    assert(isinstance(database, pymongo.database.Database))
    assert(isinstance(otype, str))
    assert(isinstance(oid, str))

    database.favorites.delete_many({"otype": otype, "oid": oid})
