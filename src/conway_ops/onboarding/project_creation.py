from pathlib                                                        import Path
import os                                                           as _os

from conway.util.yaml_utils                                         import YAML_Utils

from conway_ops.onboarding.git_usage                                import GitUsage
from conway_ops.onboarding.project_creation_context                 import ProjectCreationContext
from conway_ops.onboarding.repo_bundle                              import RepoBundle
from conway_ops.scaffolding.scaffold_generator                      import ScaffoldGenerator

class ProjectCreation():

    '''
    Class to assist operator to set up a development area by cloning all the multiple repos that comprise a 
    Conway application.

    :param str local_root: Folder or URL of the parent folder for all local GIT repos.

    :param str remote_root: Folder or URL of the parent folder for the remote GIT repos

    :param RepoBundle repo_bundle: Object encapsulating the names of the GIT repos for which joint GIT operations 
        are to be done by this :class:`RepoAdministration` instance.

    :param str remote_gh_user: GitHub username with rights to the remote repository. If the remote is not in
        GitHub, it may be set to None

    :param str gh_secrets_path: path in the local file system for a file that contains a GitHub token to access the remote.
        The token must correspond to the user given by the `remote_gh_user` parameter. If the remote is not in GitHub
        then it may be set to None

    '''
    def __init__(self, local_root, remote_root, repo_bundle, remote_gh_user, gh_secrets_path):
        self.local_root                                 = local_root
        self.remote_root                                = remote_root
        self.repo_bundle                                = repo_bundle
        self.remote_gh_user                             = remote_gh_user
        self.gh_secrets_path                            = gh_secrets_path

        # Load the token for accessing the remote in GitHub, if we indeed are using GitHub and have a secrets path
        if not self.gh_secrets_path is None:
            secrets_dict                                = YAML_Utils().load(self.gh_secrets_path)
            self.github_token                           = secrets_dict['secrets']['github_token']  
        else:
            self.github_token                           = None          

    def create_project(self, project_name, work_branch_name, scaffold_spec=None, git_usage=GitUsage.git_local_and_remote):
        '''
        Creates all the repos required for a project as per standard patterns of the 
        :class:``RepoBundle``.

        :param str project_name: name of the project (i.e., application) for which repos must be created
        :param str work_branch_name: name of the branch in which work will be done, i.e., a branch that exists
            both in the local and the remote and which is how the local pushes work to the remote.
            NB: By default, the master branch only exists in the remote, hence the need for the work_branch_name.

        :param ScaffoldSpec scaffold_spec: Object encapsulating the code patterns for which sample code should be included
            in the newly created project. By default is is None, in which case the only files generated in the new
            project will be a ``README.md`` and ``.gitignore``.

        :return: a :class:``RepoBundle`` with information about all the repos created for project ``project_name``.
        :rtype: RepoBundle
        '''
        bundle                                          = RepoBundle(project_name)
        created_files_l                                 = []
        for repo_info in bundle.bundled_repos():

            with ProjectCreationContext(repo_admin=self, repo_name=repo_info.name, 
                                         git_usage          = git_usage,
                                         work_branch_name   = work_branch_name) as ctx:
                
                ctx.files_l                            = self._populate_filesystem_repo(repos_root         = ctx.repos_root, 
                                                                                            repo_info       = repo_info,
                                                                                            scaffold_spec   = scaffold_spec)
                created_files_l.append(ctx.files_l)

        # Now generate the config folder, which is external to all repos since it is runtime configuration that must
        # be set by the operator, not the developer
        # It only can be generated when there is a scaffolding spec
        if not scaffold_spec is None:
            config_root                                 = f"{ctx.repos_root}/config"
            scaffold_gen                                = ScaffoldGenerator(config_root, scaffold_spec)
            config_files_l                              = [_os.path.relpath(f, start= config_root) for f in scaffold_gen.generate("config")]
            created_files_l.append(config_files_l)

        return bundle # return bundle, created_files_l
      
    def _populate_filesystem_repo(self, repos_root, repo_info, scaffold_spec):
        '''
        Populates all generated content for a new repo.

        This method is supposed to be called within the ``_ProjectCreationContext`` context manager, so that
        all its preconditions are met. For example, that certain GIT repos already have been created by the
        time this method is called, since they can't be created after this method is called (would result in a
        GIT error, as the working folder would not be empty after this method runs)
        '''
        repo_url                                   = f"{repos_root}/{repo_info.name}"

        Path(repo_url).mkdir(parents=True, exist_ok=True)
 
        if not scaffold_spec is None:
            scaffold_gen                                = ScaffoldGenerator(repo_url, scaffold_spec)
            # The ScaffoldGenerator will return a list of generated files, with their absolute path. However, this method
            # needs to strip the root folder for the repo, to avoid exceptions, since GIT operations need the relative
            # path of the files under the repo.
            #
            # For example, the ScaffoldGenerator may return paths like:
            # 
            #       /mnt/c/Users/aleja/Documents/Code/conway/conway.scenarios/8101/ACTUALS@latest/bundled_repos_remote/cash.svc/.gitignore
            #
            #  but this method would need to return only the relative path under the "cash.svc" repo:
            #
            #       .gitignore
            #
            files_l                                     = [_os.path.relpath(f, start= repo_url) for f in scaffold_gen.generate(repo_info.subproject)]
        else:
            # Avoid having an empty repo, so that it has a head and we can create branches.
            # Accomplish that by adding a scaffold README.md and a scaffold .gitignore
            README_FILENAME                         = "README.md"
            with open(f"{repo_url}/{README_FILENAME}", 'w') as f:
                f.write(f"{repo_info.description} for application '{repo_info.name}'.\n")

            GIT_IGNORE_FILENAME                     = ".gitignore"
            with open(f"{repo_url}/{GIT_IGNORE_FILENAME}", 'w') as f:
                for line in self._git_ignore_content():
                    f.write(line + "\n")

            files_l                                 =  [README_FILENAME, GIT_IGNORE_FILENAME]

        return files_l
    