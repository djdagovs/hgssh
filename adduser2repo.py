#!/usr/bin/env python

"""adduser2repo: add a user to hgssh3 configuration file."""

__author__      = "Robert Tulke, rt@debian.sh"
__copyright__   = "Copyright 2014, Robert Tulke"
__license__     = "GPL"
__version__     = "1.0.3"
__status__      = "Testing"

import ConfigParser, os, sys

cfgfile = "/home/repo/hgssh3.conf"

## main part
config = ConfigParser.ConfigParser()
config.read(cfgfile)

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

## check if repository section are already in there
if not config.has_section(repo):
    config.add_section(repo)
    config.set(repo,"location", path)
    print "repository: [%s] now added to %s!" % (repo, cfgfile)
else:
    print "repository: [%s] is already exist in %s!" % (repo, cfgfile)

## check if a user is in section already in there
if not config.has_option(repo, user):
    config.set(repo, user, perm)
    config.write(open(cfgfile, "w"))
    print "user: %s added to section repository [%s]" % (user, repo)
else:
    print "user: %s is already exist in section repository [%s]" % (user, repo)

## check the permission
perms = get_permission(repo, cfgfile)
access = perms[user]

if access not in [perm]:
    if perm in ['read','write']:
       config.set(repo, user, perm)
       config.write(open(cfgfile, "w"))
       print "the permission for user: %s is now changed to: %s" % (user, perm)
       print
       print "[%s]" % repo
       print "%s = %s" % (user, perm)
    else:
       print "the permission can only be read|write"
else:
    print "the permission for: %s is already set" % (user)
