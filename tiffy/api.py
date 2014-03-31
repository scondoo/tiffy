import json

from google.appengine.api import urlfetch

from tiffy.exceptions import InvalidArgumentsError, TypeformError


_TYPE_FORM_API_URI = 'https://api.typeform.com/v0/form/{token}?key={api_key}&completed={completed}'


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


class Tiffy(object):
    def __init__(self, api_key):
        if api_key is None:
            raise InvalidArgumentsError(
                'api_key cannot be None'
            )

        self.api_key = api_key

    def _get_typeform_url(self, token, completed=True, since=None, until=None):
        if not isinstance(completed, bool):
            raise InvalidArgumentsError(
                'completed parameter must be a boolean'
            )

        url = _TYPE_FORM_API_URI.format(token=token,
                                        api_key=self.api_key,
                                        completed=str(completed).lower())

        if since is not None:
            url += '&since={}'.format(since)

        if until is not None:
            url += '&until={}'.format(until)

        return url

    def _fire_typeform_urlfetch_call(self, token, deadline, since, until):
        response = TypeformResponse(urlfetch.create_rpc(deadline=deadline), token)
        urlfetch.make_fetch_call(response.rpc, self._get_typeform_url(token, since, until))
        return response

    def get_typeform_multi(self, tokens, deadline=None, completed=True, since=None, until=None):
        if not isinstance(tokens, list):
            tokens = [tokens]

        typeform_responses = []
        for token in tokens:
            typeform_response = self._fire_typeform_urlfetch_call(token, deadline, since, until)
            typeform_responses.append(typeform_response)

        return typeform_responses

    def get_typeform(self, token, deadline=None, completed=True, since=None, until=None):
        return self._fire_typeform_urlfetch_call(token, deadline, since, until)