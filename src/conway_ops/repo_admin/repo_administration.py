from pathlib                                                        import Path
import os                                                           as _os
import pandas                                                       as _pd
import xlsxwriter
from enum                                                           import Enum

from conway.observability.logger                                    import Logger

from conway.reports.report_writer                                   import ReportWriter

from conway_ops.repo_admin.repo_statics                             import RepoStatics
from conway_ops.repo_admin.repo_inspector_factory                   import RepoInspectorFactory
from conway_ops.repo_admin.repo_inspector                           import RepoInspector
from conway_ops.repo_admin.filesystem_repo_inspector                import FileSystem_RepoInspector
from conway_ops.repo_admin.repo_bundle                              import RepoBundle
from conway_ops.repo_admin.git_client                               import GitClient
from conway_ops.scaffolding.scaffold_generator                      import ScaffoldGenerator


class GitUsage (Enum):

    no_git_usage                                    = 0
    git_local_only                                  = 1
    git_local_and_remote                            = 2


class _ProjectCreationContext:

    def __init__(self, repo_admin, repo_name, git_usage=GitUsage.git_local_and_remote, work_branch_name=None):
        '''
        This class is a context manager intended to be used when creating a new repo for a project.
        It takes care of the GIT-related aspects of creating such a repo, so that the logic surrounded by this
        context manager can focus on the "functional" aspects, i.e., populating the content of interest in 
        the filesystem's folder for the repo (what in GIT corresponds to the work directory)
        '''
        self.repo_admin                             = repo_admin
        self.repo_name                              = repo_name
        self.git_usage                              = git_usage
        self.work_branch_name                       = work_branch_name

        # These are created upon entering the context
        self.repos_root                             = None
        self.git_repo                               = None

        # These are set by the business logic running within the context
        self.files_l                                = None

    def __enter__(self):
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

    def __exit__(self, exc_type, exc_value, exc_tb):

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



from conway.util.yaml_utils                                     import YAML_Utils

