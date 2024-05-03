from git                                                            import Repo

from conway.util.toml_utils                                         import TOML_Utils

from conway_ops.util.git_client                                     import GitClient


class RepoSetup():

    '''
    Class to support creation of a local development environment for a user's profile.

    The services of this class pre-suppose that the user's profile has access to one or more projects
    in GitHub, each of which consist of one or more repos.

    It also pre-supposes that the caller has access to user profile information.

    This class allows the user to clone such repos into a local folder of the user's choice, and to configure
    the local GIT repository as per Conway standards pased on the profile configuration. Specifically:

    * Creation of local branch based on the profile
    * Configure the local GIT repo's user and e-mail
    * Configure Beyond Compare as a diff and merge tool, invoked from WSL but running in Windows

    :param str sdlc_root: folder in the local file system under which CCL SDLC profiles and tools exist.
    :param str profile_name: name of the user profile for which repos should be setup.
    '''
    def __init__(self, sdlc_root, profile_name):

        self.sdlc_root                                  = sdlc_root
        self.profile_name                               = profile_name
        self.profile_path                               = f"{sdlc_root}/sdlc.profiles/{profile_name}/profile.toml" 
        self.profile                                    = TOML_Utils().load(self.profile_path)

    def setup(self, project):
        '''
        For the given project, it clones and configures all repos for that project that are specified in 
        the user profile self.profile_name.

        The repos are created in a project folder under the profile's root folder for local development.

        :param str project: name of the project to set up. Must be a project that appears in 
                            self.profile["local_development"]

        '''
        P                                               = self.profile

        GH_ORGANIZATION                                 = P["git"]["github_organization"]
  
        REPO_LIST                                       = P["local_development"][project]
        LOCAL_ROOT                                      = P["local_development"]["root"]
        WORKING_BRANCH                                  = P["git"]["working_branch"]
        USER                                            = P["git"]["user"]["name"]

        REMOTE_ROOT                                     = f"https://{USER}@github.com/{GH_ORGANIZATION}"

        # Step 1: clone all applicable repos
        #
        cloned_repo_l = []
        for some_repo_name in REPO_LIST:

            cloned_repo                                 = Repo.clone_from(f"{REMOTE_ROOT}/{some_repo_name}.git", 
                                                                      f"{LOCAL_ROOT}/{project}/{some_repo_name}")
            cloned_repo_l.append(cloned_repo)

        # Step 2:  create working branch
        #
        for some_repo in cloned_repo_l:

            executor                                    = GitClient(some_repo.working_dir)
            # Only create branch with '-b' option if it already exists.
            if executor.execute(command                 = f"git branch --list {WORKING_BRANCH}") == "":
                executor.execute(command                = f"git checkout -b {WORKING_BRANCH}")
            else:
                executor.execute(command                = f"git checkout {WORKING_BRANCH}")

            # Check if branch exists in remote. If not, push local branch. If yes, set it as the upstream.
            if executor.execute(command                 = f"git ls-remote --heads origin {WORKING_BRANCH}") == "":
                executor.execute(command                = f"git push origin -u {WORKING_BRANCH}")
            else:
                executor.execute(command                = f"git branch --set-upstream-to=origin/{WORKING_BRANCH} {WORKING_BRANCH}")

        # Step 3: configure repos
        #
        # GOTCHA
        # Configuring BeyondCompare to work in WSL can be tricky. These settings are based on this post:
        #
        # https://stackoverflow.com/questions/71093803/git-with-beyond-compare-4-on-wsl2-windows-11-not-opening-the-repo-version
        #
        for some_repo in cloned_repo_l:
            self.configure(some_repo.working_dir)

    def configure(self, repo_path):
        '''
        Configures a local repo as per the CCL standards.

        :param str repo_path: path in the local file system for a GIT repo.

        '''
        P                                               = self.profile

        USER                                            = P["git"]["user"]["name"]
        USER_EMAIL                                      = P["git"]["user"]["email"]

        BC_PATH                                         = P["git"]["bc_path"]

        WIN_CRED_PATH                                   = P["git"]["win_cred_path"]


        executor                                        = GitClient(repo_path)
        # At present, credentials manager configuration is global and done in ~/.bashrc, so comment it for now
        #
        #executor.execute(command                        = f'git config --local credential.helper "{WIN_CRED_PATH}"')
        #executor.execute(command                        = f'git config --local credential.https://dev.azure.com.usehttppath true')
        
        executor.execute(command                        = f'git config --local user.name "{USER}"')
        executor.execute(command                        = f'git config --local user.email "{USER_EMAIL}"')
    
        executor.execute(command                        = f'git config --local diff.tool bc')
        
        executor.execute(command                        = f'git config --local difftool.prompt false')
    
        executor.execute(command                        = f'git config --local difftool.bc.path "{BC_PATH}"')
        executor.execute(command                        = f'git config --local difftool.bc.trustExitCode true')
    
        # For the difftool.bc.cmd, we need to map the local and remote paths between WSL and Windows, and to do that
        # we need to pass a setting for which the quotes can get a little tricky. 
        #
        # Ultimately this is what we want to the argument list. The 
        # last argument needs to have 2 levels of quotes since it is a composite that internally also has composites. Hence the challenge:
        #
        #  ['git',
        #   'config',
        #   '--local',
        #   'difftool.bc.cmd',
        #   '"/mnt/c/Program Files/Beyond Compare 4/BCompare.exe" "$(wslpath -aw $LOCAL)" "$(wslpath -aw $REMOTE)"'
        #  ]
        #
        # To achieve that (a string with 2 levels of quotes inside it) we need to use 3 levels of quotes (since the outer 
        # level is needed to define the string).
        #
        # That is why we use this patther for the argument to executor.execute, where we escape the inner 
        # single quote (\') to distinguish it from the outer single quote (')
        #
        #   f'git config --local difftool.bc.cmd \'"{BC_PATH}" "$(wslpath -aw $LOCAL)" "$(wslpath -aw $REMOTE)"\''
        #
        executor.execute(command                        = f'git config --local difftool.bc.cmd \'"{BC_PATH}"' 
                                                            + f' "$(wslpath -aw $LOCAL)" "$(wslpath -aw $REMOTE)"\'')
    
    
        executor.execute(command                        = f'git config --local merge.tool bc')
    
        executor.execute(command                        = f'git config --local mergetool.bc.path "{BC_PATH}"')
        executor.execute(command                        = f'git config --local mergetool.bc.trustExitCode true')
    
        # For mergetool.bc.cmd we have the same challenges with triple quotes as described above for the difftool.bc.cmd. 
        # In this case, this # is the argument list we need:
        #
        #  ['git',
        #   'config',
        #   '--local',
        #   'mergetool.bc.cmd',
        #   '"/mnt/c/Program Files/Beyond Compare 4/BCompare.exe" "$(wslpath -aw $LOCAL)" "$(wslpath -aw $REMOTE)" "$(wslpath -aw $BASE)" "$(wslpath -aw $MERGED)"'
        #  ]
        #
        # So we again escape the inner single quote:
        #
        #   f'git config --local mergetool.bc.cmd \'"{BC_PATH}" "$(wslpath -aw $LOCAL)" "$(wslpath -aw $REMOTE)" "$(wslpath -aw $BASE)" "$(wslpath -aw $MERGED)"\''
        #
        executor.execute(command                        = f'git config --local mergetool.bc.cmd \'"{BC_PATH}"'
                                                            + f' "$(wslpath -aw $LOCAL)" "$(wslpath -aw $REMOTE)"'
                                                            + f' "$(wslpath -aw $BASE)"  "$(wslpath -aw $MERGED)"\'')