
from conway.application.application                                 import Application
from conway.util.http_response_handler                              import HTTP_ResponseHandler

class GitHub_ReponseHandler(HTTP_ResponseHandler):

    '''
    '''
    def __init__(self):
        super().__init__()

    def process(self, parent_context, response):
        '''
        :param response: HTTP response object to process
        :type response: requests.models.Response
        
        :param parent_context: the SchedulingContext of a "parent". Typical use case would be that
            the "parent" is the SchedulingContext of a caller that directly or indirectly led to the call of this
            method.
        :type parent_context: conway.async_utils.scheduling_context.SchedulingContext

        :returns: The payload of the response, if the handler considers the response successful. Otherwise
                the handler will raise an exception.
        :rtype: dict
        '''
        status                                              = response.status_code
        url                                                 = response.url
        data                                                = self._as_json(response)

        # response.request is of type PreparedRequest 
        #   - see https://requests.readthedocs.io/en/latest/api/#requests.PreparedRequest
        #
        req                                                 = response.request
        match status:
            case 422:
                match data:
                    case {'message': 'Validation Failed',           \
                            'errors': [{                            \
                                    'resource': 'PullRequest',      \
                                    'code': 'custom',               \
                                    'message': msg                  \
                            }],                                     \
                            'documentation_url': doc_url}:
                        if not parent_context is None:
                            Application.app().log(f"PR ignored: '{msg}'", xlabels=parent_context.as_xlabel())
                        else:
                            Application.app().log(f"PR ignored: '{msg}'")
                        return None

                    case _:
                        self._fail(response)
            case _:         
                return super().process(response)
            

            