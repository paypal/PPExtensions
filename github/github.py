from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler
from git import Repo, exc, GitCommandError
from shutil import move
from urllib.parse import urlparse, unquote

import requests
import json
import os

GITHUB_URL_PREFIX = "https://github.com/"
GITHUB_API_PREFIX = "https://api.github.com"
GITHUB_TOKEN = os.getenv("githubtoken","")
NOTEBOOK_STARTUP_PATH = os.getcwd() + "/"
LOCAL_REPO_FOLDER = "Sharing"
LOCAL_REPO_PREFIX = NOTEBOOK_STARTUP_PATH + LOCAL_REPO_FOLDER


class PrivateGitHandler(IPythonHandler):
    """
    The base class that has all functions used in private sharing backend handlers.
    """

    def error_handler(self, err, iserr=True):
        err = err.replace("\n", "<br/>").replace("\t", "  ")
        if iserr:
            self.set_status(500)
            self.finish(err)

    @staticmethod
    def git_clone(local_repo_path, repo_url):
        try:
            repo_instance = Repo(local_repo_path)
        except exc.NoSuchPathError:
            o = urlparse(repo_url)
            repo_url_with_token = o.scheme + "://" + GITHUB_TOKEN + "@" + o.hostname + o.path
            Repo.clone_from(repo_url_with_token, local_repo_path)
            with open(local_repo_path + "/.gitignore", "a") as f:
                f.write("\n.*\n.gitignore")
            repo_instance = Repo(local_repo_path)
        return repo_instance

    def git_commit(self, from_path, to_path, file_name, repo_instance, commit_message):
        try:
            move(from_path, to_path)
        except Exception as e:
            self.error_handler(str(e))
        git_instance = repo_instance.git
        if not os.path.isdir(to_path):
            git_instance.add(file_name)
        else:
            git_instance.add("--a")
        git_instance.commit("-m", commit_message)

    @staticmethod
    def git_commit_inside(file_name, repo_instance, commit_message, option):
        git_instance = repo_instance.git
        if option == "single":
            git_instance.add(file_name)
        else:
            git_instance.add("--a")
        git_instance.commit("-m", commit_message)

    @staticmethod
    def get_repo(file_path):
        repos = dict()
        headers = {'Authorization': 'token ' + GITHUB_TOKEN}
        parts = file_path.split("/")
        if parts[0] == LOCAL_REPO_FOLDER:
            repo_name = parts[1] + "/" + parts[2]
            branch = requests.get(GITHUB_API_PREFIX + '/repos/' + repo_name + '/branches', headers=headers)
            if branch.status_code == 404:
                repos[repo_name] = ['Branch Not Found!']
            if len(branch.json()) == 0:
                repos[repo_name] = ['master']
            else:
                repos[repo_name] = [br['name'] for br in branch.json()]
        else:
            params = {'affiliation': "owner", "per_page": 100, "sort": "full_name"}
            repo = requests.get(GITHUB_API_PREFIX + '/user/repos', headers=headers, params=params).json()
            for rp in repo:
                repo_name = rp['full_name']
                branch = requests.get(GITHUB_API_PREFIX + '/repos/' + repo_name + '/branches', headers=headers)
                if branch.status_code == 404:
                    repos[repo_name] = ['Branch Not Found!']
                if len(branch.json()) == 0:
                    repos[repo_name] = ['master']
                else:
                    repos[repo_name] = [br['name'] for br in branch.json()]
        return json.dumps(repos)


class PrivateGitGetRepoHandler(PrivateGitHandler):
    """
    Get the accessible github repos and display them in the dropdown in github push menu
    """

    def get(self):
        file_path = self.get_argument("filepath", "")
        try:
            repos = self.get_repo(file_path)
            self.finish(repos)
        except Exception as e:
            self.error_handler(str(e))


