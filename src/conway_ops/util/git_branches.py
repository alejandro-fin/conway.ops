from enum                                                           import Enum

'''
Enum class used to represent the standard branches used in Conway projects for merging and releasing.
I.e., all branches that are not "feature" branches
'''
class GitBranches (Enum):

    MASTER_BRANCH                                       = "master"
    INTEGRATION_BRANCH                                  = "integration"
    OPERATE_BRANCH                                      = "operate"
