
from conway_ops.onboarding.repo_bundle        import RepoBundle


class RepoBundleSubset(RepoBundle):

    '''
    Helper class used to represent a bundle of repos that is a subset of another bundle.
    An example use case is when there is a partial fork of some, but not all, the repos that comprise
    an application. In that case this class comes handy to create a ``RepoBundle`` object that
    represents the partial fork, and thereby allow fork developers to leverage the services
    of the :class:`BranchLifechcleManager` even if they did not fork all the repos of the application.

    :param RepoBundle full_bundle: A repo bundle for which this class represents a subset
    :param list[str] subset_repo_names: names of the repos in ``full_bundle`` that comprise the subset
        of repos which are bundled into this :class:`RepoBundleSubset` instance.
    '''
    def __init__(self, full_bundle, subset_repo_names):
        self.full_bundle                        = full_bundle
        self.subset_repo_names                  = subset_repo_names

        super().__init__(full_bundle.project_name)

    def bundled_repos(self):
        '''
        :return: The names of the repos comprising this :class:`RepoBundle`.
        :rtype: List[str]
        '''
        result_l                                = []
        for repo_info in self.full_bundle.bundled_repos():
            if repo_info.name in self.subset_repo_names:
                result_l.append(repo_info)

        return result_l
