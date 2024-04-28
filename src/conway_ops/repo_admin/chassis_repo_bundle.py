
from conway_ops.repo_admin.repo_bundle         import RepoBundle, RepoInfo

class Chassis_RepoBundle(RepoBundle):

    '''
    '''
    def __init__(self):
        PROJECT_NAME                                    = "conway"
        super().__init__(PROJECT_NAME)

    def bundled_repos(self):
        '''
        :return: The names of the repos comprising this :class:`RepoBundle`.
        :rtype: List[str]
        '''
        repo_info_l                                     = super().bundled_repos()
        repo_info_l.append(RepoInfo("conway", "acceptance",
                           "Source code for test framework available to applications built with the '" 
                                + self.project_name + "'."))
        repo_info_l.append(RepoInfo("conway", "acceptance.docs",
                           "Source code for documentation on test framework provided as part of the '" 
                                + self.project_name + "'."))

        return repo_info_l
