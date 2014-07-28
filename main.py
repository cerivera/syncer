import argparse
import sh
import github
from path import path
from constants import *

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=[PULL, PUSH, DISCONNECT])
args = parser.parse_args()

syncer_dir = path.expand(path('~/.syncer'))

if path.isdir(syncer_dir):
    print("path exists")
else:
#    path.mkdir(syncer_dir)
    username = input('GitHub username: ')
    if github.check_repo_exists(username, SYNCER_REPO_NAME):
        print("GitHub repo exists")
    else:
        print("Need to create GitHub repo")

if args.command == PULL:
    print("pulling down synced files.")
elif args.command == PUSH:
    print("pushing up synced files")
elif args.command == DISCONNECT:
    print("disconnecting from syncer")
