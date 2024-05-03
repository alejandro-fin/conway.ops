
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

        APPLICATION                         = self.project_name

        bundled_repos                       = [RepoInfo(APPLICATION, "svc",
                                                        "Source code for business logic and services layers"),
                                                RepoInfo(APPLICATION,"docs",
                                                        "Source code for documentation website"),
                                                RepoInfo(APPLICATION, "test",
                                                        "Source code for test cases"),
                                                RepoInfo(APPLICATION, "scenarios",
                                                        "Collection of self-contained databases (scenarios) used by test cases"),
                                                RepoInfo(APPLICATION, "ops",
                                                        "Source code for tools to operate")
                                                ]

        return bundled_repos
    
class RepoInfo():

    '''
    Data structure used to hold some descriptive information about a repo, pertinent when
    creating or manipulating the repo.

    As per Conway semantics, a Conway project entails multiple repos, each for a subproject. Standard naming for
    repos is then "{project name}.{subproject name}". For example, "cash.svc" would be the name of a repo
    for the "cash" Conway project and the "svc" subproject.

    :param str project: Name of the Conway project, one of whose repos is identified by this object.
    :param str subproject: Name of the sub-project corresponding to the specific repo identified by this object.
    :param str description: Short description of what is the purpose of the repo.
    '''
    def __init__(self, project, subproject, description):
        self.project                        = project
        self.subproject                     = subproject
        self.name                           = f"{project}.{subproject}"
        self.description                    = description