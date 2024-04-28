
class {{ p.calc }}ServiceConfig():

    '''
    Helper class used to hold all the properties that are part of the configuration for the {{ p.calc }}Service class.

    :param str {{ p.in_hub }}_hub: represents a path, URL or equivalent, serving as the root area for the 
        inputs that the {{ p.calc }}Service must rely on.

    :param str {{ p.out_hub }}_hub: represents a path, URL or equivalent to identify the root area under which 
        the {{ p.calc }}Service should store its results.

    :param dict policy: contains settings for the mathematical algorithms used by the {{ p.calc }}Service
    '''
    def __init__(self, {{ p.in_hub }}_hub, {{ p.out_hub }}_hub, policy):
        self.{{ p.in_hub }}_hub                          = {{ p.in_hub }}_hub
        self.{{ p.out_hub }}_hub                          = {{ p.out_hub }}_hub
        self.policy                                         = policy