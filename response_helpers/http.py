
import json

from django import http

class JSONResponse(http.HttpResponse):

    def __init__(self, content='', **kwargs):
        kwargs.update(content_type="application/json")
        if not isinstance(content, basestring):
            content = json.dumps(content)

        super(JSONResponse, self).__init__(content=content, **kwargs)
