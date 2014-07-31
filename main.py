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

    print("Cloning GitHub repo.")
    sh.git('clone', 'https://%s:%s@github.com/%s/%s.git' % (username, password, username, SYNCER_REPO_NAME), syncer_dir)

    needs_commit = False
    sh.cd(syncer_dir)
    if not path.isfile(path('manifest.json')):
        sh.touch('manifest.json')
    
    if not path.isdir(path('content')):
        sh.mkdir('content')

    if not path.isdir(path('backup')):
        sh.mkdir('backup')

    if not path.isfile(path('.gitignore')):
        needs_commit = True
        with open('.gitignore', 'w') as gitignore_file:
            gitignore_file.write('backup')

    if needs_commit:
        sh.git('add', '-A')
        sh.git('commit', '-m', 'Setting up scaffolding.')


if args.command in PULL:
    ensure_syncer_dir()
    sh.cd(syncer_dir)
    sh.git('pull', 'origin', 'master')

    with open(path('manifest.json', 'r')) as manifest_file:
        json_data = json.load(manifest_file) 
        for key, paths in json_data.items():
            backup_base_path = syncer_dir + path('/backup/%s' % key)
            content_base_path = syncer_dir + path('/content/%s' % key)

            if not path.exists(backup_base_path):
                sh.mkdir(backup_base_path)

            for fs_path in paths:
                backup_path = backup_base_path + fs_path.replace('~', '.')
                content_path = content_base_path + fs_path.replace('~', '.')

                # save a backup first
                if not path.exists(backup_path):
                    sh.cp('-r', fs_path, backup_path)

                # create symlink from content_path to fs_path
                sh.ln('-s', content_path, fs_path) 

    # TODO iterate manifest and copy files around.  Save backup if nothing in backup for that key

elif args.command == TRACK:
    ensure_syncer_dir()
    sh.cd(syncer_dir)

    key = 'special_config'
    ps = ['~/.special_config_file']

    json_data = {}
    with open(path('manifest.json'), 'r') as manifest_file:
        try:
            json_data = json.load(manifest_file)
        except:
            json_data = {}

    json_data[key] = ps
    with open(path('manifest.json'), 'w') as manifest_file:
        manifest_file.write(json.dumps(json_data))

    content_base_path = syncer_dir + path('/content/%s' % key)

    if not path.exists(content_base_path):
        sh.mkdir(content_base_path)

    for p in ps:
        content_path = content_base_path + '/' + p.replace('~', '.')
        sh.cp('-r', path.expand(path(p)), content_path)  

    sh.git('add', '-A')
    sh.git('commit', '-m', 'Tracking %s' % key)
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
        sh.git('push', 'origin', 'master')
        print("Pushed latest config")

elif args.command == DISCONNECT:
    #TODO iterate all keys and replace files (if there's a backup)
    # remove ~/.syncer
    print("disconnecting from syncer")

