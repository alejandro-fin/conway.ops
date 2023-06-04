
class RepoBundle():

    '''
    Represents the standard structure of a "bundle" of repos for an application, i.e., the knowledge about
    the names of all the repos required for a project as per standard patterns of the :class:``conway``
    module, namely:

    * The repo for the application itself, i.e., the business logic and the service layer exposing business functionality
    * A repo for the code of test cases
    * A repo for the scenarios (i.e., test data) that test cases rely on
    * A repo for the documentation
    * A repo for the tooling required to operate the application

    :param str project_name: Name of the application for which this instance of RepoBundle represents the
        names of all Git repos required by that application

    '''
    def __init__(self, project_name):
        self.project_name                   = project_name



    def bundled_repos(self):
        '''
        :return: Information about the repos comprising this :class:`RepoBundle`.
        :rtype: List[RepoInfo]
        '''
        # Standard templates for naming repos

        APPLICATION_REPO_NAME               = self.project_name

        bundled_repos                       = [RepoInfo(APPLICATION_REPO_NAME,
                                                        "Source code for business logic and services layers"),
                                                RepoInfo(APPLICATION_REPO_NAME + "_docs",
                                                        "Source code for documentation website"),
                                                RepoInfo(APPLICATION_REPO_NAME + "_test",
                                                        "Source code for test cases"),
                                                RepoInfo(APPLICATION_REPO_NAME + "_scenarios",
                                                        "Collection of self-contained databases (scenarios) used by test cases"),
                                                RepoInfo(APPLICATION_REPO_NAME + "_ops",
                                                        "Source code for tools to operate")
                                                ]

        return bundled_repos
    
class RepoInfo():

    '''
    Data structure used to hold some descriptive information about a repo, pertinent when
    creating or manipulating the repo

    :param str name: Name of the repo
    :param str description: Short description of what is the purpose of the repo.
    '''
    def __init__(self, name, description):
        self.name                           = name
        self.description                    = description