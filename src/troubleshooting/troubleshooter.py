import time
import sys                                                                  as _sys

CODING_ROOT = "C:/Alex/Code"

MODULE_PATHS = [CODING_ROOT + "/conway_ops/src"]
import sys
sys.path.extend(MODULE_PATHS)

CONWAY_ROOT_FORK            = CODING_ROOT + "/conway_fork"
REMOTE_CONWAY_FORK_ROOT     ="https://github.com/alejandro-fin/"
CONWAY_LOCAL_REPOS          = ["conway.svc", "conway.acceptance", "conway.ops", "conway.test", "conway.scenarios"]

from conway.util.command_parser                                 import CommandParser
from conway.util.dataframe_utils                                import DataFrameUtils
from conway.util.profiler                                       import Profiler
from conway.util.timestamp                                      import Timestamp

from conway_ops.repo_admin.repo_statics                         import RepoStatics
from conway_ops.repo_admin.repo_administration                  import RepoAdministration
from conway_ops.repo_admin.chassis_repo_bundle                  import Chassis_RepoBundle


class Troubleshooter():

    def __init__(self):
        pass

    def run(self):
        '''
        '''                                           
        # Select what to troubleshoot, and comment out whatever we are not troubleshooting
        #
        with Profiler("Troubleshooting"):
            # self.some_other_thing_to_do()
            #self.troubleshoot_repo_report()

            s = 'git config --local user.name "alejandro-fin"'
            args_list                                           = CommandParser().get_argument_list(s)
            print(args_list)
        
    def troubleshoot_repo_report(self):
        '''
        '''
        CRB                                 = Chassis_RepoBundle()
        PUBLICATION_FOLDER                  = "C:/Alex/tmp2"
        
        conway_admin                        = RepoAdministration(local_root     = CONWAY_ROOT_FORK, 
                                                                remote_root     = REMOTE_CONWAY_FORK_ROOT, 
                                                                repo_bundle     = CRB)
        conway_admin.create_repo_report(publications_folder     = PUBLICATION_FOLDER, 
                                        repos_in_scope_l        = CONWAY_LOCAL_REPOS)



        
if __name__ == "__main__":
    # execute only if run as a script
    def main(args):    
        troubleshooter                                              = Troubleshooter()    
        troubleshooter.run()

    main(_sys.argv)