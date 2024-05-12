import os                                               as _os
import sys                                              as _sys
import importlib                                        as _importlib

from conway.util.toml_utils                             import TOML_Utils

from conway_ops.util.git_branches                       import GitBranches


class UserProfile():

    '''
    This class holds a user profile in memory. Upon creation of an instance of this class, the profile will
    be loaded from the `profile_path`.

    If some settings in the profile configuration file use environment variables, this class will evaluate those
    environment variables at the time the profile configuration is loaded.

    :param str profile_path: absolute path in the local file system where the profile configuration file resides
    '''
    def __init__(self, profile_path):

        self.profile_path                               = profile_path

        self.profile_dict                               = TOML_Utils().load(self.profile_path)

        P                                               = self.profile_dict

        self.GH_ORGANIZATION                            = P["git"]["github_organization"]

        LOCAL_DEV_ROOT                                  = P["local_development"]["dev_root"]
        OPERATE_ROOT                                    = P["operate"]["operate_root"]

        # Evaluate any environment variable that lives in the path
        self.LOCAL_DEV_ROOT                             = _os.path.expandvars(LOCAL_DEV_ROOT) 
        self.OPERATE_ROOT                               = _os.path.expandvars(OPERATE_ROOT) 
  
        self.USER                                       = P["git"]["user"]["name"]
        self.USER_EMAIL                                 = P["git"]["user"]["email"]

        self.BC_PATH                                    = P["git"]["bc_path"]

        self.WIN_CRED_PATH                              = P["git"]["win_cred_path"]

        self.REMOTE_ROOT                                = f"https://{self.USER}@github.com/{self.GH_ORGANIZATION}"


    def REPO_LIST(self, project):
        '''
        '''
        P                                               = self.profile_dict
        _REPO_LIST                                      = P["projects"][project]["repos"]
        return _REPO_LIST
    
    def OK_TO_DISPLAY_TOKEN(self):
        '''
        This should normally return False, but for profiles specific to the test harness it may return true
        when the tests need the access token to be visible in certain places (e.g., in the Git config remote's URL,
        so that the test harness is not prompted by GIT for credentials)
        '''
        P                                               = self.profile_dict
        if "ok_to_display_token" not in P["git"].keys():
            return False
        
        return P["git"]["ok_to_display_token"]
    
    def REMOTE_IS_LOCAL(self):
        '''
        Determines if remote repos are on the local file system or in GitHub.

        :returns: True if remotes are local, and False otherwise

        '''
        P                                               = self.profile_dict
        if "remote_is_local" not in P["git"].keys():
            return False
        
        return P["git"]["remote_is_local"]

    def OPS_REPO(self, project):
        '''
        '''
        P                                               = self.profile_dict
        _OPS_REPO                                      = P["projects"][project]["ops_repo"]
        return _OPS_REPO
    
    def REPO_BUNDLE_CLASS_NAME(self, project):
        '''
        '''
        P                                               = self.profile_dict
        _REPO_BUNDLE_CLASS_NAME                         = P["projects"][project]["repo_bundle_class"]
        return _REPO_BUNDLE_CLASS_NAME
    
    def instantiate_repo_bundle(self, project, operate):
        '''
        Returns an instance of the class whose name is self.REPO_BUNDLE_CLASS_NAME
        '''
        OPS_REPO                        = self.OPS_REPO(project)
        REPO_BUNDLE_CLASS_NAME          = self.REPO_BUNDLE_CLASS_NAME(project)

        # Add the ops repo's src folder to the path so that the Python class loader can later find this project's
        # repo bundle class and load it. As there might be multiple installations of the ops repos in this
        # machine's file system, put the ops repo we want to be used in front of the path
        #
        local_root                      = self.LOCAL_ROOT(operate=operate, root_folder=None)
        PATH_TO_OPS_MODULES             = f"{local_root}/{project}/{OPS_REPO}/src"
        _sys.path                       = [PATH_TO_OPS_MODULES] + _sys.path

        tokens                          = REPO_BUNDLE_CLASS_NAME.split(".")
        module_name                     = ".".join(tokens[:-1])
        class_name                      = tokens[-1]

        module                          = _importlib.import_module(module_name)
        class_                          = getattr(module, class_name)
        repo_bundle                     = class_()

        return repo_bundle, PATH_TO_OPS_MODULES

    def LOCAL_ROOT(self, operate, root_folder):
        '''
        '''
        P                                               = self.profile_dict
        if operate:
            _LOCAL_ROOT                                 = self.OPERATE_ROOT if root_folder is None else root_folder
        else:
            _LOCAL_ROOT                                 = self.LOCAL_DEV_ROOT if root_folder is None else root_folder
    
        return _LOCAL_ROOT
    
    def BRANCHES_TO_CREATE(self, operate):
        '''
        '''
        P                                               = self.profile_dict
        GB                                              = GitBranches
        if operate:
            _WORKING_BRANCH                             = GB.OPERATE_BRANCH.value
            _BRANCHES_TO_CREATE                         = [GB.OPERATE_BRANCH.value]
        else:
            _WORKING_BRANCH                             = P["git"]["working_branch"]
            _BRANCHES_TO_CREATE                         = [GB.INTEGRATION_BRANCH.value, _WORKING_BRANCH]

        return _BRANCHES_TO_CREATE




