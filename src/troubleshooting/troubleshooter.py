import asyncio
import sys                                                                  as _sys

CODING_ROOT = "/home/alex/consultant1@CCL/dev"

MODULE_PATHS = [CODING_ROOT + "/conway_ops/src"]
import sys
sys.path.extend(MODULE_PATHS)

CONWAY_ROOT_FORK            = CODING_ROOT + "/conway_fork"
REMOTE_CONWAY_FORK_ROOT     = 'https://alejandro-fin@github.com/alejandro-fin'
CONWAY_LOCAL_REPOS          = ["conway.svc", "conway.acceptance", "conway.ops", "conway.test", "conway.scenarios"]

from conway.async_utils.schedule_based_log_sorter               import ScheduleBasedLogSorter
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
            
                #runner.run(self.create_pull_request())
                #runner.run(self.troubleshoot_repo_report())
                runner.run(self.troubleshoot_scheduled_based_sorter())

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
        
    def troubleshoot_scheduled_based_sorter(self):
        '''
        '''
        log_lines                           = [{'message': '\n----------- conway.acceptance (local) -----------', 'labels': {'timestamp': '56.245 sec', 'thread': 'MainThread', 'task': 'Task-12', 'source': 'branch_lifecycle_manager:491'}}, {'message': "local = '/home/alex/consultant1@FIN/dev/conway_fork/conway.acceptance'", 'labels': {'timestamp': '56.251 sec', 'thread': 'MainThread', 'task': 'Task-12', 'source': 'filesystem_repo_inspector:370', 'scheduling_context': {'timestamp': '56.209 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': '\n----------- conway.svc (local) -----------', 'labels': {'timestamp': '56.256 sec', 'thread': 'MainThread', 'task': 'Task-13', 'source': 'branch_lifecycle_manager:491'}}, {'message': "local = '/home/alex/consultant1@FIN/dev/conway_fork/conway.svc'", 'labels': {'timestamp': '56.260 sec', 'thread': 'MainThread', 'task': 'Task-13', 'source': 'filesystem_repo_inspector:370', 'scheduling_context': {'timestamp': '56.232 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': '\n----------- conway.scenarios (local) -----------', 'labels': {'timestamp': '56.263 sec', 'thread': 'MainThread', 'task': 'Task-14', 'source': 'branch_lifecycle_manager:491'}}, {'message': "local = '/home/alex/consultant1@FIN/dev/conway_fork/conway.scenarios'", 'labels': {'timestamp': '56.267 sec', 'thread': 'MainThread', 'task': 'Task-14', 'source': 'filesystem_repo_inspector:370', 'scheduling_context': {'timestamp': '56.226 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': '\n----------- conway.test (local) -----------', 'labels': {'timestamp': '56.272 sec', 'thread': 'MainThread', 'task': 'Task-15', 'source': 'branch_lifecycle_manager:491'}}, {'message': "local = '/home/alex/consultant1@FIN/dev/conway_fork/conway.test'", 'labels': {'timestamp': '56.278 sec', 'thread': 'MainThread', 'task': 'Task-15', 'source': 'filesystem_repo_inspector:370', 'scheduling_context': {'timestamp': '56.239 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': '\n----------- conway.ops (local) -----------', 'labels': {'timestamp': '56.282 sec', 'thread': 'MainThread', 'task': 'Task-16', 'source': 'branch_lifecycle_manager:491'}}, {'message': "local = '/home/alex/consultant1@FIN/dev/conway_fork/conway.ops'", 'labels': {'timestamp': '56.288 sec', 'thread': 'MainThread', 'task': 'Task-16', 'source': 'filesystem_repo_inspector:370', 'scheduling_context': {'timestamp': '56.218 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "@ 'integration' (local):\n\nYour branch is up to date with 'origin/integration'.", 'labels': {'timestamp': '56.300 sec', 'thread': 'MainThread', 'task': 'Task-12', 'source': 'filesystem_repo_inspector:379', 'scheduling_context': {'timestamp': '56.209 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "@ 'integration' (local):\n\nM\tsrc/conway_ops/repo_admin/branch_lifecycle_manager.py\nM\tsrc/conway_ops/repo_admin/filesystem_repo_inspector.py\nM\tsrc/conway_ops/repo_admin/github_repo_inspector.py\nM\tsrc/conway_ops/repo_admin/repo_administration.py\nM\tsrc/conway_ops/repo_admin/repo_inspector.py\nM\tsrc/troubleshooting/troubleshooter.py\nYour branch is up to date with 'origin/integration'.", 'labels': {'timestamp': '56.308 sec', 'thread': 'MainThread', 'task': 'Task-16', 'source': 'filesystem_repo_inspector:379', 'scheduling_context': {'timestamp': '56.218 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "@ 'integration' (local):\n\nYour branch is up to date with 'origin/integration'.", 'labels': {'timestamp': '56.314 sec', 'thread': 'MainThread', 'task': 'Task-15', 'source': 'filesystem_repo_inspector:379', 'scheduling_context': {'timestamp': '56.239 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "@ 'integration' (local):\n\nYour branch is up to date with 'origin/integration'.", 'labels': {'timestamp': '56.319 sec', 'thread': 'MainThread', 'task': 'Task-14', 'source': 'filesystem_repo_inspector:379', 'scheduling_context': {'timestamp': '56.226 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "@ 'integration' (local):\n\nM\tsrc/conway/async_utils/schedule_based_log_sorter.py\nYour branch is up to date with 'origin/integration'.", 'labels': {'timestamp': '56.325 sec', 'thread': 'MainThread', 'task': 'Task-13', 'source': 'filesystem_repo_inspector:379', 'scheduling_context': {'timestamp': '56.232 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "'integration' (remote) -> 'integration' (local):\n\nAlready up to date.", 'labels': {'timestamp': '58.343 sec', 'thread': 'MainThread', 'task': 'Task-16', 'source': 'filesystem_repo_inspector:383', 'scheduling_context': {'timestamp': '56.218 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "'integration' (remote) -> 'integration' (local):\n\nAlready up to date.", 'labels': {'timestamp': '58.350 sec', 'thread': 'MainThread', 'task': 'Task-12', 'source': 'filesystem_repo_inspector:383', 'scheduling_context': {'timestamp': '56.209 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "'integration' (remote) -> 'integration' (local):\n\nAlready up to date.", 'labels': {'timestamp': '58.356 sec', 'thread': 'MainThread', 'task': 'Task-15', 'source': 'filesystem_repo_inspector:383', 'scheduling_context': {'timestamp': '56.239 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "'integration' (remote) -> 'integration' (local):\n\nAlready up to date.", 'labels': {'timestamp': '58.362 sec', 'thread': 'MainThread', 'task': 'Task-13', 'source': 'filesystem_repo_inspector:383', 'scheduling_context': {'timestamp': '56.232 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "'integration' (remote) -> 'integration' (local):\n\nAlready up to date.", 'labels': {'timestamp': '58.369 sec', 'thread': 'MainThread', 'task': 'Task-14', 'source': 'filesystem_repo_inspector:383', 'scheduling_context': {'timestamp': '56.226 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "@ 'afin-onsite' (local):\n\nM\tsrc/conway_ops/repo_admin/branch_lifecycle_manager.py\nM\tsrc/conway_ops/repo_admin/filesystem_repo_inspector.py\nM\tsrc/conway_ops/repo_admin/github_repo_inspector.py\nM\tsrc/conway_ops/repo_admin/repo_administration.py\nM\tsrc/conway_ops/repo_admin/repo_inspector.py\nM\tsrc/troubleshooting/troubleshooter.py\nYour branch is up to date with 'origin/afin-onsite'.", 'labels': {'timestamp': '58.374 sec', 'thread': 'MainThread', 'task': 'Task-16', 'source': 'filesystem_repo_inspector:389', 'scheduling_context': {'timestamp': '56.218 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': '@ \'afin-onsite\' (local):\n\nYour branch is ahead of \'origin/afin-onsite\' by 2 commits.\n  (use "git push" to publish your local commits)', 'labels': {'timestamp': '58.382 sec', 'thread': 'MainThread', 'task': 'Task-12', 'source': 'filesystem_repo_inspector:389', 'scheduling_context': {'timestamp': '56.209 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': '@ \'afin-onsite\' (local):\n\nYour branch is ahead of \'origin/afin-onsite\' by 2 commits.\n  (use "git push" to publish your local commits)', 'labels': {'timestamp': '58.389 sec', 'thread': 'MainThread', 'task': 'Task-15', 'source': 'filesystem_repo_inspector:389', 'scheduling_context': {'timestamp': '56.239 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': '@ \'afin-onsite\' (local):\n\nYour branch is ahead of \'origin/afin-onsite\' by 2 commits.\n  (use "git push" to publish your local commits)', 'labels': {'timestamp': '58.396 sec', 'thread': 'MainThread', 'task': 'Task-14', 'source': 'filesystem_repo_inspector:389', 'scheduling_context': {'timestamp': '56.226 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': '@ \'afin-onsite\' (local):\n\nM\tsrc/conway/async_utils/schedule_based_log_sorter.py\nYour branch is ahead of \'origin/afin-onsite\' by 2 commits.\n  (use "git push" to publish your local commits)', 'labels': {'timestamp': '58.401 sec', 'thread': 'MainThread', 'task': 'Task-13', 'source': 'filesystem_repo_inspector:389', 'scheduling_context': {'timestamp': '56.232 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "'integration' (local) -> 'afin-onsite' (local):\n\nAlready up to date.", 'labels': {'timestamp': '58.411 sec', 'thread': 'MainThread', 'task': 'Task-16', 'source': 'filesystem_repo_inspector:348', 'scheduling_context': {'timestamp': '56.218 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "'integration' (local) -> 'afin-onsite' (local):\n\nAlready up to date.", 'labels': {'timestamp': '58.418 sec', 'thread': 'MainThread', 'task': 'Task-12', 'source': 'filesystem_repo_inspector:348', 'scheduling_context': {'timestamp': '56.209 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "'integration' (local) -> 'afin-onsite' (local):\n\nAlready up to date.", 'labels': {'timestamp': '58.423 sec', 'thread': 'MainThread', 'task': 'Task-15', 'source': 'filesystem_repo_inspector:348', 'scheduling_context': {'timestamp': '56.239 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "'integration' (local) -> 'afin-onsite' (local):\n\nAlready up to date.", 'labels': {'timestamp': '58.428 sec', 'thread': 'MainThread', 'task': 'Task-14', 'source': 'filesystem_repo_inspector:348', 'scheduling_context': {'timestamp': '56.226 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': "'integration' (local) -> 'afin-onsite' (local):\n\nAlready up to date.", 'labels': {'timestamp': '58.433 sec', 'thread': 'MainThread', 'task': 'Task-13', 'source': 'filesystem_repo_inspector:348', 'scheduling_context': {'timestamp': '56.232 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': 'branch_lifecycle_manager:538'}}}, {'message': 'Refresh from integration completed in 2.23 sec', 'labels': {'timestamp': '58.437 sec', 'thread': 'MainThread', 'task': 'Task-11', 'source': '<source location undetermined>'}}]
        
        SIZE                                                        = len(log_lines) #31
        FROM                                                        = 0
        UNTIL                                                       = SIZE
        input_lines                                                 = log_lines[FROM:UNTIL]
        sorter                                                      = ScheduleBasedLogSorter(input_lines)
        
        line1                                                       = sorter.cleaned_lines[FROM] #log_lines[FROM]
        line2                                                       = sorter.cleaned_lines[UNTIL-1] # log_lines[UNTIL-1]
        
        keys_l                                                      = [sorter._log_line_key(a_line) for a_line in sorter.cleaned_lines]
        
        print(keys_l)
        
        # When the bug was detected, these were the values:
        #
        # key1 = 
        # key2 = 
        #
        key1                                                        = sorter._log_line_key(line1)
        key2                                                        = sorter._log_line_key(line2)
        try:
            result_l                                                = sorter.sort()
        except Exception as ex:
            print(ex)
            
        return result_l



        
if __name__ == "__main__":
    # execute only if run as a script
    def main(args):    
        troubleshooter                                              = Troubleshooter()    
        troubleshooter.run()

    main(_sys.argv)