# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

#import gridfs

#import samlab.database

# Get the web server.
from samlab.web.app import application

# This is just so we can build the documentation
database = None
fs = None

## Create the database connection.
#if "database-name" in application.config and "database-uri" in application.config and "database-replicaset" in application.config:
#    database, fs = samlab.database.connect(
#        name=application.config["database-name"],
#        uri=application.config["database-uri"],
#        replicaset=application.config["database-replicaset"],
#        )

