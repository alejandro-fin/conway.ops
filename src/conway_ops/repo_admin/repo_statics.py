import abc

class RepoStatics(abc.ABC):

    '''
    Represents a static enum collection of static variables that are used in the administration of GIT repos
    associated to a Conway application.
    '''
    def __init__(self):
        pass

    REPO_NAME_COL                                       = "Repo"
    LOCAL_OR_REMOTE_COL                                 = "Local/Remote"
    CURRENT_BRANCH_COL                                  = "Current Branch"
    LAST_COMMIT_COL                                     = "Last commit"
    LAST_COMMIT_TIMESTAMP_COL                           = "Last commit timestamp"
    LAST_COMMIT_HASH_COL                                = "Last commit hash"
    NB_UNTRACKED_FILES_COL                              = "# Untracked files"
    NB_MODIFIED_FILES_COL                               = "# Modified files"
    NB_DELETED_FILES_COL                                = "# Deleted files"

    LOCAL_REPO                                          = "Local"
    REMOTE_REPO                                         = "Remote"

    RELEASE_CANDIDATE_BRANCH_PREFIX                     = "rc-"

    # Used for reports on repo stats
    #
    OPERATOR_REPORTS                                    = "Operator Reports"
    DEV_OPS_REPORTS_FOLDER                              = "DevOps"
    REPORT_REPO_STATS                                   = "Repo Stats"
    REPORT_REPO_STATS_WORKSHEET                         = "Report"
    #REPORT_REPO_STATS_LOG_WORKSHEET_PREFIX              = "GIT log"

    # Used for columns in log worksheets of repo stats report
    #
    COMMIT_NB_COL                                       = "Commit #"
    COMMIT_DATE_COL                                     = "Date"
    COMMIT_SUMMARY_COL                                  = "Summary"
    COMMIT_FILE_NB_COL                                  = "File #"
    COMMIT_FILE_COL                                     = "Commited Files"
    COMMIT_HASH_COL                                     = "Commit"
    COMMIT_AUTHOR_COL                                   = "Author"
  

