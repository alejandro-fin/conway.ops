from conway.database.single_root_data_hub                      import SingleRootDataHub, DataHubHandle

class Repos_DataHub(SingleRootDataHub):

    '''
    Class to assist operator to manage the multiple repos that comprise a ConwayApplication solution

    :param str hub_handle: Folder or URL of the parent containing all application-related GIT repos.

    '''
    def __init__(self, name: str, hub_handle: DataHubHandle):

        super().__init__(name, hub_handle)

    def _instantiate(self, name, hub_handle):

        return Repos_DataHub(self.name, name, hub_handle)

