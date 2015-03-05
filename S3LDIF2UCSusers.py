# encoding: utf-8
"""
Samba3toUCS -- import users and groups from a Samba3 environment into UCS 3.2

main is the start module.
"""

import subprocess
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
        self.user_container = str()
        self.group_container = str()
        self.computer_container = str()
        super(S3LDIF2UCSusers, self).__init__(*args, **kwargs)

    def handle(self, dn, entry):
        logger.debug("dn: '%s' entry: '%s'", dn, entry)
        try:
            if dn.endswith(settings.old_groups) and "posixGroup" in entry["objectClass"]:
                self.groups[dn] = entry
            elif (dn.endswith(settings.old_users) or dn.endswith(settings.old_computers)) and \
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

    @staticmethod
    def _mkpw(pw_length=10):
        pw = subprocess.check_output(["/usr/bin/makepasswd", "--minchars=%d" % pw_length]).strip("\n")
        assert len(pw) == pw_length
        return pw

    def locate_target_containers(self):
        try:
            default_containers = subprocess.check_output(["/usr/sbin/udm", "settings/directory", "list"])
        except Exception, e:
            logger.exception("Reading default containers.")
            raise e

        for def_c in default_containers.split("\n"):
            df = def_c.strip()
            if df.startswith("users:"):
                self.user_container = df.split()[-1]
            elif df.startswith("groups:"):
                self.group_container = df.split()[-1]
            elif df.startswith("computers: cn=computers"):
                self.computer_container = df.split()[-1]

    def create_groups(self):
        """
        Create not-existing groups except those in settings.black_lists["groups"], returns existing, not-added groups.

        :return: dict
        """
        pass

    def create_users(self):
        """
        Create not-existing users except those in settings.black_lists["users"], returns existing, not-added users.

        :return: dict
        """
        counter = 0
        created = 0
        existed = 0
        failed = 0
        blacklisted = 0
        passwords_txt = open("passwords.txt", "wb")

        for dn, entry in self.users.items():
            counter += 1
            if entry["uid"][0] in settings.black_lists["users"]:
                logger.info("%04d/%04d omitting blacklisted user '%s'.", counter, len(self.users), dn)
                blacklisted += 1
                continue
            try:
                out = subprocess.check_output(["udm", "users/user", "list", "--filter", "username=" + entry["uid"][0]])
            except subprocess.CalledProcessError, cpe:
                logger.exception("Looking for existence of user '%s', error code: %d, output: '%s'", "TEST",
                                 cpe.returncode, cpe.output)
            if len(out.split("\n")) > 2:
                logger.info("%04d/%04d not adding existing user '%s'", counter, len(self.users), dn)
                existed += 1
                continue
            pw = self._mkpw()
            logger.info("%04d/%04d adding user '%s' with password '%s'", counter, len(self.users), dn, pw)
            try:
                firstname = " ".join(entry["cn"][0].split()[0:-1])
            except:
                firstname = ""
            try:
                lastname = entry["cn"][0].split()[-1]
            except:
                lastname = ""
            try:
                profilepath = entry["sambaProfilePath"][0]

            except:
                profilepath = ""

            try:
                out = subprocess.check_output(["udm", "users/user", "create",
                                               "--position=" + self.user_container,
                                               "--set", "username=" + entry["uid"][0],
                                               "--set", "firstname=" + firstname,
                                               "--set", "lastname=" + lastname,
                                               "--set", "password=" + pw,
                                               "--set", "profilepath=" + profilepath,
                                               "--set", "sambahome=" + entry["sambaHomePath"][0],
                                               "--set", "unixhome=" + entry["homeDirectory"][0],
                                               "--set", "gecos=%s %s" % (firstname, lastname),
                                               "--set", "displayName=%s %s" % (firstname, lastname),
                                               "--set", "description=added by S3LDIF2UCSusers"])
                logger.debug("out: '%s'", out)
                created += 1
                passwords_txt.write('"%s", "%s"\n' % (entry["uid"][0], pw))
            except subprocess.CalledProcessError, cpe:
                logger.exception("Creating user '%s', error code: %d, output: '%s'", "TEST", cpe.returncode, cpe.output)
                failed += 1
        logger.info("Total: %d, created: %d, existed: %d, failed: %d, blacklisted: %d", len(self.users), created,
                    existed, failed, blacklisted)
        passwords_txt.close()

    def create_computers(self):
        """
        Create not-existing computers except those in settings.black_lists["computers"], returns existing,
        not-added computers.

        :return: dict
        """
        pass
