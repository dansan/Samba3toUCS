# encoding: utf-8

logfile = "s3toucs.log"
ldiffile = "test.ldif"

old_rootdn = "dc=itck,dc=edu,dc=af"
old_groups = "ou=Groups," + old_rootdn
old_users = "ou=Users," + old_rootdn
old_computers = "ou=Computers," + old_rootdn

# overwrite default settings
from local_settings import *
