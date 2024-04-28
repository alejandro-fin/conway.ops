import abc

class ScaffoldingStatics(abc.ABC):

    '''
    Represents a static enum collection of static variables that are used in the scaffolding process for a new
    Conway application
    '''
    def __init__(self):
        pass

    PARAMS                                              = "p" # "params"

    AUTHOR_PARAM                                        = "author"
    AUTHOR_EMAIL_PARAM                                  = "author_email"
    PROJECT_DESCRIPTION_PARAM                           = "project_description"
    PROJECT_ROOT_PARAM                                  = "project_root"

    PROJECT_PARAM                                       = "project"
    APP_PARAM                                           = "app"
    APP_CODE_PARAM                                      = "app_code"

    CALC_SVC_PARAM                                      = "calc"
    CALC_SVC_RESOURCE                                   = "calc_resource"

    IMPORT_SVC_PARAM                                    = "import"
    IMPORT_SVC_RESOURCE                                 = "import_resource"

    INPUT_HUB_PARAM                                     = "in_hub"

    OUTPUT_HUB_PARAM                                    = "out_hub"




  

