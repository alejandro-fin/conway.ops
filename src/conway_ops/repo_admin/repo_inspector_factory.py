from pathlib                                            import Path

from conway_ops.repo_admin.filesystem_repo_inspector    import FileSystem_RepoInspector
from conway_ops.repo_admin.github_repo_inspector        import GitHub_RepoInspector

class RepoInspectorFactory():

    '''
    Factory used to choosing and instantiating instantiate a concrete class derived from RepoInspector based
    on the path or URL of the repo.

    For example, if a filesystem path is given for the repo, then it will instantiate a 
    :class:`FileSystem_RepoInspector`, whild if a ``github.com`` URL is given, it will instantiate a 
    :class:`GitHub_RepoInspector.
    '''
    def __init__(self):
        pass

    # Want to match GitHub URLs, which as per CCL policies must include the user name, so typically might look like
    #
    #       'https://alejandro-fin@github.com/alejandro-fin/conway.svc'
    #
    GIT_HUB_URL_MATCH                                   = "@github.com/"
    def findInspector(parent_url, repo_name):
        '''
        :param str parent_url: A string identifying the location under which the repo of interest lives as
            a "subfolder" or "sub resource". May be a path to the local file system or the URL to a remote server.
        :param str repo_name: A string identifying the name of the repo of interest, as a "subfolder"
            or "sub resource" under the ``parent_url``.

        :return: An instance of a concrete class extending :class:`RepoInspector`
        '''    
        full_path                                       = parent_url + "/" + repo_name
        if Path(full_path).exists():
            inspector                                   = FileSystem_RepoInspector(parent_url, repo_name)
        elif RepoInspectorFactory.GIT_HUB_URL_MATCH in parent_url:
            inspector                                   = GitHub_RepoInspector(parent_url, repo_name)
        else:
            raise ValueError("No repo inspector is available for '" + full_path + "'")
        
        return inspector
