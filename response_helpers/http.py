
import json

from django import http
from django.core.serializers.json import DjangoJSONEncoder


class JSONResponse(http.HttpResponse):

    def __init__(self, content='', **kwargs):
        kwargs.update(content_type="application/json")
        if not isinstance(content, str):
            content = json.dumps(content, cls=DjangoJSONEncoder)

        super(JSONResponse, self).__init__(content=content, **kwargs)


class CSVResponse(http.StreamingHttpResponse):
    """
    Streams a csv response. Expects streaming content to be a generator.
    """

    def __init__(self, streaming_content='', file_name="csv_download", **kwargs):
        kwargs.update(content_type="text/csv")

        super(CSVResponse, self).__init__(streaming_content=streaming_content, **kwargs)
        self['Content-Disposition'] = "attachment; filename={}.csv;".format(file_name)
