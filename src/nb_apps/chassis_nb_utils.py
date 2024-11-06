import os                                                           as _os

from conway_ops.notebook_client.notebook_utils                      import NotebookUtils

from conway.application.application                                 import Application

from chassis_nb_application                                        import Chassis_NB_Application

# Start the global singleton that represents a (mock) application based on 
# :class:`conway`, so that the notebooks can invoke class:`conway` services (since anything based on the class:`conway`
# requires a global :class:`Application` object to exist as context)
#
if Application._singleton_app is None:
    Chassis_NB_Application()


class Chassis_NB_Utils(NotebookUtils):

    '''
    '''
    def __init__(self):

        # __file__ is something like 
        #
        #   'C:\Alex\Code\conway\conway.ops\src\notebooks\chassis_nb_utils.py'
        #
        # So to get the chassis repo ("conway.ops") we need to go 2 directories up
        #
        directory                       = _os.path.dirname(__file__)

        for idx in range(2):
            directory                   = _os.path.dirname(directory)
        repo_directory                  = directory

        super().__init__(project_name="conway", repo_directory=repo_directory)

    def _import_conway_dependencies(self):
        '''
        Imports common Conway modules that are often needed in application notebooks, and remembers them as attributes
        of self
        '''
        super()._import_conway_dependencies()
        
        # NB: If you are reading this code in an IDE, it is possible that the imports below are shown by the
        #   IDE as if they are not found. That is not correct - IDEs are confused because the path to these
        #   modules was added dynamically by the call to self._display_environment(), which happens
        #   before this method is called
        #
        from conway_ops.onboarding.repo_bundle_factory                          import RepoBundleFactory

        self.RepoBundleFactory                 = RepoBundleFactory



