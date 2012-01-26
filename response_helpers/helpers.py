
import csv
from cStringIO import StringIO

from django.http import HttpResponse, HttpRequest
from django.template.loader import render_to_string
from django.template.context import RequestContext
from functools import wraps


def render(template_name, request, context_data=None, response_type=HttpResponse, **kwargs):
    """
    renders template to an HttpResponse always giving RequestContext
    """
    content = render_to_string(template_name, context_data, context_instance=RequestContext(request))
    return response_type(content, **kwargs)

def render_to(template_name, response=HttpResponse):
    """
    decorator to allow a view to return a dictionary and render
    the contents to a template as an HttpResponse with RequestContext.

    USAGE:
    @render_to('myapp/my_template_name.html')
    def sample_view(response, *args, **kwargs):
        return {'some': 'data'}

    """
    def renderer(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            """
            if the view returns something other than a context_data
            dictionary, maybe the user is returning a redirect or some
            other response, so we won't try to render to the template.
            """
            if not isinstance(request, HttpRequest):
                raise AssertionError("request is " + request.__class__.__name__ + ". Must be HttpRequest...")

            context_data = func(request, *args, **kwargs)
            if not isinstance(context_data, dict):
                return context_data
            return render(template_name, request, context_data, response)
        return wrapper
    return renderer

def render_to_pdf(template_name, context):
    """
    a helper to render an html template to a pdf document.

    USAGE:
    def my_view(request):
        template_name = "myapp/pdf_template.html"
        return render_to_pdf(template_name, {'data': 'some_value'})
    """
    # don't import until you really have to so people using this don't need
    # to install xhtml2pdf and all its dependencies if they don't use it.
    from xhtml2pdf import pisa


    pdf_stream = StringIO()
    rendered_template = StringIO(render_to_string(template_name, context).encode("ISO-8859-1"))

    pisa_document = pisa.pisaDocument(rendered_template, pdf_stream)
    if pisa_document.err:
        exception_message = "Error creating pdf from html. \r\n"
        exception_message += "\r\n".join([str(msg) for msg in pisa_document.log])
        raise Exception(exception_message)

    return HttpResponse(pdf_stream.getvalue(), mimetype='application/pdf')

class CSVResponse(object):
    """
    Takes an iterable of dictionaries, converts their values to
    a csv format and delivers back an HttpResponse that will download
    the file for the user.

    ATTRIBUTES:
    file_name: what the file will be named when delivered (don't add .csv)
    field_names: a list of headers for the csv file in the order desired

    USAGE:
    def example_view(request):
        list_of_dictionaries = get_list_of_dictionaries() # i.e. do your query
        csv_response = CSVResponse(list_of_dictionaries)
        return csv_response.response

    """
    file_name = ''
    field_names = None

    def __init__(self, data_iterable):
        self.data_iterable = data_iterable

    @property
    def response(self):
        csv_data = self._create_csv()

        response = HttpResponse(csv_data)
        response['Content-Type'] = "text/csv"
        response['Content-Disposition'] = "attachment; filename=%s;" % (self.get_file_name() + ".csv")
        response['Content-Length'] = len(csv_data)
        return response

    def get_file_name(self):
        return self.file_name or 'download'

    def get_field_names(self):
        return self.field_names or []

    def _create_csv(self):
        """
        StringIO holds the csv data in a memory buffer that acts
        like a regular file. Python's csv library does all the
        heaving lifting and worrying about creating the csv properly.
        """
        f = StringIO()
        try:
            self._write_csv_contents(f)
            return f.getvalue()
        finally:
            f.close()

    def _write_csv_contents(self, f):
        """
        f should be a file like object DictWriter can write to.
        """
        writer = csv.DictWriter(f, fieldnames=self.get_field_names(), extrasaction="ignore")
        # writeheader wasn't added till python 2.7... fall back to
        # manually write the header if necessary
        if hasattr(writer, 'writeheader'):
            writer.writeheader()
        else:
            header = dict(zip(writer.fieldnames, writer.fieldnames))
            writer.writerow(header)
        writer.writerows(self.data_iterable)
