# encoding: utf-8
"""
Samba3toUCS -- import users and groups from a Samba3 environment into UCS 3.2

main is the start module.
"""

import logging

from ldif import LDIFParser

import settings

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

logger = logging.getLogger()


class S3LDIF2UCSusers(LDIFParser, object):
    def __init__(self, *args, **kwargs):
        self.users = dict()
        self.groups = dict()
        self.computers = dict()
        super(S3LDIF2UCSusers, self).__init__(*args, **kwargs)

    def handle(self, dn, entry):
        logger.debug("dn: '%s' entry: '%s'", dn, entry)
        try:
            if dn.endswith(settings.groups()) and "posixGroup" in entry["objectClass"]:
                self.groups[dn] = entry
            elif (dn.endswith(settings.users()) or dn.endswith(settings.computers())) and \
                            "posixAccount" in entry["objectClass"]:
                if entry["cn"][0].endswith("$") and "W" in entry["sambaAcctFlags"][0]:
                    self.computers[dn] = entry
                else:
                    self.users[dn] = entry
            else:
                pass
        except KeyError, ke:
            logger.exception("KeyError when looking at dn: '%s', entry: '%s'.", dn, entry)
        except Exception:
            logger.exception("Unknown Error when looking at dn: '%s', entry: '%s'.", dn, entry)
