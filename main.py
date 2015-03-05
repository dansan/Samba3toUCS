#!/usr/bin/env python
# encoding: utf-8
"""
Samba3toUCS -- import users and groups from a Samba3 environment into UCS 3.2

main is the start module.
"""

import sys
import logging

import ldap

import settings
from S3LDIF2UCSusers import S3LDIF2UCSusers

__all__ = []
__version__ = 0.1
__date__ = '2015-03-01'
__updated__ = '2015-03-01'

__author__ = "Daniel Tröder"
__copyright__ = "2015, Daniel Tröder"
__credits__ = ["Daniel Tröder"]
__license__ = "GPLv3"
__maintainer__ = "Daniel Tröder"
__email__ = "daniel@admin-box.com"
__status__ = "Development"

DEBUG = 0

logger = logging.getLogger()


def main():  # IGNORE:C0111
    setup_logging()

    logger.info("** STARTING **")
    logger.debug("python-ldap version %s", ldap.__version__)
    logger.debug("Configuration: %s", {"logfile": settings.logfile, "ldiffile": settings.ldiffile, "old_rootdn":
        settings.old_rootdn, "old_groups": settings.old_groups, "old_users": settings.old_users, "old_computers":
        settings.old_computers})

    parser = S3LDIF2UCSusers(open(settings.ldiffile, "rb"))
    parser.parse()
    parser.locate_target_containers()

    logger.info("Found %d groups, %d users and %d computers", len(parser.groups), len(parser.users),
                len(parser.computers))
    logger.debug("Found groups:\n    %s", "\n    ".join(parser.groups))
    logger.debug("Found users:\n    %s", "\n    ".join(parser.users))
    logger.debug("Found computers:\n    %s", "\n    ".join(parser.computers))
    logger.debug("Found target containers:\n    user: %s\n    group: %s\n    computer: %s", parser.user_container,
                 parser.group_container, parser.computer_container)

    parser.create_groups()
    parser.create_users()
    parser.create_computers()

    return 0


def setup_logging():
    """
    Log with level DEBUG to logfile and level INFO to terminal.

    :return: None
    """
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-5s  %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    fh = logging.FileHandler(settings.logfile)
    formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-5s %(module)s.%(funcName)s:%(lineno)d  %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(fh)


if __name__ == "__main__":
    sys.exit(main())
