Samba3toUCS
===========

Import users and groups from a Samba3 environment into UCS 3.2.

This software is written specifically for the university of Kabuls migration of a Samba3 system to a Univention
 Corporate Server. If you have use for it, you'll may have to adapt the LDAP node names.
 
The  LDAP tree is assumed to look like this:
```
root -> settings.ROOTDN
groups: ou=Groups,ROOTDN
users: ou=Users,ROOTDN
```
Computer accounts are searched in both the users path and in ou=Computers,ROOTDN.

Usage
=====

1. `virtualenv s3toucs && source s3toucs/bin/activate && pip install -r requirements.txt`
2. Create `local_settings.py` and copy the configuration variables you have to change from `settings.py` into it and 
adapt them. All variables from settings.py will be overwritten by those in local_settings.py.
3. run: `(s3toucs) ./main.py`

Dependencies
============

- python-ldap
