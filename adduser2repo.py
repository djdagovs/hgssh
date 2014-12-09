#!/usr/bin/env python

"""adduser2repo: add a user to hgssh3 configuration file."""

__author__      = "Robert Tulke, rt@debian.sh"
__copyright__   = "Copyright 2014, Robert Tulke"
__license__     = "GPL"
__version__     = "1.0.3"
__Modified_By   = "Rachit Gupta, rachit.gupta@berlin-airport.de"
__status__      = "Testing"

import ConfigParser, os, sys

config = ConfigParser.ConfigParser()
config.read("/home/repo/hgssh3.conf")

def get_permission(repository,conf):

    #return a dict like the following for the 'repository' section for all users:
    #permission = {'user1': 'write','user2': 'read'}
    config = ConfigParser.SafeConfigParser()
    config.optionxform = str
    config.read(conf)

    if config.has_section(repository):
        return dict(config.items(repository))
    return {}

## check parameter
if len(sys.argv) < 4:
    sys.exit('Usage: %s repositoryname username read|write' % sys.argv[0])

repo = sys.argv[1]
user = sys.argv[2]
perm = sys.argv[3]
path = "/home/repo"
repopath = path + repo

#perms = get_permission(repo,"/home/repo/hgssh3.conf")
#access = perms[user]
#if access not in [perm]:
#    config.set(repo, user, perm)
#    config.write(open("/home/repo/hgssh3.conf", "w"))

## check if repository section are already in there
if not config.has_section(repo):
    config.add_section(repo)
    config.set(repo,"location", path)
    print "section: %s added!" % repo
else:
   print "The section exit ..checking user ...."
   
## check if a user is in section already in there
if not config.has_option(repo, user):
    config.set(repo, user, perm)
    config.write(open("/home/repo/hgssh3.conf", "w"))
    print "user: %s added!" %user
else:
   print "The user %s already exist, checking permissions..." % user

## check the permission
perms = get_permission(repo,"/home/repo/hgssh3.conf")
access = perms[user]

if access not in [perm]:
    if perm in ['read','write']:
       config.set(repo, user, perm)
       config.write(open("/home/repo/hgssh3.conf", "w"))
       print "The permission is now changed to: %s" % perm
    else:
       print "The permission can only be read|write"
else:
  print "the permission is set"
