
from conway.application.application                                 import Application
from conway.util.http_response_handler                              import HTTP_ResponseHandler

class GitHub_ReponseHandler(HTTP_ResponseHandler):

    '''
    '''
    def __init__(self):
        super().__init__()

    def process(self, response):
        '''
        :param requests.models.Response response: HTTP response object to process
        :returns: The payload of the response, if the handler considers the response successful. Otherwise
                the handler will raise an exception.
        :rtype: dict
        '''
        status                                              = response.status_code
        url                                                 = response.url
        data                                                = response.json()
        match status:
            case 422:
                match data:
                    case {'message': 'Validation Failed',           \
                            'errors': [{                            \
                                    'resource': 'PullRequest',      \
                                    'code': 'custom',               \
                                    'message': msg                  \
                            }],                                                             \
                            'documentation_url': doc_url}:
                        Application.app().log(f"PR ignored: '{msg}'")
                        return None

                    case _:
                            
                        raise ValueError(f"Error status {response.status_code} from HTTP request to '{url}'."
                            + f"\n\nFor the third, this was the HTTP response: \n{data}")  
            case _:         
                return super().process(response)
            