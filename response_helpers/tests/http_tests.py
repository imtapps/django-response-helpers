
import datetime

from django import test
from django.http import StreamingHttpResponse


from response_helpers import http


class JSONResponseTests(test.TestCase):

    def test_uses_json_content_type(self):
        response = http.JSONResponse()
        self.assertEqual("application/json", response['Content-Type'])

    def test_returns_string_of_content_when_given_string(self):
        expected = '{this: "thing"}'
        response = http.JSONResponse(expected)
        self.assertEqual(expected, response.content)

    def test_turns_object_into_json_string_when_given_object_as_content(self):
        expected = {'this': "thing", 'other': 2}
        response = http.JSONResponse(expected)
        self.assertEqual('{"this": "thing", "other": 2}', response.content)

    def test_properly_translates_dates_into_json(self):
        date = datetime.date.today()
        expected = {'this': "thing", 'date': date}
        response = http.JSONResponse(expected)
        self.assertEqual('{"this": "thing", "date": "' + str(date) + '"}', response.content)

    def test_properly_translates_times_into_json(self):
        time = datetime.time()
        expected = {'this': "thing", 'time': time}
        response = http.JSONResponse(expected)
        self.assertEqual('{"this": "thing", "time": "' + str(time) + '"}', response.content)

    def test_properly_translates_datetimes_into_json(self):
        dt = datetime.datetime(year=2011, month=01, day=01, hour=10, minute=10, second=10)
        expected = {'this': "thing", 'datetime': dt}
        response = http.JSONResponse(expected)
        from django import VERSION
        if VERSION[:2] in [(1, 4), (1, 5)]:
            formatted_dt = dt.isoformat()
        else:
            formatted_dt = str(dt)
        self.assertEqual('{"this": "thing", "datetime": "' + formatted_dt + '"}', response.content)


class CSVResponseTests(test.TestCase):

    def setUp(self):
        self.sut = http.CSVResponse

    def test_subclasses_streaming_response(self):
        self.assertTrue(issubclass(self.sut, StreamingHttpResponse))

    def test_uses_csv_content_type(self):
        response = self.sut()
        self.assertEqual("text/csv", response['Content-Type'])

    def test_sets_disposition_to_attachment_with_file_name(self):
        response = self.sut(file_name="myfile")
        self.assertEqual("attachment; filename=myfile.csv;", response['Content-Disposition'])
