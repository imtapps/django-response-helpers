"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import mock
from django.test import TestCase

from response_helpers import helpers

class CSVResponseTests(TestCase):

    def setUp(self):
        self.field_names = ["field1", "field2"]

    def test_get_file_name_returns_file_name_property(self):
        csv_response = helpers.CSVResponse([])
        file_name = "A File Name"
        csv_response.file_name = file_name
        self.assertEqual(file_name, csv_response.get_file_name())

    def test_get_fields_returns_fields_property_when_exists(self):
        csv_response = helpers.CSVResponse([])
        fields = ["field1", "field2"]
        csv_response.field_names = fields
        self.assertEqual(fields, csv_response.get_field_names())

    def test_turns_data_iterable_into_csv_in_create_csv(self):
        """
        Tests that we're writing out the header row and also all
        the items in our data iterable we sent in.
        """
        field_names = ['field1', 'field2']
        data_iterable = [
            {'field1': 'test1.1', 'field2': 'test1.2'},
            {'field1': 'test2.1', 'field2': 'test2.2'},
        ]
        csv_response = helpers.CSVResponse(data_iterable)
        csv_response.field_names = field_names
        result = csv_response._create_csv()
        self.assertEqual(
            "field1,field2\r\n"
            "test1.1,test1.2\r\n"
            "test2.1,test2.2\r\n"
        , result)

    @mock.patch('response_helpers.helpers.CSVResponse._write_csv_contents', mock.Mock())
    @mock.patch('response_helpers.helpers.StringIO', spec='cStringIO.StringIO')
    def test_closes_string_io_object_in_create_csv(self, string_io):
        io_object = string_io.return_value
        csv_response = helpers.CSVResponse([])
        csv_response._create_csv()
        io_object.close.assert_called_once_with()


    def test_sets_response_content_to_csv_data(self):
        with mock.patch('response_helpers.helpers.CSVResponse._create_csv') as create_csv:
            csv_data = "some,csv\r\ndata,here\r\n"
            create_csv.return_value = csv_data
            csv_response = helpers.CSVResponse([])

            response = csv_response.response
            self.assertEqual(csv_data, response.content)

    def test_sets_response_mime_type_to_text_csv(self):
        with mock.patch('response_helpers.helpers.CSVResponse._create_csv') as create_csv:
            create_csv.return_value = ""
            csv_response = helpers.CSVResponse([])

            response = csv_response.response
            self.assertEqual("text/csv", response['Content-Type'])

    def test_sets_response_content_disposition_to_attachment_and_filename(self):
        with mock.patch('response_helpers.helpers.CSVResponse._create_csv') as create_csv:
            create_csv.return_value = ""
            csv_response = helpers.CSVResponse([])
            csv_response.file_name = "csv_file"

            response = csv_response.response
            expected_disposition = "attachment; filename=csv_file.csv;"
            self.assertEqual(expected_disposition, response['Content-Disposition'])

    def test_sets_response_content_length_to_csv_data_length(self):
        with mock.patch('response_helpers.helpers.CSVResponse._create_csv') as create_csv:
            csv_data = "some,csv\r\ndata,here\r\n"
            create_csv.return_value = csv_data
            csv_response = helpers.CSVResponse([])

            response = csv_response.response
            self.assertEqual(str(len(csv_data)), response['Content-Length'])
