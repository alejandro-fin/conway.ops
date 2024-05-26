from httpx                                                  import AsyncClient

from conway.application.application                         import Application
from conway.util.secrets                                    import Secrets

from conway_ops.util.github_response_handler                import GitHub_ReponseHandler

class GitHub_Client():

    '''
    Asynchronous context manager used to invoke GitHub APIs

    :param str github_owner: the GitHub account under which we will be invoking GitHub APIs. May be a user or an
        organization.
    '''
    def __init__(self, github_owner):
        self.github_owner                       = github_owner
        self.async_client                       = None # will be created in enter

        # We need to enforce that this context manager instance is only entered once at a time, since if two
        # threads enter it at the same time, the second one will reset the pointer to the
        # self.async_client, leaving a dangling HTTP connection and/or causing problems with resources being closed
        # by one thread that affects the other thread. 
        self.reference_counter                  = 0

    async def __aenter__(self):
        '''
        '''
        self.reference_counter                  += 1
        if self.reference_counter > 1:
            raise ValueError("Invalid use of the GitHub_Client context manager: you are entering the same context"
                             + " a second time, before the first traversal through this context has closed.")
        self.async_client                       = AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        '''
        '''
        await self.async_client.aclose()
        self.reference_counter                  -= 1

    async def GET(self, resource, sub_path):
        '''
        Invokes the "GET" HTTP verb on the GitHub API specified by the parameters.

        :param str resource: indicates the top resource for the API. For example, "{owner}/repos". 
        :param str sub_path: Indicates the path of a desired sub-resource to get, under the URL for the
            `resource`. Examples: "/commits/master", "/branches", "/pulls" 

        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        result                                  = await self._http_call("GET", resource=resource, sub_path=sub_path, body={}, )
        return result
    
    async def POST(self, resource, sub_path, body):
        '''
        Invokes the "POST" HTTP verb on the Git Hub API to create a resource associated to this inspector's repo.

        :param str resource: indicates the top resource for the API. For example, "{owner}/repos". 
        :param str sub_path: Indicates the path of a desired sub-resource to create, under the URL for the
            `resource`. Examples: "/commits/master", "/branches", "/pulls" 
        :param dict|list body: JSON object to submit in the HTTP request.
        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        result                                  = await self._http_call("POST", resource=resource, sub_path=sub_path, body=body)
        return result
    
    async def PUT(self, resource, sub_path, body):
        '''
        Invokes the "PUT" HTTP verb on the Git Hub API to update a resource associated to this inspector's repo.

        :param str resource: indicates the top resource for the API. For example, "{owner}/repos".
        :param str sub_path: Indicates the path of a desired sub-resource to update, under the URL for the
            `resource`. Examples: "/commits/master", "/branches", "/pulls" 
 
        :param dict|list body: JSON object to submit in the HTTP request.
        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        result                                  = await self._http_call("PUT", sub_path=sub_path, body=body, resource=resource)
        return result
           
    async def DELETE(self, resource, sub_path):
        '''
        Invokes the "DELETE" HTTP verb on the Git Hub API to update a resource associated to this inspector's repo.

        :param str resource: indicates the top resource for the API. For example, "{owner}/repos". 
        :param str sub_path: Indicates the path of a desired sub-resource to delete, under the URL for the
            `resource`. Examples: "/commits/master", "/branches", "/pulls" 

        :param dict body: payload to submit in the HTTP request.
        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        result                                  = await self._http_call("DELETE", sub_path=sub_path, resource=resource)
        return result
        
    async def _http_call(self, method, resource, sub_path, body={}):
        '''
        Invokes the Git Hub API specified by the parameters.

        :param str method: the HTTP verb to use ("GET", "POST", or "PUT")
        :param str sub_path: Indicates the path of a desired sub-resource to delete, under the URL for the
            `resource`. Examples: "/commits/master", "/branches", "/pulls" 
        :param str resource: indicates the top resource for the API. For example, "repos". It is an optional
            argument that defaults to "repos" if it is not provided.
        :param dict body: optional payload to submit in the HTTP request. 
        :return: A Json representation of the resource as given by the GitHub API
        :rtype: str
        '''
        GIT_HUB_API                         = f"https://api.github.com"
 
        match resource:
            case "repos" | "orgs" | "users":
                url                   = f"{GIT_HUB_API}/{resource}/{self.github_owner}{sub_path}"
            case "user":
                # GOTCHA:
                #       The "user" resource represents the currently authenticated user. As opposed to the "users"
                #   resource, which can manipulate "other" users different from the currently authenticated user.
                #   To create/update repos for a user, use the "user" resource, not the "users" resource.
                url                   = f"{GIT_HUB_API}/user{sub_path}"
            case "": # Return meta information
                url                   = f"{GIT_HUB_API}"
            case _:
                raise ValueError(f"Unsupported GitHub resource '{resource}'")
            
        # Uncomment to debug
        #APP.log(f"... calling '{method} {url}'")
        
        headers = {
            'Authorization': 'Bearer ' + Secrets.GIT_HUB_TOKEN(),
            'Content-Type' : 'application/json',
            # GOTCHA:
            #       Painfully found that GitHub post APIs will only work with the "vnd.github*" MIME types
            #'Accept'       : 'application/json'
            'Accept'        : 'application/vnd.github+json'
            
        }

        # Before making the HTTP call, make some pre-flight checks. 
        #
        self._check_readiness()

        # Now that we did our pre-flight check, make the HTTP call
        try:
            response                        = await self.async_client.request(   
                                                                method          = method, 
                                                                url             = url, 
                                                                json            = body,
                                                                headers         = headers, 
                                                                timeout         = 20) 
            

        except Exception as ex:
            raise ValueError("Problem connecting to Git Hub. Error is: " + str(ex))
        
        return GitHub_ReponseHandler().process(response)    


    def _check_readiness(self):
        '''
        Helper method intended to be called before invoking `self.async_client` methods that make HTTP calls.

        If any of its checks fails, it raises a ValueError. Else it returns None.
        
        Motivation for these checks:
            1.  This class `GitHub_Client` is an async context manager, and callers should only use it that
                way. So if the caller is making HTTP calls via `GitHub_Client` but using an instance X of it 
                that is not within an "async with X" statement, then we want to error out.
            2.  Even if the caller initially made HTTP calls correctly using an instance X of `GitHub_Client`
                via an `async with X` statement, we want to make sure the caller does not reuse of that instance X
                outside of that `async with X` statement, since upon exiting the `asycn with X` statement
                we closed the `self.async_client`, and it will error out with hard to track error message
                like "ClosedResourceError". By pre-empting such errors via this `_check_readiness` check,
                we can cause the error to instead be triggered by the Conway code base, making it more obvious
                to see the caller code base that led to the problem, by inspecting the error's stack trace.
        '''
        if self.async_client is None:
            raise ValueError("Invalid use of GitHub_Client methods: please invoke them only within an "
                             + "`asycn with X` statement, where `X` is an instance of `GitHub_Client")
        
        if self.async_client.is_closed:
            raise ValueError("Invalid reuse of GitHub_Client instance since it is already closed. "
                             + "This can happen when you reuse a prior GitHub_Client instance outside its "
                             + "original `async with  ...` statement.")