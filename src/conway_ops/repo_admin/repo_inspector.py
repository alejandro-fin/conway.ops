import abc
import pandas                                                       as _pd

from conway_ops.repo_admin.repo_statics                             import RepoStatics

class RepoInspector(abc.ABC):

    '''
    Abstract class for utility classes that provide convenience methods to query GIT repos.

    :param str parent_url: A string identifying the location under which the repo of interest lives as
        a "subfolder" or "sub resource". May be a path to the local file system or the URL to a remote server.
    :param str repo_name: A string identifying the name of the repo of interest, as a "subfolder"
        or "sub resource" under the ``parent_url``.

    '''
    def __init__(self, parent_url, repo_name):

        self.parent_url                     = parent_url
        self.repo_name                      = repo_name

    @abc.abstractmethod
    def current_branch(self):
        '''
        :return: The name of the current branch
        :rtype: str
        '''
    
    @abc.abstractmethod
    def modified_files(self):
        '''
        :return: List of files that have been modified but not yet staged. In the boundary case where a file
            has an unstaged deletion, that does not count as "modified" as per the semantics of this method.
        :rtype: list
        '''
    
    @abc.abstractmethod
    def deleted_files(self):
        '''
        :return: List of files with an unstaged deletion
        :rtype: list
        '''

    @abc.abstractmethod
    def untracked_files(self):
        '''
        :return: List of files that are not tracked
        :rtype: list
        '''

    @abc.abstractmethod
    def last_commit(self):
        '''
        :return: A :class:`CommitInfo` with information about last commit"
        :rtype: str
        '''
    
    @abc.abstractmethod
    def branches(self):
        '''
        :return: (local) branches for the repo
        :rtype: list[str]
        '''

    @abc.abstractmethod
    def committed_files(self):
        '''
        Returns an iterable over CommitedFileInfo objects, yielding in chronological order the history of commits
        (i.e., a log) for the repo associated to this :class:`RepoInspector`
        '''

    @abc.abstractmethod
    def pull_request(self, from_branch, to_branch, title, body):
        '''
        Creates and completes a pull request from the ``from_branch`` to the ``to_branch``.

        If anything goes wrong it raises an exception.
        '''


    @abc.abstractmethod
    def update_local(self, branch):
        '''
        Updates the local repo from the remote, for the given ``branch``.

        If anything goes wrong it raises an exception.

        :param str branch: repo local branch to update from the remote.
        '''

    def log_to_dataframe(self):
        '''
        :return: A DataFrame with log information. Each row in the DataFrame
            represents a file that was committed, so there are typically multiple rows per commit.
        :rtype: :class:`pandas.DataFrame`
        '''
        commit_nb_l                                     = []
        commit_date_l                                   = []
        summary_l                                       = []
        commit_file_nb_l                                = []
        commit_file_l                                   = []
        commit_hash_l                                   = []
        commit_author_l                                 = []

        for cfi in self.committed_files():

            commit_nb_l.                                append(cfi.commit_nb)
            commit_date_l.                              append(cfi.commit_date)
            summary_l.                                  append(cfi.summary)
            commit_file_nb_l.                           append(cfi.commit_file_nb)
            commit_file_l.                              append(cfi.commit_file)
            commit_hash_l.                              append(cfi.commit_hash)
            commit_author_l.                            append(cfi.commit_author)
        
        log_dict                                        = {RepoStatics.COMMIT_NB_COL:       commit_nb_l,
                                                           RepoStatics.COMMIT_DATE_COL:     commit_date_l,
                                                           RepoStatics.COMMIT_SUMMARY_COL:  summary_l,
                                                           RepoStatics.COMMIT_FILE_NB_COL:  commit_file_nb_l,
                                                           RepoStatics.COMMIT_FILE_COL:     commit_file_l,
                                                           RepoStatics.COMMIT_HASH_COL:     commit_hash_l,
                                                           RepoStatics.COMMIT_AUTHOR_COL:   commit_author_l}

        log_df                                          = _pd.DataFrame(log_dict)
        return log_df

class CommitInfo():
    '''
    Helper data structure to contain some information about a commit

    :param str commit_hash: Hash for a commit. Example: "15e5a7f280096c84ed08b72371580907d0f52ff5"
    :param str commit_msg: Message for a commit. Example: "Added logic to create submissions directory if missing"
    :param Timestamp commit_ts: Timestamp as of when the commit was made
    '''
    def __init__(self, commit_hash, commit_msg, commit_ts):
        self.commit_hash                    = commit_hash
        self.commit_msg                     = commit_msg
        self.commit_ts                      = commit_ts

class CommittedFileInfo():
    '''
    Helper data structure to contain log information about 1 file included in a commit, contextualized
    within the broader list of files for that commit, and beyond that, contextualized within the overall
    set of commits.
    
    So there would be multiple :class:`CommittedFileInfo` objects per commit, one per file in the commit.
    All those would share the same general information about the commit.

    In the description of parameters below, we use this terminology:

    * *this file* refers to the file associated with this :class:`CommittedFileInfo`

    * *this commit* refers to the commit that contains this file.

    :param int commit_nb: the :class:`RepoInspector` keeps count of the commits that exist, associating them numbers 0, 1, 2, ..., ordering
        the commits by the date when they were made. In that count, this parameter represents the number
        for this commit.
    :param str commit_date: the date for this commit.
    :param str summary: this commit's message
    :param int commit_file_nb: the :class:`RepoInspector` keeps count of the files included in each commit,
        associating them numbers 0, 1, 2, ...,. In that count, this parameter represents the number for this file.
    :param str commit_file: relative path (within the repo) for this file.
    :param str commit_hash: GIT ash for this commit
    :param str commit_author: name of this commit's author
    '''
    def __init__(self, commit_nb, commit_date, summary, commit_file_nb, commit_file, commit_hash, commit_author):

        self.commit_nb                      = commit_nb
        self.commit_date                    = commit_date
        self.summary                        = summary
        self.commit_file_nb                 = commit_file_nb
        self.commit_file                    = commit_file
        self.commit_hash                    = commit_hash
        self.commit_author                  = commit_author


    