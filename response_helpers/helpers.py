
import csv
from cStringIO import StringIO

from django.http import HttpResponse

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