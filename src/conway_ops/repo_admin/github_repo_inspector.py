import requests                                             as _requests
from dateutil                                               import parser as _parser


from conway.application.application                         import Application

from conway.util.yaml_utils                                 import YAML_Utils
from conway_ops.repo_admin.repo_inspector                   import RepoInspector, CommitInfo, CommittedFileInfo

class GitHub_RepoInspector(RepoInspector):

    '''
    Utility class that is able to execute GIT commands for public repos located in GitHub

    :param str parent_url: A string identifying the location under which the repo of interest lives as
        a "subfolder" or "sub resource". May be a path to the local file system or the URL to a remote server.
    :param str repo_name: A string identifying the name of the repo of interest, as a "subfolder"
        or "sub resource" under the ``parent_url``.

    '''
    def __init__(self, parent_url, repo_name):

        super().__init__(parent_url, repo_name)

        # parent_url is something like 
        #
        #       "https://github.com/alejandro-fin"
        #
        # so we can extract the owner name from it ("alejandro-fin" in the example). This will be needed
        # to construct the URLs for other calls to the Git Hub API
        #
        cleaned_url                                     = parent_url.strip("/").strip()
        self.owner                                      = cleaned_url.split("/")[-1]

        if len(self.owner) == 0:
            raise ValueError("No owner was included in parent url '" + str(parent_url) + "', so can't call Git Hub APIs")
        
        # Get GitHub token to make authenticated calls.
        #
        SECRETS_PATH                                    = Application.app().config.secrets_path()
        secrets_dict                                    = YAML_Utils().load(SECRETS_PATH)
        self.github_token                               = secrets_dict['secrets']['github_token']

    GIT_HUB_API                                         = "https://api.github.com"
    

    def _get_resource(self, resource_path):
        '''
        Invokes the Git Hub API to get information about the repo associated to this inspector.

        :param str resource_path: Indicates the path of a desired resource under the URL for the
            repo for which self is an inspector. Examples: "/commits/master", "/branches"
        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        root_path                           = self.GIT_HUB_API + "/repos/" + self.owner + "/" + self.repo_name
        url                                 = root_path + resource_path

        return self._get_from_url(url)     
    
    def _get_from_url(self, url):
        '''
        Invokes the URL to get information about the repo associated to this inspector.

        :param str url: Indicates the absolute url in the GitHub API. 
        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        headers = {
            'Authorization': 'Bearer ' + self.github_token,
            'Content-Type' : 'application/json',
            'Accept'       : 'application/json'
        }
        try:
            response                        = _requests.request(method          = 'GET', 
                                                                url             = url, 
                                                                params          = {}, 
                                                                data            = '', \
                                                                headers         = headers, 
                                                                timeout         = 20,
                                                                verify          = True) 

            data                            = response.json()

        except Exception as ex:
            raise ValueError("Problem connecting to Git Hub. Error is: " + str(ex))

        if response.status_code != 200:
            certificate_file                = f"<YOUR CONDA INSTALL ROOT>/envs/<YOUR CONDA ENVIRONMENT>/lib/site-packages/certifi/cacert.pem"
                         
            raise ValueError(f"Error status {response.status_code} from doing: GET on '{url}'."
                             + f"\nThis often happens due to one of two things: "
                             + f"\n\t1) expired GitHub certificates (most common)"
                             + f"\n\t2) or expired GitHub token in the secrets file for conway.ops"
                             + f"\nFor the first, if using Conda, check {certificate_file}"
                             + f"\nFor the latter, login to GitHub as a user with access to the remote repos in question"
                             + f"\nand generate a token (in settings=>developer settings) and copy it to the secrets file for this repo.")  

        return data      


    def current_branch(self):
        '''
        :return: The name of the current branch
        :rtype: str
        '''
        # In the Git Hub world there is no notion of "current branch" - this is a GIT-in-the-filesystem
        # notion. 
        # Since for practical purposes this is invoked when comparating some cloned repo to the master
        # branch in the remote, we just treat "master" as the "current branch" in GitHub
        return "master"
    
    def modified_files(self):
        '''
        :return: List of files that have been modified but not yet staged. In the boundary case where a file
            has an unstaged deletion, that does not count as "modified" as per the semantics of this method.
        :rtype: list
        '''
        # In the Git Hub world there is no notion of "modified files" - this is a GIT-in-the-filesystem
        # notion. 
        # So we return an empty list
        return []
    
    def deleted_files(self):
        '''
        :return: List of files with an unstaged deletion
        :rtype: list
        '''
        # In the Git Hub world there is no notion of "deleted files" - this is a GIT-in-the-filesystem
        # notion. 
        # So we return an empty list
        return []
    
    def untracked_files(self):
        '''
        :return: List of files that are not tracked
        :rtype: list
        '''
        # In the Git Hub world there is no notion of "untracked files" - this is a GIT-in-the-filesystem
        # notion. 
        # So we return an empty list
        return []

    def last_commit(self):
        '''
        :return: A :class:`CommitInfo` with information about last commit"
        :rtype: str
        '''
        data                                = self._get_resource("/commits/master")
        
        commit_datetime                     = _parser.parse(data['commit']['author']['date'])
        
        commit_hash                         = data['sha']

        commit_ts                           = commit_datetime.strftime("%y%m%d.%H%M%S")

        commit_msg                          = data['commit']['message']

        result                              = CommitInfo(commit_hash, commit_msg, commit_ts)

        return result

        
    def branches(self):
        '''
        :return: (local) branches for the repo
        :rtype: list[str]
        '''
        data                                = self._get_resource("/branches")

        result                              = [b['name'] for b in data]

        return result


    def committed_files(self):
        '''
        Returns an iterable over CommitedFileInfo objects, yielding in chronological order the history of commits
        (i.e., a log) for the repo associated to this :class:`RepoInspector`
        '''
        # This provides the first most recent commit, and links to "parent" commits - the commits right before it
        data                                = self._get_resource("/commits/master")

        results_dict                        = self._committed_files_impl(results_dict_so_far={}, data=data)

        # We need to sort commits by date in descending order (so most recent commits on top).
        # Remember that the keys of results_dict are pairs of strings representing (commit hash, commit date)
        #
        unsorted_keys                       = list(results_dict.keys())
        sorted_keys                         = sorted(unsorted_keys, key=lambda pair: pair[1], reverse=True)

        aggregated_cfi_l                    = []

        # We are listing commits in reverse order (so most recent commit first), so commit numbers will
        # start at the top and descend
        commit_nb                           = len(sorted_keys) - 1
        
        for key in sorted_keys:
            cfi_l                           = results_dict[key]
            for cfi in cfi_l:
                cfi.commit_nb               = commit_nb
            aggregated_cfi_l.extend(cfi_l)
            commit_nb                       -= 1

        return aggregated_cfi_l
    
    def pull_request(self, from_branch, to_branch):
        '''
        Creates and completes a pull request from the ``from_branch`` to the ``to_branch``.

        If anything goes wrong it raises an exception.
        '''    
        raise ValueError("Not yet implemented")
    
    def checkout(self, branch):
        '''
        Switches the repo to the given branch.

        :param str branch: branch to switch repo to.

        If anything goes wrong it raises an exception.
        '''
        raise ValueError("Not yet implemented")
    
    def update_local(self, branch):
        '''
        Updates the local repo from the remote, for the given ``branch``.

        If anything goes wrong it raises an exception.

        :param str branch: repo local branch to update from the remote.
        '''
        raise ValueError("Not yet implemented")

    def _committed_files_impl(self, results_dict_so_far, data):
        '''
        Helper method used to implement the recursion approach behind the method committed_files.

        It incrementally aggregates the file-per-fileinformation for one commit, and then 
        recursively calls itself to process the parent commits.

        The incremental aggregation is effected by adding additional entries to the ``results_dict_so_far``
        dictionary.

        :param dict results_dict_so_far:  keys are pairs of strings (the commit hash and commit date) 
            and for each key the value is the list
            of CommittedFileInfo objects for this commit. It represents the information we seek for 
            the commits that have been already processed prior to this method being called.
        :param dict data: The JSON response from querying the Git Hub API for the next commit to process.

        :return: a dictionary extending ``results_dict_so_far`` with additional entries for the commit
            represented by the ``data`` parameter, and the ancestors of that commit.
        :rtype: dict
        '''
        commit_date                         = data['commit']['author']['date']
        commit_author                       = data['commit']['author']['name']
        
        commit_hash                         = data['sha']
        commit_msg                          = data['commit']['message']

        # The commit history is a tree, so not linear. It is possible we come across the same commit more than once.
        # So if we already saw this commit, don't process it again.
        #
        if (commit_hash, commit_date) in results_dict_so_far.keys():
            return results_dict_so_far

        file_count                          = 0
        commit_cfi_l                        = []
        results_dict                        = results_dict_so_far
        for file_info_dict in data['files']:
            filename                        = file_info_dict['filename']
            cfi                             = CommittedFileInfo(commit_nb           = -99, # Caller will later set this
                                                                commit_date         = commit_date,
                                                                summary             = commit_msg,
                                                                commit_file_nb      = file_count,
                                                                commit_file         = filename,
                                                                commit_hash         = commit_hash,
                                                                commit_author       = commit_author)
            commit_cfi_l.append(cfi)
            file_count                      += 1

        results_dict[(commit_hash, commit_date)]    = commit_cfi_l

        # Now do recursion, for each parent
        parents                             = data['parents']
        for p in parents:
            p_data                          = self._get_from_url(p['url'])
            results_dict                    = self._committed_files_impl(results_dict, p_data)

        return results_dict