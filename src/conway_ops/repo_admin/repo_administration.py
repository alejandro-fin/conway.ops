import asyncio

from pathlib                                                        import Path

import pandas                                                       as _pd
import xlsxwriter

from conway.async_utils.ushering_to                                 import UsheringTo
from conway.observability.logger                                    import Logger
from conway.reports.report_writer                                   import ReportWriter
from conway.util.yaml_utils                                         import YAML_Utils

from conway_ops.onboarding.git_usage                                import GitUsage
from conway_ops.repo_admin.repo_statics                             import RepoStatics
from conway_ops.repo_admin.repo_inspector_factory                   import RepoInspectorFactory
from conway_ops.repo_admin.repo_inspector                           import RepoInspector
from conway_ops.util.git_local_client                                     import GitLocalClient



class RepoAdministration():

    '''
    Class to assist operator to manage the multiple repos that comprise a Conway application.

    :param str local_root: Folder or URL of the parent folder for all local GIT repos.

    :param str remote_root: Folder or URL of the parent folder for the remote GIT repos

    :param RepoBundle repo_bundle: Object encapsulating the names of the GIT repos for which joint GIT operations 
        are to be done by this :class:`RepoAdministration` instance.

    :param str remote_gh_user: GitHub username with rights to the remote repository. If the remote is not in
        GitHub, it may be set to None

    :param str remote_gh_organization: the owner of the remote GitHub repo. Might be an organization or a user.
        If the remote is not in GitHub, it may be set to None.

    :param str gh_secrets_path: path in the local file system for a file that contains a GitHub token to access the remote.
        The token must correspond to the user given by the `remote_gh_user` parameter. If the remote is not in GitHub
        then it may be set to None

    '''
    def __init__(self, local_root, remote_root, repo_bundle, remote_gh_user, remote_gh_organization, gh_secrets_path):
        self.local_root                                 = local_root
        self.remote_root                                = remote_root
        self.repo_bundle                                = repo_bundle
        self.remote_gh_user                             = remote_gh_user
        self.remote_gh_organization                     = remote_gh_organization
        self.gh_secrets_path                            = gh_secrets_path

        # Load the token for accessing the remote in GitHub, if we indeed are using GitHub and have a secrets path
        if not self.gh_secrets_path is None:
            secrets_dict                                = YAML_Utils().load(self.gh_secrets_path)
            self.github_token                           = secrets_dict['secrets']['github_token']  
        else:
            self.github_token                           = None          
 
    async def branches(self, repo_name):
        '''
        :return: branches in local repo
        :rtype: list[str]
        '''
        executor                = GitLocalClient(self.local_root + "/" + repo_name)

        git_result              = await executor.execute("git branch")

        # git_result is something like
        #
        #       '  ah-dev\n  integration\n  operate\n* story_1455\n  story_1485'
        #
        # so to get a list we must split by new lines and strip spaces and the '*'

        branch_l                = [b.strip("*").strip() for b in git_result.split("\n")]
        return branch_l
    
    async def is_branch_merged_to_destination(self, repo_name, branch_name, destination_branch):
        '''
        :return: True if the local branch called ``branch_name`` has already been merged into the
            ``destination_branch``. Returns False otherwise.
        :rtype: bool
        '''
        executor                = GitLocalClient(self.local_root + "/" + repo_name)

        git_result              = await executor.execute("git branch --merged " + str(destination_branch))

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
        return sorted([repo_info.name for repo_info in self.repo_bundle.bundled_repos()])
       
    def current_local_branch(self, repo_name):
        '''
        Returns the name of the current branch in the local repo identified by ``repo_name``
        '''
        inspector                                   = RepoInspectorFactory.findInspector(self.local_root, repo_name)
        return inspector.current_branch()

    async def create_repo_report(self, publications_folder, 
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
        RS                                                  = RepoStatics
        MASKED_MSG                                          = "< MASKED > "

        STATS_DIRECTORY                                     = publications_folder + "/"                 \
                                                                + RS.OPERATOR_REPORTS + "/"    \
                                                                + RS.DEV_OPS_REPORTS_FOLDER
                                                        
        STATS_FILENAME                                      = RS.REPORT_REPO_STATS + ".xlsx"
        Path(STATS_DIRECTORY).mkdir(parents=True, exist_ok=True)

        workbook                                            = xlsxwriter.Workbook(STATS_DIRECTORY + "/" + STATS_FILENAME)
        writer                                              = ReportWriter()


        # Now generate and save the stats worksheet
        stats_df                                            = await self.repo_stats(git_usage, repos_in_scope_l)
        if mask_nondeterministic_data:
            stats_df[RS.LAST_COMMIT_TIMESTAMP_COL]          = MASKED_MSG
            stats_df[RS.LAST_COMMIT_HASH_COL]               = MASKED_MSG
   
        worksheet                                           = workbook.add_worksheet(RS.REPORT_REPO_STATS_WORKSHEET)
        widths_dict                                         = {RS.REPO_NAME_COL:               20,
                                                                RS.LOCAL_OR_REMOTE_COL:         15,
                                                                RS.LAST_COMMIT_COL:             40,
                                                                RS.LAST_COMMIT_TIMESTAMP_COL:   30,
                                                                RS.LAST_COMMIT_HASH_COL:        45}
        async with UsheringTo(result_l = []) as usher: # We don't care about the results, so use an discardable list
            
            usher                                           += asyncio.to_thread(
                                                                writer.populate_excel_worksheet,
                                                                stats_df, 
                                                                workbook, 
                                                                worksheet, 
                                                                widths_dict=widths_dict
                                                                )
            
            # Now generate and save the multiple log worksheets
            all_repos_logs_dict                             = await self._repo_logs(git_usage, repos_in_scope_l)
            for repo_name in all_repos_logs_dict.keys():
                a_repo_logs_dict                            = all_repos_logs_dict[repo_name]
                for instance_type in a_repo_logs_dict.keys(): # instance_type refers to local vs remote repos
                    log_df                                  = a_repo_logs_dict[instance_type]
                    if mask_nondeterministic_data:
                        log_df[RS.COMMIT_DATE_COL]          = MASKED_MSG
                        log_df[RS.COMMIT_HASH_COL]          = MASKED_MSG
                        log_df[RS.COMMIT_AUTHOR_COL]        = MASKED_MSG

                    sheet_name                              = RepoAdministration.worksheet_for_log(repo_name, 
                                                                                                    instance_type)
                    worksheet                               = workbook.add_worksheet(sheet_name)
                    widths_dict                             = {RS.COMMIT_DATE_COL:             30,
                                                                RS.COMMIT_SUMMARY_COL:          35,
                                                                RS.COMMIT_FILE_COL:             65,
                                                                RS.COMMIT_HASH_COL:             45,
                                                                RS.COMMIT_AUTHOR_COL:           40
                    }
                    usher                                           += asyncio.to_thread(
                                                                        writer.populate_excel_worksheet,
                                                                        log_df, 
                                                                        workbook, 
                                                                        worksheet, 
                                                                        widths_dict=widths_dict, 
                                                                        freeze_col_nb=3
                                                                        )
                                                        
        workbook.close()


    def worksheet_for_log(repo_name, instance_type):
        '''
        :param str instance_type:  Either ``RepoStatics.LOCAL_REPO`` or ``RepoStatics.REMOTE_REPO``
        :param str repo_name: Name of the repo whose logs are to be persisted in the worksheet whose name is computed
            by this method.
        :return: The worksheets used by the ``self.create_repo_report`` method to save log information for the repo
            identified by ``repo_name`` for the given ``instance_type``
        :rtype: str
        '''
        sheet_name                                      = repo_name + " (" + instance_type + ")"
        
        # xlsxwriter does not allow worksheet names to exceed 31 characters, so truncate if needed
        # to avoid an excelption when we save
        sheet_name                                      = sheet_name[:31]
        return sheet_name


    async def repo_stats(self, git_usage=GitUsage.git_local_and_remote, repos_in_scope_l=None):
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
        async def _process_one_repo(repo_name, inspector, local_or_remote):
            repo_name, current_branch, \
                commit_message, commit_ts, commit_hash, \
                untracked_files, modified_files, deleted_files \
                                                        = await self._one_repo_stats(inspector)

            return [repo_name, local_or_remote, current_branch, 
                        len(untracked_files), len(modified_files), len(deleted_files),
                        commit_message, commit_ts, commit_hash, 
                        ]

        # Need to pass repos_in_scope_l to the supervisor to avoid getting errors like
        # 
        #       UnboundLocalError: cannot access local variable 'repos_in_scope_l' where it is not associated with a value
        #
        if repos_in_scope_l is None:
            repos_in_scope_l                            = self.repo_names()
        async with UsheringTo(data_l) as usher:
            for repo_name in repos_in_scope_l:

                if git_usage in [GitUsage.git_local_and_remote, GitUsage.git_local_only]:
                    local_inspector                     = RepoInspectorFactory.findInspector(self.local_root, repo_name)

                    usher                               += _process_one_repo(
                                                                    repo_name, 
                                                                    inspector           = local_inspector, 
                                                                    local_or_remote     = RS.LOCAL_REPO)

                if git_usage in [GitUsage.git_local_and_remote]:
                    remote_inspector                    = RepoInspectorFactory.findInspector(self.remote_root, repo_name)

                    usher                               += _process_one_repo(
                                                                    repo_name, 
                                                                    inspector           = remote_inspector, 
                                                                    local_or_remote     = RS.REMOTE_REPO)

        result_df                                       = _pd.DataFrame(data = data_l, columns = columns)

        # To get deterministic results even though we are processing asynchronously, sort the DataFrame
        result_df                                       = result_df.sort_values(by = [RS.REPO_NAME_COL,
                                                                                        RS.LOCAL_OR_REMOTE_COL])

        return result_df
    
    async def _repo_logs(self, git_usage, repos_in_scope_l=None):
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

        async def _one_repo_logs(repo_name):
            result_dict[repo_name]                              = {}
            local_log_df                                        = None
            if git_usage in [GitUsage.git_local_and_remote, GitUsage.git_local_only]:
                local_inspector                                 = RepoInspectorFactory.findInspector(self.local_root, repo_name)
                local_log_df                                    = await local_inspector.log_to_dataframe()

            remote_log_df                                       = None
            if git_usage in [GitUsage.git_local_and_remote]:
                remote_inspector                                = RepoInspectorFactory.findInspector(self.remote_root,repo_name)
                remote_log_df                                   = await remote_inspector.log_to_dataframe()
            return repo_name, local_log_df, remote_log_df
        
        repo_logs_l                                             = []
        async with UsheringTo(repo_logs_l) as usher:
            for repo_name in repos_in_scope_l:
                usher                                           += _one_repo_logs(repo_name)


        # Convert the from the tuples (repo_name, local_log_df, remote_log_df) in repo_logs_l
        # to a dictionary
        #
        for repo_name, local_log_df, remote_log_df in repo_logs_l:
            result_dict[repo_name][RepoStatics.LOCAL_REPO]      = local_log_df
            result_dict[repo_name][RepoStatics.REMOTE_REPO] = remote_log_df
 
        return result_dict

    async def _one_repo_stats(self, repo: RepoInspector):
        '''
        '''
        repo_name                                       = repo.repo_name

        current_branch                                  = await repo.current_branch()

        commit_info                                     = await repo.last_commit()
        commit_hash                                     = commit_info.commit_hash
        commit_message                                  = commit_info.commit_msg
        commit_ts                                       = commit_info.commit_ts

        untracked_files                                 = await repo.untracked_files()
        modified_files                                  = await repo.modified_files()
        deleted_files                                   = await repo.deleted_files()

        return repo_name, current_branch, commit_message, commit_ts, commit_hash, \
            untracked_files, modified_files, deleted_files


    def log_info(self, msg, xlabels=None):
        '''
        Logs the ``msg`` at the INFO log level.

        :param str msg: Information to be logged
        '''
        #Application.app().log(msg, Logger.LEVEL_INFO, show_caller=False)
        Logger.log_info(msg, stack_level_increase=1, xlabels=xlabels)
