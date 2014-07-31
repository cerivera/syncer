import sh
import argparse
import github
import sys
import getpass
import json
from path import path
from constants import *

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=[PULL, PUSH, DISCONNECT, TRACK, UNTRACK])
args = parser.parse_args()

syncer_dir = path.expand(path('~/.syncer'))

def ensure_syncer_dir():
    if path.isdir(syncer_dir):
        return

    username = input('GitHub username: ')
    password = getpass.getpass('GitHub password: ')
    repo_exists = github.check_repo_exists(username, SYNCER_REPO_NAME)

    if not repo_exists:
        print("Creating new repo in GitHub")
        github.create_public_repo(username, password, SYNCER_REPO_NAME)
        # TODO need to create scaffolding for syncer dir (manifest, content/, backups/)

    print("Cloning GitHub repo.")
    sh.git('clone', 'https://%s:%s@github.com/%s/%s.git' % (username, password, username, SYNCER_REPO_NAME), syncer_dir)

    sh.cd(syncer_dir)
    if not path.isfile(path('manifest.json')):
        with open('manifest.json', 'w') as manifest_file:
            manifest_file.write('{}')
    
    if not path.isdir(path('content')):
        sh.mkdir('content')

    if not path.isdir(path('backup')):
        sh.mkdir('backup')

    if not path.isfile(path('.gitignore')):
        with open('.gitignore', 'w') as gitignore_file:
            gitignore_file.write('backup')



if args.command in PULL:
    ensure_syncer_dir()
#    sh.cd(syncer_dir)
#    sh.git('pull', 'origin', 'master')

    
    # TODO iterate manifest and copy files around.  Save backup if nothing in backup for that key

elif args.command == TRACK:
    ensure_syncer_dir()
    sh.cd(syncer_dir)
    # TODO put new key and files in manifest.  copy contents into content and save local backup if nothing there right now. 
    
elif args.command == UNTRACK:
    pass
    # TODO remove record from manifest and udpate manifest. 
elif args.command == LIST:
    ensure_syncer_dir()
    # TODO list all keys from manifest
elif args.command == PUSH:
    if not path.isdir(syncer_dir):
        print("Nothing to push.")
        sys.exit()
    else:
        # TODO assuming symlinks
        # If not, we need to copy the code to content and push it back out.  
        sh.cd(syncer_dir)
        sh.git('add', '*')
        sh.git('commit', '-am', 'Pushing new config.')
        sh.git('push', 'origin', 'master')
        print("Pushed latest config")

elif args.command == DISCONNECT:
    #TODO iterate all keys and replace files (if there's a backup)
    # remove ~/.syncer
    print("disconnecting from syncer")

