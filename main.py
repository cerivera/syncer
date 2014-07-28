import sh
import argparse
import github
import sys
import getpass
from path import path
from constants import *

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=[PULL, PUSH, DISCONNECT])
args = parser.parse_args()

syncer_dir = path.expand(path('~/.syncer'))

if path.isdir(syncer_dir):
    sh.cd(synced_dir)
    sh.git('pull', 'origin', 'master')
else:
    username = input('GitHub username: ')
    password = getpass.getpass('GitHub password: ')
    repo_exists = github.check_repo_exists(username, SYNCER_REPO_NAME)

    if not repo_exists:
        print("Creating new repo in GitHub")
        github.create_public_repo(username, password, SYNCER_REPO_NAME)

    print("Cloning GitHub repo.")
    sh.git('clone', 'https://%s:%s@github.com/%s/%s.git' % (username, password, username, SYNCER_REPO_NAME), syncer_dir)

if args.command == PULL:
    print("pulling down synced files.")
elif args.command == PUSH:
    print("pushing up synced files")
elif args.command == DISCONNECT:
    #TODO iterate all keys and replace files (if there's a backup)
    # remove ~/.syncer
    print("disconnecting from syncer")

