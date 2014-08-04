import sh
import argparse
import github
import sys
import getpass
import json
from path import path
from constants import *

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=[PULL, PUSH, DISCONNECT, TRACK, UNTRACK, LIST])
parser.add_argument('-k', '--key')
parser.add_argument('-f', '--files', nargs="+")
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

    with open(path('manifest.json'), 'r') as manifest_file:
        json_data = json.load(manifest_file) 
        for key, paths in json_data.items():
            backup_base_path = syncer_dir + path('/backup/%s' % key)
            content_base_path = syncer_dir + path('/content/%s' % key)

            if not path.exists(backup_base_path):
                sh.mkdir(backup_base_path)

            for f in paths:
                f_path = path(f)
                backup_path = backup_base_path + '/' +  f_path.name
                content_path = content_base_path + '/' + f_path.name

                # save a backup first
                if not path.exists(backup_path):
                    sh.cp('-r', path.expand(f_path), backup_path)

                # create symlink from content_path to f_path
                sh.ln('-s', content_path, path.expand(f_path)) 

elif args.command == TRACK:
    if not (args.key or args.files):
        raise Exception("Track is missing key and files")

    ensure_syncer_dir()
    sh.cd(syncer_dir)

    json_data = {}
    with open(path('manifest.json'), 'r') as manifest_file:
        try:
            json_data = json.load(manifest_file)
        except:
            json_data = {}

    json_data[args.key] = args.files
    with open(path('manifest.json'), 'w') as manifest_file:
        manifest_file.write(json.dumps(json_data))

    content_base_path = syncer_dir + path('/content/%s' % args.key)

    if not path.exists(content_base_path):
        sh.mkdir(content_base_path)

    for f in args.files:
        f_path = path(f)
        sh.cp('-r', path.expand(f_path), content_base_path + '/' + f_path.name)  

    sh.git('add', '-A')
    sh.git('commit', '-m', 'Tracking %s' % args.key)
    
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

