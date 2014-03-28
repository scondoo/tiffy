import json

from google.appengine.api import urlfetch

from tiffy.exceptions import InvalidArgumentsError, TypeformError


_TYPEFORM_API_KEY = 'API KEY HERE'
_TYPE_FORM_API_URI = 'https://api.typeform.com/v0/form/{}?key=' + _TYPEFORM_API_KEY + '&completed={}'


class TypeformResponse(object):
    def __init__(self, url_rpc, token):
        if url_rpc is None:
            raise InvalidArgumentsError(
                'URL RPC cannot be None'
            )

        if token is None:
            raise InvalidArgumentsError(
                'Token cannot be None'
            )

        self.rpc = url_rpc
        self.token = token
        self.json = None

    def raise_if_error(self, response):
        status_code = response.status_code
        if status_code != 200:
            message = response.content
            raise TypeformError(self.token, message, response.status_code)

    def get_json(self):
        if self.json is not None:
            return self.json

        response = self.rpc.get_result()
        self.raise_if_error(response)

        self.json = json.loads(response.content)
        return self.json

    def get_responses(self):
        return self.get_json().get('responses', [])


def _get_typeform_url(token, completed=True, since=None, until=None):
    url = _TYPE_FORM_API_URI.format(token, str(completed).lower())
    if since is not None:
        url += '&since={}'.format(since)

    if until is not None:
        url += '&until={}'.format(until)

    return url


def _fire_typeform_urlfetch_call(token, deadline, since, until):
    response = TypeformResponse(urlfetch.create_rpc(deadline=deadline), token)
    urlfetch.make_fetch_call(response.rpc, _get_typeform_url(token, since, until))
    return response


def get_typeform_multi(tokens, deadline=None, completed=True, since=None, until=None):
    if not isinstance(tokens, list):
        tokens = [tokens]

    typeform_responses = []
    for token in tokens:
        typeform_response = _fire_typeform_urlfetch_call(token, deadline, since, until)
        typeform_responses.append(typeform_response)

    return typeform_responses


def get_typeform(token, deadline=None, completed=True, since=None, until=None):
    return _fire_typeform_urlfetch_call(token, deadline, since, until)