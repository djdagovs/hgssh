#!/usr/bin/env python
#
# Copyright 2005-2007 by Intevation GmbH <intevation@intevation.de>
#
# Author(s):
# Thomas Arendsen Hein <thomas@intevation.de>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# This script is based on the original hg-ssh and also hgssh2.py
#
# hgssh3.py - modified by <chaubner@chrishaubner.com>
#
"""
hgssh3.py - a wrapper for ssh access to mercurial repositories

To be used in ~/.ssh/authorized_keys with the "command" option, see sshd(8):
command="hgssh3 username /path/to/acl_file" ssh-rsa ...
(probably together with these other useful options:
no-port-forwarding,no-X11-forwarding,no-agent-forwarding)

This allows pull/push over ssh from/to repositories based on the username given as arguments with the ssh command.

If all your repositories are subdirectories of a common directory, you can
allow shorter paths with:
command="cd path/to/my/repositories && hgssh3 username /path/to/acl_file"

*******************
ACL_file format:

[myrepo1]
location=relative/path/to/repo #This is relative to the cwd (Current working directory) and cwd will default to ~/ unless changed using 'cd /path/to/repo &&' before calling the python script.
user1=write #Read/Write access
user2=read  #Read only access

[myrepo2]
location = relative/path/to/repo
user1=read
user4=read
user3=write


#Real example with 'repos' directory in the ~/ directory of the user (i.e. hg). User would check out as ssh://hg@my.server/project1:
[project1]
location=repos/customer1/project1
user1=write
user2=read


*********************
If the username provided in authorized_keys does not exist in the ACL file, or if it is set to anything
other than 'read' or 'write' (even if blank), then the access will be denied.

NOTE: The users defined in the ACL file DO NOT need to exist on the server being accessed. They simply need to match
      the entry that is provided in the command in the authorized_keys file for that user.

NOTE: The actual name of the repository folder in the location DOES NOT need to match the name in the [] section of the ACL file.
Example:
[repo1]
location=/path/to/repos/anothername
user1=read
user2=write

This script allows the use of 'short/friendly' names in access/config:
Example: ssh://hg@hg.myserver.com/myrepo1

This repository could actually live under ~/relative/path/to/repos/myrepo1. This ACL file serves as
a mapping from friendly name to actual location. This removes the need to defined multiple repo definitions
on the "command" of the ssh key as in hgssh, and also removes the need to redefine repos per user as in hgssh2.py.
This configuration allows one definition of the repository and one line per user to deny/grant access. This is very similar
to how SVN grants access controls.


"""

# Enable importing on demand to reduce startup time
# Please ensure the PYTHONPATH is correct to allow the site-packages
# folder that contains mercurial to be accessed so these imports work.
from mercurial import demandimport; demandimport.enable()
from mercurial import dispatch

import sys, os, shlex
import ConfigParser

def get_permission(repository,conf):

    #return a dict like the following for the 'repository' section for all users:
    #permission = {'user1': 'write','user2': 'read'}
    config = ConfigParser.SafeConfigParser()
    config.optionxform = str
    config.read(conf)

    if config.has_section(repository):
        return dict(config.items(repository))
    return {}

def main():
    cwd = os.getcwd()
    user = sys.argv[1]
    conf = sys.argv[2]

    # Get the original SSH Command sent through. The repo should be the item after the connect string
    orig_cmd = os.getenv('SSH_ORIGINAL_COMMAND', '?')

    try:
        cmdargv = shlex.split(orig_cmd)

    # Changed to "as" here for Python 3.3 compatibility
    except ValueError as e:
        sys.stderr.write('Illegal command "%s": %s\n' % (orig_cmd, e))
        sys.exit(255)

    if cmdargv[:2] == ['hg', '-R'] and cmdargv[3:] == ['serve', '--stdio']:
        try:

            # Now we need to extract the repository name (what is in the conf file)
            repository = cmdargv[2].replace(os.sep,'',1)

            # Get the repository and users from the config file (or get a blank {})
            perms = get_permission(repository,conf)

            # If the returned dict is empty, then exit this process. This means no section with
            # the named repository exist!
            if not len(perms):
                sys.stderr.write('No repository found for "%s"\n' % repository)
                sys.exit(255)

            # This is the reason we are using a try in case this key does not exist.
            # 'location' param under repository section contains the relative or absolute path
            # to the repository on the file system from the current working
            # directory which can be changed in the authorized_keys
            path = perms['location']

            # Get the path of the repository to be used with hg commands below.
            # This is the translation between the section name in the conf file and
            # the location param that points to the actual directory on the file system
            # By default, this uses cwd (Current working directory) and can be changed in the
            # authorized_keys file in the command section by using 'cd /path/to/start/from && '
            # as the first part of the command string before calling this script.
            repo = os.path.normpath(os.path.join(cwd, os.path.expanduser(path)))

        except KeyError:
            sys.stderr.write('Invalid Repository "%s"\n' % repository)
            sys.exit(255)

        # We will try and get the username out of the config, if it is not present, we exit!
        # We will also check to make sure the access is set to read or write. If Not, goodbye!
        try:
            access = perms[user]
        except:
            sys.stderr.write('Illegal Repository "%s"\n' % repo)
            sys.exit(255)

        # If the user does not have read or write (write implies read) we exit.
        if access not in ['read','write']:
            sys.stderr.write('Access denied to "%s"\n' % repository)
            sys.exit(255)

        cmd = ['-R', repo, 'serve', '--stdio']
        if access == "read":
            cmd += [
                '--config',
                'hooks.prechangegroup.hg-ssh=python:__main__.rejectpush',
                '--config',
                'hooks.prepushkey.hg-ssh=python:__main__.rejectpush'
                ]

        dispatch.dispatch(dispatch.request(cmd))

    else:
        sys.stderr.write('Illegal command "%s"\n' % orig_cmd)
        sys.exit(255)

def rejectpush(ui, **kwargs):
    ui.warn("Permission denied\n")
    # mercurial hooks use unix process conventions for hook return values
    # so a truthy return means failure
    return True

if __name__ == '__main__':
    main()
