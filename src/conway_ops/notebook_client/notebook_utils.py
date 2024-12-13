import os                                                           as _os
import git                                                          as _git
import sys                                                          as _sys

import abc

from conway.application.application                                 import Application

class NotebookUtils(abc.ABC):

    '''
    Utility class containing useful methods to invoke in notebooks associated to the development-time and runtime
    operations of a Conway-based application.
    
    It is expected to be used as a singleton: construct it only once and use it throughout a notebook.

    It also handles some environmental needs, such as:

    * Automatically importing required modules as part of constructing an instance of this class. This makes
      notebooks less cluttered by not having to include them in the notebook itself.

    * Also on construction, it will get, maintain and display information about which application environment is being used
      to run the notebook using this class. 

    :param str project_name: name of Conway-based application. Used in displays and to access names of repos
    :param repo_directory: path to the repo containing the Python file that implementes the concrete class for
                instantiated by self.
    '''
    def __init__(self, project_name, repo_directory):

        self.repo_directory             = repo_directory

        self.project_name               = project_name

        self._display_environment()
        self._import_dependencies()
        self._import_conway_dependencies()

    def flush_logs(self):
        '''
        This method is only applicable for derived classes associated to Conway Applications that configure
        logs to use schedule-based logging, i.e., to log in the order the code was written, not in the order
        the code was executed. The two may differ when using asyncio due to the non-deterministic nature of
        the order in which the asyncio event loop executes tasks.

        See conway.async_tuils.schedule_based_log_sorter.py for more information on schedule-based logging.

        For such situations, this method will invoke the `conway.observability.logger.Logger.flush` method.
        '''
        Application.app().logger.flush()

    def _import_dependencies(self):
        '''
        Imports common Python modules that are often needed in TVM notebooks, and remembers them as attributes
        of self
        '''
        import time
        from pathlib                    import Path
        import pandas                   
        import git
        import random
        import xlsxwriter
        import git
        import inspect

        self.time                       = time
        self.Path                       = Path
        self.pandas                     = pandas
        self.git                        = git
        self.random                     = random
        self.xlsxwriter                 = xlsxwriter
        self.git                        = git
        self.inspect                    = inspect

    def _import_conway_dependencies(self):
        '''
        Imports common Conway modules that are often needed in application notebooks, and remembers them as attributes
        of self
        '''

        # NB: If you are reading this code in an IDE, it is possible that the imports below are shown by the
        #   IDE as if they are not found. That is not correct - IDEs are confused because the path to these
        #   modules was added dynamically by the call to self._display_environment(), which happens
        #   before this method is called
        #
        from conway_ops.repo_admin.branch_lifecycle_manager                     import BranchLifecycleManager
        from conway_ops.repo_admin.repo_administration                          import RepoAdministration
        from conway_ops.repo_admin.github_repo_inspector                        import GitHub_RepoInspector
        from conway_ops.onboarding.chassis_repo_bundle                          import Chassis_RepoBundle
        from conway_ops.onboarding.repo_setup                                   import RepoSetup
        from conway_ops.scaffolding.scaffold_generator                          import ScaffoldGenerator
        from conway_ops.scaffolding.scaffold_spec                               import ScaffoldSpec
        from conway_ops.util.git_branches                                       import GitBranches
        from conway_ops.util.git_local_client                                   import GitLocalClient
        
        from conway.application.application                                     import Application
        from conway.async_utils.schedule_based_log_sorter                       import ScheduleBasedLogSorter
        from conway.util.dataframe_utils                                        import DataFrameUtils
        from conway.util.path_utils                                             import PathUtils
        from conway.util.timestamp                                              import Timestamp
        from conway.util.profiler                                               import Profiler
        from conway.util.yaml_utils                                             import YAML_Utils
        from conway.database.data_accessor                                      import DataAccessor
        from conway.reports.report_writer                                       import ReportWriter

        self.BranchLifecycleManager             = BranchLifecycleManager
        self.GitHub_RepoInspector               = GitHub_RepoInspector
        self.RepoAdministration                 = RepoAdministration
        self.Chassis_RepoBundle                 = Chassis_RepoBundle
        self.RepoSetup                          = RepoSetup
        self.ScaffoldGenerator                  = ScaffoldGenerator
        self.ScaffoldSpec                       = ScaffoldSpec
        self.GitBranches                        = GitBranches
        self.GitLocalClient                          = GitLocalClient

        self.Application                        = Application
        self.ScheduleBasedLogSorter             = ScheduleBasedLogSorter
        self.DataFrameUtils                     = DataFrameUtils
        self.PathUtils                          = PathUtils
        self.Timestamp                          = Timestamp
        self.Profiler                           = Profiler
        self.YAML_Utils                         = YAML_Utils
        self.DataAccessor                       = DataAccessor
        self.ReportWriter                       = ReportWriter

        self.DFU                                = DataFrameUtils()

    def _display_environment(self):
        '''
        Remembers environmental information as part of self, and displays it.
        '''
        REPO_NAME                       = _os.path.basename(self.repo_directory)
        REPO_BRANCH                     = _git.cmd.Git(self.repo_directory).execute(command = ["git", "rev-parse", "--abbrev-ref", "HEAD"])#,
                                                                                    #env     = _os.environ)

        APP_INSTALLATION_PATH           = _os.path.dirname(self.repo_directory) 
        APP_INSTALLATION                = _os.path.basename(APP_INSTALLATION_PATH)

        # This is intended to make it possible to application modules. For example, if the application
        # is called "foo", this would add "foo.svc/src" and "foo.ops/src" to the path.
        for repo_type in ["svc", "ops"]:
            _sys.path.append(APP_INSTALLATION_PATH + "/" + self.project_name + "." + repo_type + "/src")

        self.repo_name                  = REPO_NAME
        self.repo_branch                = REPO_BRANCH
        self.installation               = APP_INSTALLATION
        self.installation_path          = APP_INSTALLATION_PATH

        MARGIN                    = "    "
        # For color codes, see https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
        INVERSED_BLUE                   = "\033[34m\033[7m"
        RESET_COLORS                    = "\033[0m"
        INVERSED_GREEN                  = "\033[32m\033[7m"

        def display(label, msg, set_color, unset_color):
            print(label + set_color + MARGIN + msg + MARGIN + unset_color)

        display(self.project_name.upper() + " installation:            ", APP_INSTALLATION, INVERSED_BLUE, RESET_COLORS)
        display("Jupyter using repo[branch]:  ", REPO_NAME + "[" + REPO_BRANCH + "]",       INVERSED_GREEN, RESET_COLORS)
        display("Installation path:           ", APP_INSTALLATION_PATH,                     INVERSED_BLUE, RESET_COLORS)
        display("Application:                 ", str(Application.app().__class__),          INVERSED_GREEN, RESET_COLORS)
