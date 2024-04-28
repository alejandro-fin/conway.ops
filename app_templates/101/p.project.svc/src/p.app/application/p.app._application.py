import os                                                               as _os

from conway.application.application                                     import Application
from {{ p.app }}.observability.{{ logger() }} import {{ LOGGER() }}

class {{ pascal(p.app) }}Application(Application):

    def __init__(self):

        APP_NAME                                        = "{{ pascal(p.app) }}"

        logger                                          = {{ LOGGER() }}(activation_level={{ LOGGER() }}.LEVEL_INFO)

        super().__init__(logger)
          
        # __file__ is something like 
        #
        #   'C:\Alex\Code\{{ p.project }}\{{ p.project}}.svc\src\{{ p.app }}\application\{{ p.app}}_application.py'
        #
        #
        # So to get the project folder ("{{ p.project }}") we need to go 4 directories up
        #
        directory                                       = _os.path.dirname(__file__)

        for idx in range(4):
            directory                                   = _os.path.dirname(directory)
        project_directory                               = directory   
        config_path                                     = project_directory + "/config"     
          
        super().__init__(app_name=APP_NAME, config_path=config_path, logger=logger)