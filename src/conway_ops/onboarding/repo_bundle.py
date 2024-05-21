
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

    This default list can be altered by the `repo_suffixes` parameter, causing fewer or additional repo names to
    be part of this RepoBundle.

    :param str project_name: Name of the application for which this instance of RepoBundle represents the
        names of all Git repos required by that application
    :param list[str] repo_suffixes: optional parameter. If not None, then this RepoBundle object will have
        one repo name for each element in `repo_suffixes`. For example, if `repo_sufixes = ["ops", "profiles"]
        and `project_name = "sldc"`, then this RepoBundle defines a project structure consisting of repos
        `["sdlc.ops", "sdcl.profiles"]`.
    '''
    def __init__(self, project_name, repo_suffixes=None):
        self.project_name                   = project_name
        self.repo_suffixes                  = repo_suffixes


    def bundled_repos(self):
        '''
        :return: Information about the repos comprising this :class:`RepoBundle`.
        :rtype: List[RepoInfo]
        '''
        # Standard templates for naming repos

        APPLICATION                         = self.project_name

        SUFFIXES                            = ["svc", "docs", "test", "scenarios", "ops"] if self.repo_suffixes is None \
                                                                                            else self.repo_suffixes  

        DESCRIPTIONS                        = {"svc":       "Source code for business logic and services layers",
                                               "docs":      "Source code for documentation website",
                                               "test":      "Source code for test cases",
                                               "scenarios": "Collection of self-contained databases (scenarios) used by test cases",
                                               "ops":       "Source code for tools to operate"}  

        bundled_repos                       = [] 

        for suffix in SUFFIXES:
            description                     = "" if not suffix in DESCRIPTIONS.keys() else DESCRIPTIONS[suffix]
            bundled_repos.append(RepoInfo(APPLICATION, suffix, description))

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