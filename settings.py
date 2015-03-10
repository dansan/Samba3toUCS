# encoding: utf-8

logfile = "s3toucs.log"
ldiffile = "test.ldif"

old_rootdn = "dc=itck,dc=edu,dc=af"
old_groups = "ou=Groups," + old_rootdn
old_users = "ou=Users," + old_rootdn
old_computers = "ou=Computers," + old_rootdn
black_lists = {"users": ["Administrator", "nobody"],
               "groups_create": ["Domain Admins", "Domain Users", "Domain Guests", "Domain Computers",
                                 "Administrators", "Print Operators", "Replicators", "Backup Operators"],
               "groups_add_users": ["Domain Admins", "Domain Users", "Domain Guests", "Domain Computers",
                                    "Administrators", "Print Operators", "Replicators", "Backup Operators"],
               "computers": []}

# overwrite default settings
from local_settings import *
