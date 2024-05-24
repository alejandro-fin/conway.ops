from conway_ops.onboarding.repo_bundle                          import RepoBundle

class RepoBundleFactory():

    '''
    This is a convenience class, to facilitate creating a RepoBundle object for a Conway-based project.
    '''
    def __init__(self):
        pass

    def inferFromRepoList(repo_list: list[str]) -> RepoBundle:
        '''
        Creates a RepoBundle object by inferring a project from the list of repos in `repo_list`.
        The expectation is that `repo_list` would be something like

                ["scratch.svc", "scratch.ops", "scratch.test", "scratch.scenarios"]

        In this example, the inference will be that the project is "scratch" and that we need to
        that the RepoBundle would advertise that the project consists of a repo for each of the suffixes
        ".svc", ".ops", ".test", and ".scenarios".

        :param list[str] repo_list: list of repos for the project for which we seek a RepoBundle
        :returns: a RepoBundle object
        :retype: conway_ops.onboarding.repo_bundle.RepoBundle
        '''
        project_name_candidates             = list(set(elt.split(".")[0] for elt in repo_list))
        if len(project_name_candidates) != 1:
            raise ValueError(f"Bad repo_list was provided: '{repo_list}'"
                             + f"\nIt is bad because it suggests that the project is not unique, as found these "
                             + f"candidates for the project: '{project_name_candidates}'."
                             + f"\nInstead, should have found exactly 1 candidate, not {len(project_name_candidates)}.")
        
        project_name                        = project_name_candidates[0]
        cutoff                              = len(project_name) + 1 
        
        # E.g., if a repo in repo_list is "scratch.svc" then this cuts off the "scratch." suffix to leave just "svc"
        repo_suffixes                       = [elt[cutoff:] for elt in repo_list]

        return RepoBundle(project_name, repo_suffixes)