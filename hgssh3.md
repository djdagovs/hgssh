hgssh
=====

A Toolset to control ssh access to mercurial repositories and create users and repositorys.

Modified from hg-ssh (http://www.selenic.com/repo/hg-stable/raw-file/tip/contrib/hg-ssh) and hgssh2.py https://github.com/dengzhp/hgssh2 and a fork of hgssh3 https://bitbucket.org/painfulcranium/hgssh3

https://github.com/rtulke/hgssh/ for more information.

How to
------

copy hgssh3.py to your $PATH (e.g. /usr/local/bin).
chmod 755 /usr/local/bin/hgssh3.py

(We assume your user being created is named 'repo')

Create a new user `repo` with home directory `/home/repo`, all your repositories will go here. If 
you want to store your repositories elsewhere, you can do one of the following:

	1. Create your directory structure somewhere on your filesystem and ensure ownership
	  is given to hg user and hg group. Then create a symlink in the user home directory
	  to the top level folder of the repository location.
	   
	2. Use 'cd /home/repo/r &&...' in your SSH command before calling this script. For example,
	  if the top level was in /home/repo
     
    Create a config file at `/home/repo/hgssh3.conf`:
    [reponame]
    location = /home/repo/reponame
    user1 = read     
    user2 = write    
    
    [project_web]
    location = /home/repo/project_web
    user1 = write

Add a new entry to ``/home/repo/.ssh/authorized_keys``
    
    NOTE: USERNAME in this example would be user1 or user2
	
    command="hgssh3.py USERNAME ~/hgssh3.conf",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-rsa your_ssh_rsa_public_key

Create the repositories:

    su - repo
    cd /home/repo/project_web && hg init project_web 

Now you can access (only) these repositories using your ssh key:

    ssh://repo@example.com/reponame    (readonly to user1, read/write to user2)
    ssh://repo@example.com/project_web (read/write to user1only)
    
NOTES:

    If the username provided in authorized_keys does not exist in the ACL file, or if it is set to anything
    other than 'read' or 'write' (even if blank), then the access will be denied.
    *****

    The users defined in the ACL file DO NOT need to exist on the server being accessed. They simply need to match
    the entry that is provided in the command in the authorized_keys file for that user.
    *****

    The actual name of the repository folder in the location DOES NOT need to match the name in the [] section of the ACL file.
    [repo1]
    location=/home/repo/anothername
    user1=read
    user2=write

    SSH to run: ssh://repo@example.com/repo1
    *****

    This script allows the use of 'short/friendly' names in access/config:
    Example: ssh://repo@reposerver/project_web
    *****

    This ACL file serves as a mapping from friendly name to actual location. This removes the 
    need to defined multiple repo definitions on the "command" of the ssh key as in hgssh, 
    and also removes the need to redefine repos per user as in hgssh2.py. This configuration 
    allows one definition of the repository and one line per user to deny/grant access. This is very similar
    to how SVN grants access controls.
    *****
