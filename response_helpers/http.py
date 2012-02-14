
import json

from django import http
from django.core.serializers.json import DjangoJSONEncoder

class JSONResponse(http.HttpResponse):

    def __init__(self, content='', **kwargs):
        kwargs.update(content_type="application/json")
        if not isinstance(content, basestring):
            content = json.dumps(content, cls=DjangoJSONEncoder)

        super(JSONResponse, self).__init__(content=content, **kwargs)
