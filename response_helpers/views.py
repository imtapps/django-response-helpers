
import csv

from django.utils.six import StringIO
from django.views.generic import View

from response_helpers.http import CSVResponse


class CSVResponseView(View):
    """
    Returns a
    """
    file_name = '' # don't add .csv  that will be appended automatically.
    field_names = []

    def get_file_name(self):
        return self.file_name or "csv_download"

    def get_field_names(self):
        return self.field_names

    def get(self, request, *args, **kwargs):
        csvfile = StringIO()
        csvwriter = csv.DictWriter(csvfile, self.get_field_names(), extrasaction="ignore")

        csvwriter.writerow(self.get_header_row())
        data_generator = self.write_csv_data(csvwriter, csvfile, self.get_data())
        return CSVResponse(streaming_content=data_generator)

    def get_data(self):
        """
        Should return an iterable that
        """
        raise NotImplementedError

    def get_header_row(self):
        field_names = self.get_field_names()
        return dict(zip(field_names, field_names))

    def write_csv_data(self, csvwriter, csvfile, data_iterator):
        for row in data_iterator:
            csvwriter.writerow(row)
        data = self._read_and_flush(csvfile)
        yield data

    def _read_and_flush(self, csvfile):
        csvfile.seek(0)
        data = csvfile.read()
        csvfile.seek(0)
        csvfile.truncate()
        return data
