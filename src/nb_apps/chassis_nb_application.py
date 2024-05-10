import os                                                           as _os

from conway.application.application                                 import Application

from conway.observability.logger                                    import Logger

class NB_Logger(Logger):
    '''
    This is a mock logger, needed in order to run conway services in a Jupyter notebook.

    Specifically, it is needed by the :class:`Chassis_NB_Application`. Please refer to its
    documentation as to why these mock classes are needed in order to run conway services.
    '''


class Chassis_NB_Application(Application):

    '''
    This is a mock application, which is needed in order to run the conway library methods in a
    notebook.


    This is needed because the :class:`conway` requires that any business logic be run under
    the context of a global :class:`Application` object, which is normally the case for real applications, or 
    for tests of real applications.

    So in order to run notebooks (whether to manage repo lifecycles, seed scenarios or just troubleshooting)
    without a real application, we use this (mock) Application as a global context.

    Hence this class, which is initialized in ``notebooks.chassis_nb_utils.py``
    '''
    def __init__(self):

        APP_NAME                                        = "ChassisNotebookApp"

        logger                                          = NB_Logger(activation_level=Logger.LEVEL_INFO)
          
        # __file__ is something like 
        #
        #   'C:\Alex\Code\conway\conway.ops\src\notebooks\chassis_nb_application.py'
        #
        #
        # So to get the project folder ("conway") we need to go 3 directories up
        #
        directory                                       = _os.path.dirname(__file__)

        for idx in range(3):
            directory                                   = _os.path.dirname(directory)
        project_directory                               = directory   
        config_path                                     = project_directory + "/config"     
          
        super().__init__(app_name=APP_NAME, config_path=config_path, logger=logger)