class PrivateGitPushHandler(PrivateGitHandler):
    """
    Private sharing handler to push a notebook or a folder to remote repo.
    Step1: Git Clone (If necessary)
    Step2: Git Commit
    Step3: Git Push
    """

    def post(self):
        repo_name = unquote(self.get_argument("repo"))
        branch = self.get_argument("branch")
        commit_message = self.get_argument("msg")
        file_path = unquote(self.get_argument("filepath"))
        file_name = unquote(self.get_argument("filename"))
        repo_url = GITHUB_URL_PREFIX + repo_name + ".git"
        local_repo_path = LOCAL_REPO_PREFIX + "/" + repo_name
        if not file_path.startswith(LOCAL_REPO_FOLDER):
            local_repo_file_path = local_repo_path + "/" + file_path
        else:
            local_repo_file_path = NOTEBOOK_STARTUP_PATH + file_path
        repo_instance = self.git_clone(local_repo_path, repo_url)
        try:
            self.git_commit(NOTEBOOK_STARTUP_PATH + file_path, local_repo_file_path, file_name, repo_instance,
                            commit_message)
        except GitCommandError as e:
            if e.status == 1:
                self.error_handler(e.stdout, iserr=False)
            else:
                self.error_handler(e.stderr)
        try:
            push_info = repo_instance.remote().push("master:" + branch)
            assert push_info[0].flags in [512, 256, 2, 1]
            self.finish(file_name + " has been successfully pushed! ")
        except AssertionError as e:
            if push_info[0].flags == 1032:
                self.error_handler("Updates were rejected because the remote contains work that you do not have "
                                   "locally. Please do git pull and fix the possible conflicts before pushing again!")
        except GitCommandError as e:
            self.error_handler(push_info[0].summary)


class PrivateGitPullHandler(PrivateGitHandler):
    """
    Private Sharing handler to pull a notebook or an entire repo to local.
    If there is a conflict, it will show the conflict in notebook and ask the user to fix.
    """

    def post(self):
        github_repo_url = unquote(self.get_argument("github_repo_url"))
        o = urlparse(github_repo_url)
        if o.path.endswith(".git"):
            repo = o.path.strip(".git")
            branch = "master"
            repo_url = github_repo_url
        else:
            split_word = "/blob/" if "/blob/" in o.path else "/tree/"
            if split_word in o.path:
                repo, path = o.path.split(split_word)
                branch = path.split("/")[0]
                repo_url = github_repo_url.split(split_word)[0] + ".git"
            else:
                repo = o.path
                branch = "master"
                repo_url = github_repo_url + ".git"
        local_repo_path = LOCAL_REPO_PREFIX + repo
        try:
            repo_instance = self.git_clone(local_repo_path, repo_url)
            git_instance = repo_instance.git
            git_instance.pull("origin", branch)
            self.finish("Successfully pulled to Sharing" + repo)
        except GitCommandError as e:
            if "conflict" in e.stdout:
                self.error_handler(e.stdout)
            else:
                self.error_handler(e.stderr)


class PrivateGitCommitHandler(PrivateGitHandler):
    """
        GitCommit handler used by the git commit button in notebook toolBar
    """

    def post(self):
        repo_name = unquote(self.get_argument("repo"))
        file_name = unquote(self.get_argument("filename"))
        option = self.get_argument("option")
        commit_message = "Commit from PayPal Notebook"
        local_repo_path = NOTEBOOK_STARTUP_PATH + repo_name
        try:
            repo_instance = Repo(local_repo_path)
        except exc.InvalidGitRepositoryError as e:
            self.error_handler(str(e))
        try:
            self.git_commit_inside(file_name, repo_instance, commit_message, option)
            self.finish("Commit Success!")
        except GitCommandError as e:
            if e.status == 1:
                self.error_handler(e.stdout)
            else:
                self.error_handler(e.stderr)


def load_jupyter_server_extension(nb_server_app):
    """
    Called when the extension is loaded.

    Args:
        nb_server_app (NotebookWebApplication): handle to the Notebook webserver instance.
    """
    web_app = nb_server_app.web_app
    handlers = [
        (r'/github/private_github_push', PrivateGitPushHandler),
        (r'/github/private_github_pull', PrivateGitPullHandler),
        (r'/github/private_github_get_repo', PrivateGitGetRepoHandler),
        (r'/github/private_github_commit', PrivateGitCommitHandler),
    ]

    base_url = web_app.settings['base_url']
    handlers = [(url_path_join(base_url, h[0]), h[1]) for h in handlers]

    host_pattern = '.*$'
    web_app.add_handlers(host_pattern, handlers)
