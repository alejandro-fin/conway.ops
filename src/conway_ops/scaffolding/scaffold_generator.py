from jinja2                                                 import Environment, FileSystemLoader
from pathlib                                                import Path
import itertools

from conway.util.case_utils                                 import CaseUtils
from conway_ops.scaffolding.scaffolding_statics             import ScaffoldingStatics

class ScaffoldGenerator():

    '''
    Class used to scaffold new projects adhering to the Conway design patterns. It creates a project structure containing
    all the mandatory repos for a Conway application, and generates Python code and other necessary files to populate
    the project folders with sample implementation of services, tests and documentation.

    This class allows for different types of projects to be generated. For example, maybe some projects need scaffolding
    for a CLI, a UI or a web server, whereas other projects don't. To support this, code generation is dependent on the notion 
    of a :class:``ScaffoldSpec``. Code generating is normally driven from templates, and different templates are used
    depending on the concrete instance of a :class:``ScaffoldSpec`` that is passed to the constructor of this class.
    '''
    def __init__(self, project_root, spec):
        self.project_root                                   = project_root
        self.spec                                           = spec

    def generate(self, subproject):
        '''
        Generates sample code for a particular repo, as per the templates specified in ``self.spec``.

        :param str subproject:  the subfolder of a project that correspond to the particular repo, config or other area 
            for which this method will generate scaffolding code. It is needed because
            a project usually consists of multiple repos (as sub-folders of the root project folder), as well as a (runtime) config
            folder external from all repos, and scaffolding generation is done one repo at a time.
        '''
        generated_files_l                                   = []
        func_dict                                           = self._get_additional_template_functions()
        if subproject == "config": # Special case
            subproject_templates                            = f"{self.spec.templates_root}/config"
        else: # we are generating code for a repo, folder structure is templated
            subproject_templates                            = f"{self.spec.templates_root}/{ScaffoldingStatics.PARAMS}.{ScaffoldingStatics.PROJECT_PARAM}.{subproject}"
        environment                                         = Environment(loader=FileSystemLoader(subproject_templates))
        for template_relative_path in environment.list_templates():
            template                                        = environment.get_template(template_relative_path)
            template.globals.update(func_dict)
            destination_templated_filename                  = f"{self.project_root}/{template_relative_path}"
            destination_filenames_l                         = self._eval_templated_path(destination_templated_filename, 
                                                                                        self.spec.variables_dict)
            for destination in destination_filenames_l:
                content = template.render(
                    self.spec.variables_dict
                )
                destination_path                                = Path(destination).parent.as_posix()
                Path(destination_path).mkdir(parents=True, exist_ok=True)
                with open(destination, mode="w", encoding="utf-8") as generated_file:
                    generated_file.write(content)
                    generated_files_l.append(destination)

        return generated_files_l
    
    def _get_additional_template_functions(self):
        '''
        Returns a dictionary where the keys are strings and the values are Python callables.

        The intention is to pass this functions dictionary to Jinja templates' globals, as a way to enrich the Jinja
        primitives with additional functions that can be called in the Jinja constructs.
        This was inspired by https://saidvandeklundert.net/2020-12-24-python-functions-in-jinja/
        '''
        SS                                              = ScaffoldingStatics
        CU                                              = CaseUtils
        P                                               = self.spec.variables_dict[SS.PARAMS]
        func_dict = {
            "camel":                                    CU.as_camel,
            "pascal":                                   CU.as_pascal,
            "snake":                                    CU.as_snake,
            "kebab":                                    CU.as_kebab,
            "static":                                   CU.as_static,

            "LOGGER":                                   lambda: CU.as_static(P[SS.APP_CODE_PARAM]) + "_Logger",
            "logger":                                   lambda: P[SS.APP_CODE_PARAM] + "_logger",
            "SCENARIOS":                                lambda: CU.as_static(P[SS.APP_CODE_PARAM]) + "_SCENARIOS_REPO",
            "APP":                                      lambda: CU.as_static(P[SS.APP_CODE_PARAM]),
        }
        return func_dict


    def _eval_templated_path_part(self, path_part, variables_dict):
        '''
        Helper method to modify *path_part* names that are using template variables
        (a *path_part* is either a folder or a filename).

        It is a building block for ``self._eval_templated_path``, whereby the latter breaks a path into 
        the component path_parts and uses this method to evaluate each path_part separately.

        Additionally, a templated path_part may evaluate to one or multiple path_parts, depending on whether
        the ``variable_dict`` tree of entries is a :class:``str`` or a :class:``list``.

        For that reason, this method returns a list.

        For example, if ``variables_dict["p"]["project"] == "cash"``, then if ``path_part == "p.project.svc"``
        the method will return ``[cash.svc]``

        As an example of multiple path_parts, if ``variables_dict["p"]["svc"] == ["pricing", "reporting"],
        then if ``path_part == p.svc._config``, then this method will return 
        ["pricing_config", "reporting_config"]

        :param str path_part: a posibly templated path_part or filename. Example: ``"p.project"``
        :param dict variables_dict: dictionary defining the template variables, possibly nested across subdictionaries.
        :return: a modified path_part where templated strings are replaced by their values.
        :rtype: list[str]
        '''
        tokens = path_part.split(".")
        if len(tokens) == 0 or not tokens[0] in variables_dict.keys(): # Hit bottom - nothing templated in the path
            return [path_part]
        
        # If we get here, then we had a match, so the path includes templates
        val                                                 = variables_dict[tokens[0]]
        tail_path_part                                         = ".".join(tokens[1:])
        
        if type(val)==dict: # we need to recurse
            return self._eval_templated_path_part(tail_path_part, val)
        elif type(val)==list:
            return [f"{str(item)}{tail_path_part}" for item in val]
        else:
            return [f"{str(val)}{tail_path_part}"]
        
    def _eval_templated_path(self, path, variables_dict):
        '''
        Helper method to evaluate template variables in a templated path and return the resulting path.

        It returns a list, since it is possible for a templated path to evaluate to multiple concrete
        paths.

        For example, if 
        
        .. code-block::
        
            path == p.project.svc/src/p.app/__init__.py"
            
        then this mehod will return

        .. code-block::
        
            ["cash.svc/src/cash_management/__init__.py"]
            
        provided that 

        * ``variables_dict["p"]["project"] == "cash"``
        * and ``variables_dict["p"]["app_name"] == "cash_management"``

        :param str path: a posibly templated path_part or filename. Example: ``"p.project.svc/src/p.app/__init__.py"``
        :param dict variables_dict: dictionary defining the template variables, possibly nested across subdictionaries.
            Some template variables might be defined as lists, meaning that each item in the list is a possible
            value for evaluating the templated path.
        :return: a modified path where templated strings are replaced by their values.
        :rtype: list[str]
        '''
        # evaluated_parts is a list of lists. The first index corresponds to each part x 
        # in the templated path. The second index corresponds to all the possible path paths that x might evaluate to.
        evaluated_parts                                 = [] 
        for templated_path_part in Path(path).parts:
            path_part_l                                 =  self._eval_templated_path_part(templated_path_part, 
                                                                                             variables_dict)
            evaluated_parts.append(path_part_l)

        # Now we must process the "list of lists", and allow for all combinations, in the following sense:
        #
        #   Say the first member of evaluated parts is [x1, x2, .., x5]
        #       and the second member is [y1]
        #       and the third is [z1, z2,..., z6]
        #
        #   Then we will crete a list of paths "xi/yj/zk" for all combinations of i=1, ...6, j-1, and z=1, ..., 6
        #
        result_l                                        = []
        
        # The asterisk in *evaluated_parts unbundles the list so that we can pass a non-deterministic
        # number of arguments to itertools.product. Each such argument is one of the inner lists in evaluated_parts
        # (recall that evaluated_parts is a list of lists)
        for combination in itertools.product(*evaluated_parts):
            result_l.append("/".join(combination))

        return result_l
