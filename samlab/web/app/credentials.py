# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

import logging
import traceback

import flask

log = logging.getLogger(__name__)


def fail_all():
    def implementation(authorization):
        return False
    return implementation


def pass_all():
    def implementation(authorization):
        return True
    return implementation


def check_ldap(server, user_dn, timeout=5):
    def implementation(authorization):
        if not authorization:
            return False
        log.info("Checking credentials for %s with %s.", authorization.username, server)
        try:
            search_dn = user_dn.format(authorization.username)

            import ldap3
            ldap_server = ldap3.Server(server, use_ssl=True)
            connection = ldap3.Connection(ldap_server, user=search_dn, password=authorization.password, receive_timeout=timeout)
            if not connection.bind():
                return False
            return True
        except Exception:
            log.error("%s" % traceback.format_exc())
            return False
    return implementation


def exact_match(username="test", password="test"):
    def implementation(authorization):
        if not authorization:
            return False
        return authorization.username == username and authorization.password == password
    return implementation


