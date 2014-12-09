#!/bin/bash
#
# This script will create a merurial repository.
# author: robert tulke, rt@debian.sh 12.2014
##

REPOUSER=repo
REPOPATH=/home/repo                     # path to repository folder
REPONAME=$1                             # given repository name
DIRECTORY="$REPOPATH/$REPONAME"         # full path

## if the repository name is not given, then
if [ -z $1 ]; then
    echo "Usage: addrepo myproject1"
    echo "This script will create a mercurial repository to [$REPOPATH]"
    echo
    echo -n "Please choose a name for your repository: "
    read REPONAME

    ## check if a string contains white spaces
    if [[ $REPONAME = *[[:space:]]* ]]; then
        echo "ERROR: Your repository name contains a whitespace."
        exit 1
    fi

    DIRECTORY="$REPOPATH/$REPONAME"
fi

## if repo directory exist, then
if [ ! -d "$DIRECTORY" ]; then
    sudo -u $REPOUSER mkdir -pv $REPOPATH/$REPONAME
    sudo -u $REPOUSER hg init $REPOPATH/$REPONAME
    echo "[$REPONAME]" >>$REPOPATH/hgssh3.conf
    echo "location = $REPOPATH/$REPONAME" >>$REPOPATH/hgssh3.conf
    echo >>$REPOPATH/hgssh3.conf
    exit 0
else
    echo "ERROR: the directory [$DIRECTORY] is already exists... you must choose another repository name"
    exit 1
fi
