
import csv
from cStringIO import StringIO

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

def render_to_pdf(template_name, context):
    """
    a helper to render an html template to a pdf document.

    USAGE:
    def my_view(request):
        template_name = "myapp/pdf_template.html"
        return render_to_pdf(template_name, {'data': 'some_value'})
    """
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
        writer.writeheader()
        writer.writerows(self.data_iterable)