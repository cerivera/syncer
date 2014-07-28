import requests
import json
from constants import *


def check_repo_exists(username, repo_name):
    response = requests.get('%s/users/%s/repos' % (GITHUB_API_URL, username))
    json_response = response.json()

    if 'message' in json_response:
        raise Exception(json_response['message'])

    for repo in json_response:
        if repo['name'] == repo_name:
            return True

    return False


def create_public_repo(username, password, repo_name):
    payload = {
        'name': repo_name, 
        'private': False
    }

    response = requests.post('%s/user/repos' % GITHUB_API_URL, data=json.dumps(payload), auth=(username, password))
    json_response = response.json()

    if 'message' in json_response:
        raise Exception(json_response['message'])
    
    return True

