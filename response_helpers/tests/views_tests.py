
from django import test
from django.views.generic import View

from response_helpers import views


class SampleCSVResponse(views.CSVResponseView):
    field_names = ("first_field", "second_field")

    def get_data(self):
        return [{
            "first_field": "one",
            "second_field": "two",
        }, {
            "first_field": "second_one",
            "second_field": "second_two",
        }]


class CSVResponseViewTests(test.TestCase):

    def setUp(self):
        self.sut = views.CSVResponseView

    def test_subclasses_generic_view(self):
        self.assertTrue(issubclass(self.sut, View))

    def test_get_filename_uses_filename_from_class_when_present(self):
        file_name = "MyFile"
        self.sut.file_name = file_name
        self.assertEqual(file_name, self.sut().get_file_name())

    def test_get_filename_uses_default_filename_when_not_explicitly_set(self):
        self.assertEqual("csv_download", self.sut().get_file_name())

    def test_get_field_names_returns_field_names_when_defined(self):
        field_names = ["one", "two"]
        self.sut.field_names = field_names
        self.assertEqual(field_names, self.sut().get_field_names())

    def test_get_header_row_returns_dict_of_field_names(self):
        field_names = ["one", "two"]
        self.sut.field_names = field_names
        header_row = self.sut().get_header_row()
        self.assertEqual({
            "one": "one",
            "two": "two",
        }, header_row)

    def test_get_method_returns_csv_of_data_as_content(self):
        from cStringIO import StringIO

        request = test.RequestFactory().get("/")
        sut = SampleCSVResponse()
        sut.field_names = ["first_field", "second_field"]
        response = sut.get(request)

        s = StringIO()
        for i in response.streaming_content:
            s.write(i)

        self.assertEqual(
            "first_field,second_field\r\n"
            "one,two\r\n"
            "second_one,second_two\r\n", s.getvalue())