class RepoAdministration():

    '''
    Class to assist operator to manage the multiple repos that comprise a Conway application.

    :param str local_root: Folder or URL of the parent folder for all local GIT repos.

    :param str remote_root: Folder or URL of the parent folder for the remote GIT repos

    :param RepoBundle repo_bundle: Object encapsulating the names of the GIT repos for which joint GIT operations 
        are to be done by this :class:`RepoAdministration` instance.

    :param str remote_gh_user: GitHub username with rights to the remote repository. If the remote is not in
        GitHub, it may be set to None

    :param str gb_secrets_path: path in the local file system for a file that contains a GitHub token to access the remote.
        The token must correspond to the user given by the `remote_gh_user` parameter. If the remote is not in GitHub
        then it may be set to None

    '''
    def __init__(self, local_root, remote_root, repo_bundle, remote_gh_user, gb_secrets_path):
        self.local_root                                 = local_root
        self.remote_root                                = remote_root
        self.repo_bundle                                = repo_bundle
        self.remote_gh_user                             = remote_gh_user
        self.gb_secrets_path                            = gb_secrets_path

        # Load the token for accessing the remote in GitHub, if we indeed are using GitHub and have a secrets path
        if not self.gb_secrets_path is None:
            secrets_dict                                = YAML_Utils().load(self.gb_secrets_path)
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

            with _ProjectCreationContext(repo_admin=self, repo_name=repo_info.name, 
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
    



    
    def branches(self, repo_name):
        '''
        :return: branches in local repo
        :rtype: list[str]
        '''
        executor                = GitClient(self.local_root + "/" + repo_name)

        git_result              = executor.execute("git branch")

        # git_result is something like
        #
        #       '  ah-dev\n  integration\n  operate\n* story_1455\n  story_1485'
        #
        # so to get a list we must split by new lines and strip spaces and the '*'

        branch_l                = [b.strip("*").strip() for b in git_result.split("\n")]
        return branch_l
    
    def is_branch_merged_to_destination(self, repo_name, branch_name, destination_branch):
        '''
        :return: True if the local branch called ``branch_name`` has already been merged into the
            ``destination_branch``. Returns False otherwise.
        :rtype: bool
        '''
        executor                = GitClient(self.local_root + "/" + repo_name)

        git_result              = executor.execute("git branch --merged " + str(destination_branch))

        # git_result is something like
        #
        #       '  ah-dev\n  integration\n  operate\n* story_1455\n  story_1485'
        #
        # so to get a list we must split by new lines and strip spaces and the '*'

        branch_l                = [b.strip("*").strip() for b in git_result.split("\n")]

        if branch_name in branch_l:
            return True
        else:
            return False
    
    def repo_names(self):
        '''
        :return: names of all the repos in this :class:`RepoAdministration`'s repo bundle.
        :rtype: list[str]
        '''
        return [repo_info.name for repo_info in self.repo_bundle.bundled_repos()]
       
    def current_local_branch(self, repo_name):
        '''
        Returns the name of the current branch in the local repo identified by ``repo_name``
        '''
        inspector                                   = RepoInspectorFactory.findInspector(self.local_root, repo_name)
        return inspector.current_branch()

    def checkout_branch(self, branch_name, repos_in_scope_l, local=True):
        '''
        For GIT repos in scope, switches them all to the branch given by ``branch_name``, provided that:

        * No repo in scope have no untracked files
        * No repo in scope is bare
        * All repos in scope have branch called ``branch_name``

        :param str branch_name: The name of the branch to which to switch
        :param list[str] repos_in_scope_l: A list of names for GIT repos for which stats are requested. 

        :param bool local: Optional parameter that is True by default. 
            If True, then the repos in scope are local, i.e., the GIT repos under ``self.local_root``. If False,
            then repos in scope are remote, i.e., under ``self.remote_root``.
        :return: A DataFrame with the status information about each repo
        :rtype: :class:`pandas.DataFrame`
        '''
        RS                                              = RepoStatics()
        if local:
            REPOS_ROOT                                  = self.local_root
            repo_environment                            = RS.LOCAL_REPO
        else:
            REPOS_ROOT                                  = self.remote_root
            repo_environment                            = RS.REMOTE_REPO

        # Check that we can move out of current branch safely, i.e., there is no uncommitted work
        stats_df                                        = self.repo_stats(repos_in_scope_l=repos_in_scope_l,
                                                                          git_usage = GitUsage.git_local_and_remote)
        stats_df                                        = stats_df[stats_df[RS.LOCAL_OR_REMOTE_COL]==repo_environment]
        def _bad_row(row):
            '''
            Returns True if the ``row`` contains information about a repo that has untracked changes or is dirty
            (i.e., working tree has modifications and/or index has uncommitted changes)
            '''
            if row[RS.NB_UNTRACKED_FILES_COL] > 0 or row[RS.NB_MODIFIED_FILES_COL] > 0 or row[RS.NB_DELETED_FILES_COL] > 0:
                return True
            else:
                return False

        bad_df                                          = stats_df[stats_df.apply(lambda row: _bad_row(row), axis=1)]
        if len(bad_df) > 0:
            raise ValueError("Can't switch to branch '" + str(branch_name) + "' because these repos have uncommitted changes: "
                             + ", ".join(list(bad_df[RS.REPO_NAME_COL].unique())))
        
        # Now check that branch exists in all the pertinent repos
        repos_lacking_desired_branch                    = []
        for repo_name in repos_in_scope_l:
            inspector                                   = RepoInspectorFactory.findInspector(REPOS_ROOT, repo_name)
            branches                                    = inspector.branches()
            if not branch_name in branches:
                repos_lacking_desired_branch.append(repo_name)
        if len(repos_lacking_desired_branch) > 0:
            raise ValueError("Can't switch to branch '" + str(branch_name) + "' because that branch doesn't exist in these repos: "
                             + ", ".join(repos_lacking_desired_branch))

        # Now move to the new branch
        for repo_name in repos_in_scope_l:
            inspector                                   = RepoInspectorFactory.findInspector(REPOS_ROOT, repo_name)

            status                                      = inspector.checkout(branch_name)

            print("\n-----------" + repo_name + "-----------\n")
            print("\tStatus:\t\t" + str(status))

    def create_repo_report(self, publications_folder, 
                           repos_in_scope_l             = None, 
                           git_usage                    = GitUsage.git_local_and_remote,
                           mask_nondeterministic_data   = False):
        '''
        Creates an Excel report with multiple worksheets, as follows:

        * There is a worksheet with general stats for all repos

        * For each repo name, there are two worksheets, containing log information for the local and remote
            repos with those names.

        :param str publications_folder: Root directory for a folder structure under which all reports
            must be saved. The Excel report created by this method will be saved in the subdirectory
            ``/Operator Reports/DevOps/`` under this root ``publications_folder``.
        :param list[str] repos_in_scope_l: A list of names for GIT repos for which stats are requested. If set to None, 
            then it will default to provide stats for the repos ``self.repo_bundle``
        :param GitUsage get_usage: enum used to determine which GIT areas were created, if any, to scope the report to the GIT
            areas actually used.
        :param bool mask_nondeterministic_data: If True, then any data that is non-deterministic (such as dates or hash 
            codes) is masked. This is False by default. Typical use case for masking is in test cases that need 
            determinism.
        :rtype: None
        '''
        # First, set up common static variables 
        MASKED_MSG                                              = "< MASKED > "

        STATS_DIRECTORY                                         = publications_folder + "/"                 \
                                                                    + RepoStatics.OPERATOR_REPORTS + "/"    \
                                                                    + RepoStatics.DEV_OPS_REPORTS_FOLDER
                                                        
        STATS_FILENAME                                          = RepoStatics.REPORT_REPO_STATS + ".xlsx"
        Path(STATS_DIRECTORY).mkdir(parents=True, exist_ok=True)

        workbook                                                = xlsxwriter.Workbook(STATS_DIRECTORY + "/" + STATS_FILENAME)
        writer                                                  = ReportWriter()

        # Now generate and save the stats worksheet
        stats_df                                                = self.repo_stats(git_usage, repos_in_scope_l)
        if mask_nondeterministic_data:
            stats_df[RepoStatics.LAST_COMMIT_TIMESTAMP_COL]     = MASKED_MSG
            stats_df[RepoStatics.LAST_COMMIT_HASH_COL]          = MASKED_MSG

        worksheet                                               = workbook.add_worksheet(RepoStatics.REPORT_REPO_STATS_WORKSHEET)
        widths_dict                                             = {RepoStatics.REPO_NAME_COL:               20,
                                                                    RepoStatics.LOCAL_OR_REMOTE_COL:         15,
                                                                    RepoStatics.LAST_COMMIT_COL:             40,
                                                                    RepoStatics.LAST_COMMIT_TIMESTAMP_COL:   30,
                                                                    RepoStatics.LAST_COMMIT_HASH_COL:        45}
        writer.populate_excel_worksheet(stats_df, workbook, worksheet, widths_dict=widths_dict)
        
        # Now generate and save the multiple log worksheets
        all_repos_logs_dict                                     = self.repo_logs(git_usage, repos_in_scope_l)
        for repo_name in all_repos_logs_dict.keys():
            a_repo_logs_dict                                    = all_repos_logs_dict[repo_name]
            for instance_type in a_repo_logs_dict.keys(): # instance_type refers to local vs remote repos
                log_df                                          = a_repo_logs_dict[instance_type]
                if mask_nondeterministic_data:
                    log_df[RepoStatics.COMMIT_DATE_COL]         = MASKED_MSG
                    log_df[RepoStatics.COMMIT_HASH_COL]         = MASKED_MSG
                    log_df[RepoStatics.COMMIT_AUTHOR_COL]       = MASKED_MSG

                sheet_name                                      = RepoAdministration.worksheet_for_log(repo_name, 
                                                                                                       instance_type)
                worksheet                                       = workbook.add_worksheet(sheet_name)
                widths_dict                                     = {RepoStatics.COMMIT_DATE_COL:             30,
                                                                    RepoStatics.COMMIT_SUMMARY_COL:          35,
                                                                    RepoStatics.COMMIT_FILE_COL:             65,
                                                                    RepoStatics.COMMIT_HASH_COL:             45,
                                                                    RepoStatics.COMMIT_AUTHOR_COL:           40
                }
                writer.populate_excel_worksheet(log_df, workbook, worksheet, widths_dict=widths_dict, freeze_col_nb=3)
                                                        
        workbook.close()

    def worksheet_for_log(repo_name, instance_type):
        '''
        :param str instance_type:  Either ``RepoStatics.LOCAL_REPO`` or ``RepoStatics.REMOTE_REPO``
        :param str repo_name: Name of the repo whose logs are to be persisted in the worksheet whose name is computed
            by this method.
        :return: The worksheets used by the ``create_repo_report`` method to save log information for the repo
            identified by ``repo_name`` for the given ``instance_type``
        :rtype: str
        '''
        sheet_name                                      = repo_name + " (" + instance_type + ")"
        
        # xlsxwriter does not allow worksheet names to exceed 31 characters, so truncate if needed
        # to avoid an excelption when we save
        sheet_name                                      = sheet_name[:31]
        return sheet_name


    def repo_stats(self, git_usage, repos_in_scope_l=None):
        '''
        :param list[str] repos_in_scope_l: A list of names for GIT repos for which stats are requested. If set to None, 
            then it will default to provide stats for names of ``self.repo_bundle.bundled_repos()``
        :return: A descriptive DataFrame with information about each repo, such as what branch it is in for local and 
            remote, whether it has unchecked or untracked files, and most recent commit.
        :rtype: :class:`pandas.DataFrame`
        '''
        RS                                              = RepoStatics()

        data_l                                          = []

        columns                                         = [RS.REPO_NAME_COL,
                                                           RS.LOCAL_OR_REMOTE_COL,
                                                           RS.CURRENT_BRANCH_COL,
                                                           RS.NB_UNTRACKED_FILES_COL,
                                                           RS.NB_MODIFIED_FILES_COL,
                                                           RS.NB_DELETED_FILES_COL,
                                                           RS.LAST_COMMIT_COL,
                                                           RS.LAST_COMMIT_TIMESTAMP_COL,
                                                           RS.LAST_COMMIT_HASH_COL,
                                                           ]
        if repos_in_scope_l is None:
            repos_in_scope_l                            = self.repo_names()
        for repo_name in repos_in_scope_l:

            if git_usage in [GitUsage.git_local_and_remote, GitUsage.git_local_only]:
                local_inspector                         = RepoInspectorFactory.findInspector(self.local_root, repo_name)

                repo_name, current_branch, \
                    commit_message, commit_ts, commit_hash, \
                    untracked_files, modified_files, deleted_files \
                                                        = self._one_repo_stats(local_inspector)
                local_or_remote                         = RS.LOCAL_REPO
                data_l.append([repo_name, local_or_remote, current_branch, 
                            len(untracked_files), len(modified_files), len(deleted_files),
                            commit_message, commit_ts, commit_hash, 
                            ])

            if git_usage in [GitUsage.git_local_and_remote]:
                remote_inspector                        = RepoInspectorFactory.findInspector(self.remote_root, repo_name)

                repo_name, current_branch, \
                    commit_message, commit_ts, commit_hash, \
                    untracked_files, modified_files, deleted_files \
                                                        = self._one_repo_stats(remote_inspector)
                local_or_remote                         = RS.REMOTE_REPO
                data_l.append([repo_name, local_or_remote, current_branch, 
                            len(untracked_files), len(modified_files), len(deleted_files),
                            commit_message, commit_ts, commit_hash, 
                            ])

        result_df                                       = _pd.DataFrame(data = data_l, columns = columns)

        return result_df
    
    def repo_logs(self, git_usage, repos_in_scope_l=None):
        '''
        :param GitUsage get_usage: enum used to determine which GIT areas were created, if any, to scope the report to the GIT
        areas actually used.

        :param list[str] repos_in_scope_l: A list of names for GIT repos for which stats are requested. If set to None, then 
            it will default to provide stats for ``self.repo_names``
        :return: Logs for each of the repos named in ``repos_in_scope_l``. For each repo name, two DataFrames are produced, 
            corresponding to the local and remote repos for a given name. These multiple DataFrames are packaged in 
            a 2-level dictionary, where the top level keys are the repo names, the next level keys are the 
            ``RepoStatics.LOCAL_REPO`` and ``RepoStatics.REMOTE_REPO``, and the values are the log DataFrames.
        :rtype: :class:`dict`
        '''
        result_dict                                             = {}
        if repos_in_scope_l is None:
            repos_in_scope_l                                    = self.repo_names()
        for repo_name in repos_in_scope_l:
            result_dict[repo_name]                              = {}

            local_log_df                                        = None
            if git_usage in [GitUsage.git_local_and_remote, GitUsage.git_local_only]:
                local_inspector                                 = RepoInspectorFactory.findInspector(self.local_root, repo_name)
                local_log_df                                    = local_inspector.log_to_dataframe()
                result_dict[repo_name][RepoStatics.LOCAL_REPO]  = local_log_df

            remote_log_df                                       = None
            if git_usage in [GitUsage.git_local_and_remote]:
                remote_inspector                                = RepoInspectorFactory.findInspector(self.remote_root,repo_name)
                remote_log_df                                   = remote_inspector.log_to_dataframe()
                result_dict[repo_name][RepoStatics.REMOTE_REPO] = remote_log_df
 
        return result_dict

    def _git_ignore_content(self):
        '''
        :return: Contents with which to initialize a new ``.gitignore`` file for a new Git repo.
        :rtype: list[str]
        '''
        lines                                           = []
        lines.append("# Python build")
        lines.append("__pycache__/")
        lines.append("*.egg-info/")
        lines.append("")
        lines.append("")
        lines.append("# Used in documentation")
        lines.append("build/")
        lines.append("*.~docx")
        lines.append("*.~xlsx")
        lines.append("*.~vsdx")
        lines.append("*.~pptx")
        lines.append("")
        lines.append("")
        lines.append("# Used in operator tools")
        lines.append("*.ipynb_checkpoints/")
        lines.append("")
        lines.append("# Used in test scenarios")
        lines.append("ACTUALS@*/")
        lines.append("RUN_NOTES/")
        lines.append("")
        lines.append("")

        return lines

    def _one_repo_stats(self, repo: RepoInspector):
        '''
        '''
        repo_name                                       = repo.repo_name
        current_branch                                  = repo.current_branch()

        commit_info                                     = repo.last_commit()
        commit_hash                                     = commit_info.commit_hash
        commit_message                                  = commit_info.commit_msg
        commit_ts                                       = commit_info.commit_ts

        untracked_files                                 = repo.untracked_files()
        modified_files                                  = repo.modified_files()
        deleted_files                                   = repo.deleted_files()

        return repo_name, current_branch, commit_message, commit_ts, commit_hash, \
            untracked_files, modified_files, deleted_files


    def log_info(self, msg):
        '''
        Logs the ``msg`` at the INFO log level.

        :param str msg: Information to be logged
        '''
        #Application.app().log(msg, Logger.LEVEL_INFO, show_caller=False)
        Logger.log_info(msg)
