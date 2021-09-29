# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging
import traceback

log = logging.getLogger(__name__)


class LDAP(object):
    """Check credentials against an LDAP server."""
    def __init__(self, server, user_dn, timeout=5):
        self.server = server
        self.user_dn = user_dn
        self.timeout = timeout

    def __call__(self, authorization):
        if not authorization:
            return False
        try:
            search_dn = self.user_dn.format(authorization.username)
            log.info("Checking credentials for %s with %s.", search_dn, self.server)

            import ldap3
            ldap_server = ldap3.Server(self.server, use_ssl=True)
            connection = ldap3.Connection(ldap_server, user=search_dn, password=authorization.password, receive_timeout=self.timeout)
            if not connection.bind():
                log.warning("Credential check failed.")
                return False
            return True
        except Exception:
            log.error("%s" % traceback.format_exc())
            return False


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(server={self.server!r}, user_dn={self.user_dn!r}, timeout={self.timeout!r})"


class ExactMatch(object):
    """Allow credentials that match the given username and password."""
    def __init__(self, username="test", password="test"):
        self.username = username
        self.password = password


    def __call__(self, authorization):
        if not authorization:
            return False
        return authorization.username == self.username and authorization.password == self.password


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}(username={self.username!r}, password={self.password!r})"


class ForbidAll(object):
    """Forbid all credentials."""
    def __call__(self, authorization):
        return False


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}()"


class PermitAll(object):
    """Permit all non-empty credentials."""
    def __call__(self, authorization):
        return True if authorization else False


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}()"


class PermitAny(object):
    """Permit any credentials, including empty."""
    def __call__(self, authorization):
        return True


    def __repr__(self):
        return f"{self.__class__.__module__}.{self.__class__.__name__}()"


