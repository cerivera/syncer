import sh
from constants import *

def check_repo_exists(username, repo_name):
    try:
        repos_data = sh.grep(
                sh.curl('%s/users/%s/repos' % (GITHUB_API_URL, username)), 
                '"name"\s*:\s*%s' % repo_name)
        return True
    except sh.ErrorReturnCode:
        return False
