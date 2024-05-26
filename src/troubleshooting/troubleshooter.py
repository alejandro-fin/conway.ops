import asyncio
import sys                                                                  as _sys

CODING_ROOT = "/home/alex/consultant1@CCL/dev"

MODULE_PATHS = [CODING_ROOT + "/conway_ops/src"]
import sys
sys.path.extend(MODULE_PATHS)

CONWAY_ROOT_FORK            = CODING_ROOT + "/conway_fork"
REMOTE_CONWAY_FORK_ROOT     = 'https://alejandro-fin@github.com/alejandro-fin'
CONWAY_LOCAL_REPOS          = ["conway.svc", "conway.acceptance", "conway.ops", "conway.test", "conway.scenarios"]

from conway.util.command_parser                                 import CommandParser
from conway.util.dataframe_utils                                import DataFrameUtils
from conway.util.profiler                                       import Profiler
from conway.util.timestamp                                      import Timestamp

from conway_ops.onboarding.chassis_repo_bundle                  import Chassis_RepoBundle
from conway_ops.repo_admin.github_repo_inspector                import GitHub_RepoInspector
from conway_ops.repo_admin.repo_statics                         import RepoStatics
from conway_ops.repo_admin.repo_administration                  import RepoAdministration

class Troubleshooter():

    def __init__(self):
        pass

    def run(self):
        '''
        '''                                           
        # Select what to troubleshoot, and comment out whatever we are not troubleshooting
        #
        with Profiler("Troubleshooting"):
            with asyncio.Runner() as runner:
            
                runner.run(self.create_pull_request())
                #runner.run(self.troubleshoot_repo_report())

    async def create_pull_request(self):
        '''
        '''
        # Pre-flight: need to initialize an application since the GitHub_RepoInspector will  need to read an
        # application profile in order to get the GitHub token
        #
        SDLC_ROOT                           = "/home/alex/admin1@CCL/sdlc/"

        SDLC_MODULE_PATHS                   = [f"{SDLC_ROOT}/sdlc.ops/nb_apps"]
        sys.path.extend(SDLC_MODULE_PATHS)
        from sdlc_nb_application                                        import SDLC_NB_Application
        SDLC_NB_Application()

        # Now the main troubleshooting
        REPO_NAME = 'conway.ops'
        gh                                  = GitHub_RepoInspector(parent_url=REMOTE_CONWAY_FORK_ROOT, repo_name=REPO_NAME)
        pr1                                 = await gh.pull_request(    from_branch   = "integration", 
                                                                        to_branch     = "master", 
                                                                        title         = "Dummy PR for test purposes",
                                                                        body          = "Discard this PR")
        return pr1
        
    async def troubleshoot_repo_report(self):
        '''
        '''
        CRB                                 = Chassis_RepoBundle()
        PUBLICATION_FOLDER                  = "C:/Alex/tmp2"
        
        conway_admin                        = RepoAdministration(local_root     = CONWAY_ROOT_FORK, 
                                                                remote_root     = REMOTE_CONWAY_FORK_ROOT, 
                                                                repo_bundle     = CRB)
        await conway_admin.create_repo_report(publications_folder     = PUBLICATION_FOLDER, 
                                        repos_in_scope_l        = CONWAY_LOCAL_REPOS)



        
if __name__ == "__main__":
    # execute only if run as a script
    def main(args):    
        troubleshooter                                              = Troubleshooter()    
        troubleshooter.run()

    main(_sys.argv)