from .api import Api


class Repo:

    def __init__(self, api: Api):
        self.api = api

    def file_urls(self, user, repo, path):
        """
        Explore recursively a repo and extract the file list

        :param user: Github Username
        :param repo: Github Repo
        :param path: Path in the Repo
        :return: Flat list of all files recursively found along with their download URLs
        """
        contents = self.api.contents(user, repo, path)
        return self.format_result(contents)

    def format_result(self, contents):
        return [{
            'file_path': file['path'],
            'download_url': file['download_url']
        } for file in contents]