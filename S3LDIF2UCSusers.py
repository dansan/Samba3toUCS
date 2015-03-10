# encoding: utf-8
"""
Samba3toUCS -- import users and groups from a Samba3 environment into UCS 3.2

main is the start module.
"""
from __builtin__ import enumerate

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
        Create not-existing groups except those in settings.black_lists["groups"], add users to (also pre-existing)
        groups.

        :return: None
        """
        logger.info("Starting to add groups.")
        created = 0
        existed = 0
        failed = 0
        blacklisted = 0
        for counter, (dn, entry) in enumerate(self.groups.items(), 1):
            cn = entry["cn"][0]
            if cn in settings.black_lists["groups_create"]:
                logger.info("%04d/%04d omitting blacklisted group '%s'.", counter, len(self.users), dn)
                blacklisted += 1
                continue
            try:
                out = subprocess.check_output(["udm", "groups/group", "list", "--filter", "name=" + cn])
            except subprocess.CalledProcessError, cpe:
                logger.exception("Looking for existence of group '%s', error code: %d, output: '%s'", cn,
                                 cpe.returncode, cpe.output)
                continue
            if len(out.split("\n")) > 2:
                logger.info("%04d/%04d not adding existing group '%s'", counter, len(self.users), dn)
                existed += 1
                continue
            logger.info("%04d/%04d adding group '%s'", counter, len(self.users), cn)
            try:
                out = subprocess.check_output(["udm", "groups/group", "create",
                                               "--position=" + self.group_container,
                                               "--set", "name=" + cn])
                logger.debug("out: '%s'", out)
                created += 1
            except subprocess.CalledProcessError, cpe:
                logger.exception("Creating group '%s', error code: %d, output: '%s'", cn, cpe.returncode,
                                 cpe.output)
                failed += 1
        logger.info("Done adding groups.")
        logger.info("Total: %d, created: %d, existed: %d, failed: %d, blacklisted: %d", len(self.groups), created,
                    existed, failed, blacklisted)

        logger.info("Starting to add users to groups.")
        for dn, entry in self.groups.items():
            cn = entry["cn"][0]
            if cn in settings.black_lists["groups_add_users"]:
                logger.info("Omitting user add for blacklisted group '%s'.", dn)
                continue
            if "memberUid" in entry and entry["memberUid"]:
                logger.info("Group: '%s' has %d members.", cn, len(entry["memberUid"]))
                logger.debug("Members '%s'.", entry["memberUid"])

                space_uids = [muid for muid in entry["memberUid"] if " " in muid]
                if space_uids:
                    logger.info("Not adding %d users with space in username: %s", len(space_uids), space_uids)

                members = " ".join(["--append users=uid=%s,%s" % (memberUid, self.group_container)
                                    for memberUid in entry["memberUid"] if memberUid not in space_uids]).split()
                cmd = ["udm", "groups/group", "modify", "--dn", "cn=%s,%s" % (cn, self.group_container)]
                cmd.extend(members)
                try:
                    out = subprocess.check_output(cmd)
                    logger.debug("out: '%s'", out)
                except subprocess.CalledProcessError, cpe:
                    logger.exception("Adding users to group '%s', error code: %d, output: '%s'", cn, cpe.returncode,
                                     cpe.output)
            else:
                logger.info("Group: '%s' has no members.", cn)
        logger.info("Done adding users to groups.")


    def create_users(self):
        """
        Create not-existing users except those in settings.black_lists["users"].

        :return: None
        """
        created = 0
        existed = 0
        failed = 0
        blacklisted = 0
        passwords_txt = open("passwords.txt", "wb")

        logger.info("Starting to add users.")
        for counter, (dn, entry) in enumerate(self.users.items(), 1):
            if entry["uid"][0] in settings.black_lists["users"]:
                logger.info("%04d/%04d omitting blacklisted user '%s'.", counter, len(self.users), dn)
                blacklisted += 1
                continue
            if " " in entry["uid"][0]:
                logger.info("Not adding user with space in username: '%s'", entry["uid"][0])
                failed += 1
                continue
            try:
                out = subprocess.check_output(["udm", "users/user", "list", "--filter", "username=" + entry["uid"][0]])
            except subprocess.CalledProcessError, cpe:
                logger.exception("Looking for existence of user '%s', error code: %d, output: '%s'", entry["uid"][0],
                                 cpe.returncode, cpe.output)
                continue
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
                logger.exception("Creating user '%s', error code: %d, output: '%s'", entry["uid"][0], cpe.returncode,
                                 cpe.output)
                failed += 1
        logger.info("Total: %d, created: %d, existed: %d, failed: %d, blacklisted: %d", len(self.users), created,
                    existed, failed, blacklisted)
        passwords_txt.close()
        logger.info("Done adding users.")

    def create_computers(self):
        """
        Create not-existing computers except those in settings.black_lists["computers"],
        not-added computers.

        :return: None
        """
        pass
