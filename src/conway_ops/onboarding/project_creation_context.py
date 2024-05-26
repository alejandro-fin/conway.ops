from pathlib                                                        import Path

from conway_ops.repo_admin.filesystem_repo_inspector                import FileSystem_RepoInspector
from conway_ops.onboarding.git_usage                                import GitUsage


class ProjectCreationContext:

    '''
    This class is a context manager intended to be used when creating a new repo for a project.
    It takes care of the GIT-related aspects of creating such a repo, so that the logic surrounded by this
    context manager can focus on the "functional" aspects, i.e., populating the content of interest in 
    the filesystem's folder for the repo (what in GIT corresponds to the work directory)
    '''
    def __init__(self, repo_admin, repo_name, git_usage=GitUsage.git_local_and_remote, work_branch_name=None):

        self.repo_admin                             = repo_admin
        self.repo_name                              = repo_name
        self.git_usage                              = git_usage
        self.work_branch_name                       = work_branch_name

        # These are created upon entering the context
        self.repos_root                             = None
        self.git_repo                               = None

        # These are set by the business logic running within the context
        self.files_l                                = None

    async def __aenter__(self):
        '''
        Returns self
        
        '''
        local_url                                   = self.repo_admin.local_root + "/" + self.repo_name
        Path(local_url).mkdir(parents=True, exist_ok=False)        

        if self.git_usage == GitUsage.git_local_and_remote:
            self.repos_root                         = self.repo_admin.remote_root
            # Create folders. They shouldn't already exist, since we are creating a brand new project
            Path(self.repos_root + "/" + self.repo_name).mkdir(parents=True, exist_ok=False)
            inspector                               = FileSystem_RepoInspector(self.repos_root, self.repo_name)
            # This creates the master branch (in remote)
            self.git_repo                           = inspector.init_repo() 
        elif self.git_usage == GitUsage.git_local_only:
            self.repos_root                         = self.repo_admin.local_root
            inspector                               = FileSystem_RepoInspector(self.repos_root, self.repo_name)
            # This creates the master branch (in local)
            self.git_repo                           = inspector.init_repo() 
        else:
            self.repos_root                         = self.repo_admin.local_root
            self.git_repo                           = None

        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):

        if not exc_value is None: # Propagate the exception. TODO: Maybe should put cleanup code for any GIT repos previously created
            return False

        if self.git_usage != GitUsage.no_git_usage:
            self.git_repo.index.add(self.files_l)
            self.git_repo.index.commit("Initial commit")            

            master_branch                           = self.git_repo.active_branch
            work_branch                             = self.git_repo.create_head(self.work_branch_name)
            work_branch.checkout()

            if self.git_usage == GitUsage.git_local_and_remote:
                # In this case the self.git_repo is the remote, and need to create the local
                local_url                           = self.repo_admin.local_root + "/" + self.repo_name

                local_repo                          = self.git_repo.clone(local_url)

                # Now come back to master branch on the remote, so that if local tries to do a git push,
                # the push succeeds (i.e., avoid errors of pushing to a remote branch arising from that branch
                # being checked out in the remote, so move remote to a branch to which pushes are not made, i.e., to master).
                #
                master_branch.checkout()

