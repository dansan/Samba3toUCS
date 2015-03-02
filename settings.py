# encoding: utf-8

logfile = "s3toucs.log"
ldiffile = "test.ldif"
rootdn = "dc=itck,dc=edu,dc=af"


def groups():
    """
    Not a plain variable, so that if rootdn gets overwritten in local_settings, groups is "updated" too.
    """
    return "ou=Groups," + rootdn


def users():
    return "ou=Users," + rootdn


def computers():
    return "ou=Computers," + rootdn

# overwrite default settings
from local_settings import *
