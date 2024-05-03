from enum                                                           import Enum

class GitUsage (Enum):

    no_git_usage                                    = 0
    git_local_only                                  = 1
    git_local_and_remote                            = 2
