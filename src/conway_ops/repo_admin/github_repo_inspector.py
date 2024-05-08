import requests                                             as _requests
from dateutil                                               import parser as _parser


from conway.application.application                         import Application
from conway.util.yaml_utils                                 import YAML_Utils

from conway_ops.repo_admin.github_response_handler          import GitHub_ReponseHandler
from conway_ops.repo_admin.repo_inspector                   import RepoInspector, CommitInfo, CommittedFileInfo

class GitHub_RepoInspector(RepoInspector):

    '''
    Utility class that is able to execute GIT commands for public repos located in GitHub

    :param str parent_url: A string identifying the location under which the repo of interest lives as
        a "subfolder" or "sub resource". It is expected to be the URL to a remote server, such as GitHub URL
        to a GitHub organization or user account.
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

        #self.github_api_url                             = f"https://{self.owner}@api.github.com"
        self.github_api_url                             = f"https://api.github.com"
    
    def GET(self, resource_path):
        '''
        Invokes the "GET" HTTP verb on the Git Hub API to get a resource associated to this inspector's repo.

        :param str resource_path: Indicates the path of a desired resource to create or update, under the URL for the
            repo for which self is an inspector. Examples: "/commits/master", "/branches", "/pulls" 
        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        return self._http_call("GET", resource_path)
    
    def POST(self, resource_path, body):
        '''
        Invokes the "POST" HTTP verb on the Git Hub API to create a resource associated to this inspector's repo.

        :param str resource_path: Indicates the path of a desired resource to create or update, under the URL for the
            repo for which self is an inspector. Examples: "/commits/master", "/branches", "/pulls" 
        :param dict body: payload to submit in the HTTP request.
        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        return self._http_call("POST", resource_path, body)
    
    def PUT(self, resource_path, body):
        '''
        Invokes the "PUT" HTTP verb on the Git Hub API to update a resource associated to this inspector's repo.

        :param str resource_path: Indicates the path of a desired resource to create or update, under the URL for the
            repo for which self is an inspector. Examples: "/commits/master", "/branches", "/pulls" 
        :param dict body: payload to submit in the HTTP request.
        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        return self._http_call("PUT", resource_path, body)
           
    
    def _http_call(self, method, resource_path, body={}):
        '''
        Invokes the Git Hub API to get information about the repo associated to this inspector.

        :param str method: the HTTP verb to use ("GET", "POST", or "PUT")
        :param str resource_path: Indicates the path of a desired resource to create or update, under the URL for the
            repo for which self is an inspector. Examples: "/commits/master", "/branches", "/pulls"
        :param dict body: optional payload to submit in the HTTP request. 
        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        root_path                           = f"{self.github_api_url}/repos/{self.owner}/{self.repo_name}"
        url                                 = root_path + resource_path

        headers = {
            'Authorization': 'Bearer ' + self.github_token,
            'Content-Type' : 'application/json',
            # GOTCHA:
            #       Painfully found that GitHub post APIs will only work with the "vnd.github*" MIME types
            #'Accept'       : 'application/json'
            'Accept'        : 'application/vnd.github+json'
            
        }
        try:
            response                        = _requests.request(method          = method, 
                                                                url             = url, 
                                                                params          = {}, 
                                                                json            = body,
                                                                headers         = headers, 
                                                                timeout         = 20,
                                                                verify          = True) 

        except Exception as ex:
            raise ValueError("Problem connecting to Git Hub. Error is: " + str(ex))
        
        return GitHub_ReponseHandler().process(response)    

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
        data                                = self.GET("/commits/master")
        
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
        data                                = self.GET("/branches")

        result                              = [b['name'] for b in data]

        return result

    def committed_files(self):
        '''
        Returns an iterable over CommitedFileInfo objects, yielding in chronological order the history of commits
        (i.e., a log) for the repo associated to this :class:`RepoInspector`
        '''
        # This provides the first most recent commit, and links to "parent" commits - the commits right before it
        data                                = self.GET("/commits/master")

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
    
    def pull_request(self, from_branch, to_branch, title, body):
        '''
        Creates and completes a pull request from the ``from_branch`` to the ``to_branch``.

        If anything goes wrong it raises an exception.

        :param str from_branch: GIT branch used as the source for the pull request
        :param str to_branch: GIT branch used as the destination for the pull request
        :param str title: the value of the `title` field in the GitHub pull request object being created
        :param str body: the value of the `body` field in the GitHub pull request object being created
        :returns: The pull request information. If the pull request was not created for a benign reason
                (for example, if there are no commits to merge from the `from_branch` to the `to_branch`)
                it returns None.

        :rtype: dict
        '''    
        pr_result                           =  self._create_pull_request(from_branch, to_branch, title, body)
        if pr_result is None:
            return None
        else:
            pull_number                     = pr_result['number']
            return self._merge_pull_request(pr_result, f"PR #{pull_number}: {title}")
    
    def _create_pull_request(self, from_branch, to_branch, title, body):
        '''
        Creates a pull request from the ``from_branch`` to the ``to_branch``.

        If anything goes wrong it raises an exception.

        :param str from_branch: GIT branch used as the source for the pull request
        :param str to_branch: GIT branch used as the destination for the pull request
        :returns: The pull request information. If the pull request was not created for a benign reason
                (for example, if there are no commits to merge from the `from_branch` to the `to_branch`)
                it returns None.

        :rtype: dict
        '''    
        pr_data                             = {"title":     title,
                                               "body":      body,
                                               "head":      from_branch,
                                               "base":      to_branch}


        pr_result                           =  self.POST("/pulls", pr_data)
        if pr_result is None:
            Application.app().log(f"{from_branch}->{to_branch}: no merge needed")
            return None
        else:
            pull_number                     = pr_result['number']
            Application.app().log(f"{from_branch}->{to_branch}: PR #{pull_number} created")

        return pr_result
        
    def _merge_pull_request(self, pr, title):
        '''
        Merges a pull request.

        If anything goes wrong it raises an exception.

        :param dict pr: pull request object obtained from a previous API call to GitHub to create a pull request
        :param str title: Title for the pull request commit
        :returns: The mrege information. If no merge was needed, returns None.

        :rtype: dict
        '''    
        pull_number                         = pr['number']
        sha                                 = pr['head']['sha']
        from_branch                         = pr['head']['ref']
        to_branch                           = pr['base']['ref']

        merge_data                          = {"commit_title":      title,
                                                "commit_message":   "",
                                                "sha":              sha,
                                                "merge_method":     "merge"}

        merge_result                    =  self.PUT(f"/pulls/{pull_number}/merge", merge_data)

        Application.app().log(f"{from_branch}->{to_branch}: PR #{pull_number} merged")

        return merge_result

    
    def update_local(self, branch):
        '''
        This method is deliberatly not implemented, and will raise an error if called.

        The only reason that this method exists is that the parent abstract class mandates it, 
        but for repos in GitHub it does not apply since there is no notion of "local" repo.

        :param str branch: repo local branch to update from the remote.
        '''
        raise ValueError("This method does not apply for GitHub repos - never call it")

    def _committed_files_impl(self, results_dict_so_far, data):
        '''
        Helper method used to implement the recursion approach behind the method committed_files.

        It incrementally aggregates the file-per-file information for one commit, and then 
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
            p_data                          = self.GET(p['url'])
            results_dict                    = self._committed_files_impl(results_dict, p_data)

        return results_dict