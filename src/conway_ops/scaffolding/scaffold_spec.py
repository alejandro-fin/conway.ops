import os                                                       as _os

import conway_ops

class ScaffoldSpec():

    '''
    Data structure object that encapsulates the location in the file system for Jinja2 templates that should be
    used to generate a scaffold, i.e., a new project with sample default implementation of key patterns.

    :param str templates_root: A string representing the folder in the file system under which to find the templates
        needed for generating a scaffold. This folder should structure templates by partitioning them into subfolders,
        with each subfolder corresponding to each particular repo in the :class:``RepoBundle`` pertinent to the project being generated. 

    :param dict variables_dict: a dictionary setting the values for all the variables used in the templates from
        which the scaffolding code is to be generated. It may be hierarchical, i.e., may contain sub-dictionaries as a
        way to hierarchically structure how variables are categorized.

    '''
    def __init__(self, templates_root, variables_dict):
        self.templates_root                                     = templates_root
        self.variables_dict                                     = variables_dict

    def standard_templates_location():
        '''
        This is a class-static method that returns the location of the standard templates in the Conway distribution
        within which this function is invoked.

        It is a utility methods for other code (such as test cases) that need to know where standard templates are stored in order
        to, for example, create a ScaffoldSpec.

        For example, consider the standard template 101. Templates for it are stored in the Conway distribution under the
        ``conway.ops`` repo. If ``CONWAY_DISTRIBUTION`` is an environment variable for the Conway distribution, then templates
        and Python code would be in separate areas of the repo  ``CONWAY_DISTRIBUTION/conway.ops``.
    
        Specifically, a Python file like this one would be at

        .. code_block::

            $CONWAY_DISTRIBUTION/conway.ops/src/conway_ops/scaffolding/scaffold_spec.py

        but template 101 itself would be the folder

        .. code_block::

            $CONWAY_DISTRIBUTION/conway.ops/app_templates/101

        In such an example, this method would return ``$CONWAY_DISTRIBUTION/conway.ops/app_templates``.

        '''
        # location will initially be something like
        #
        #       '/mnt/c/Users/aleja/Documents/Code/conway/conway.ops/src/conway_ops/__init__.py'
        location                                        = conway_ops.__file__


        # After we go up the folder structure, location will be the repo folder. Something like
        #
        #       '/mnt/c/Users/aleja/Documents/Code/conway/conway.ops'
        for idx in range(3):
            location = _os.path.dirname(location)

        # Lastly, we now identify the folder for the templates itself

        templates_location                              = f"{location}/app_templates"
    
        return templates_location