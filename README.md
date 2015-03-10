Samba3toUCS
===========

Import users and groups from a Samba3 environment into UCS 3.2.

This software is written specifically for the university of Kabuls migration of a Samba3 system to a Univention
 Corporate Server. If you have use for it, you'll may have to adapt the LDAP node names. Overwrite them in 
 `local_settings.py`.

Computer accounts are searched in both the settings.users path and in settings.computers.

The DomainSID is not preserved - so all users will be new users (with the same username) and thus will get a fresh 
profile the next time they login! Application settings may or may not be preserved - depends on the applications.

Usage
=====

1. `virtualenv s3toucs && source s3toucs/bin/activate && pip install -r requirements.txt`
2. Create `local_settings.py` and copy the configuration variables you have to change from `settings.py` into it and 
adapt them. All variables from `settings.py` will be overwritten by those in `local_settings.py`.
3. run: `(s3toucs) ./main.py`

Dependencies
============

- python-ldap

Testing / Removal of added users and groups
===========================================
To remove users and groups added by this script, run in a terminal as root:

```Shell
for UnID in $(udm users/user list --filter "description=added by S3LDIF2UCSusers" \
 | grep uidNumber | cut -f 2 -d ':' | cut -f 2 -d ' ');
do udm users/user remove --filter uidNumber=$UnID;
done

for GrID in $(udm groups/group list --filter "description=added by S3LDIF2UCSusers" \
 | grep gidNumber | cut -f 2 -d ':' | cut -f 2 -d ' ');
do udm groups/group remove --filter gidNumber=$GrID;
done
```