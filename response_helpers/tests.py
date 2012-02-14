
import mock
import datetime

from django.test import TestCase

from response_helpers import helpers, http

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

    def test_sets_response_content_to_csv_data(self):
        with mock.patch('response_helpers.helpers.CSVResponse._create_csv') as create_csv:
            csv_data = "some,csv\r\ndata,here\r\n"
            create_csv.return_value = csv_data
            csv_response = helpers.CSVResponse([])

            response = csv_response.response
            self.assertEqual(csv_data, response.content)

    @mock.patch('response_helpers.helpers.CSVResponse._write_csv_contents', mock.Mock())
    @mock.patch('response_helpers.helpers.StringIO', autospec=True)
    def test_closes_string_io_object_in_create_csv(self, string_io):
        io_object = string_io.return_value
        csv_response = helpers.CSVResponse([])
        csv_response._create_csv()
        io_object.close.assert_called_once_with()

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


try:
    import xhtml2pdf
    has_xhtml2pdf = True
except ImportError:
    has_xhtml2pdf = False

if has_xhtml2pdf:

    class RenderToPdfTests(TestCase):

        @mock.patch('response_helpers.helpers.render_to_string')
        def test_renders_given_template_and_context_to_string(self, render_to_string):
            render_to_string.return_value = ""
            template = mock.Mock()
            context = mock.Mock()
            helpers.render_to_pdf(template, context)
            render_to_string.assert_called_once_with(template, context)

        @mock.patch('response_helpers.helpers.StringIO', mock.Mock(spec='cStringIO.StringIO'))
        @mock.patch('xhtml2pdf.pisa.pisaDocument', spec="xhtml2pdf.pisa.pisaDocument")
        @mock.patch('response_helpers.helpers.render_to_string')
        def test_encodes_rendered_template_with_iso_encoding(self, render_to_string, pisa_document):
            pisa_document.return_value.err = None
            rendered_template = render_to_string.return_value = mock.MagicMock()
            helpers.render_to_pdf(mock.Mock(), mock.Mock())
            rendered_template.encode.assert_called_once_with("ISO-8859-1")

        @mock.patch('xhtml2pdf.pisa.pisaDocument', spec="xhtml2pdf.pisa.pisaDocument")
        @mock.patch('response_helpers.helpers.StringIO', spec='cStringIO.StringIO')
        @mock.patch('response_helpers.helpers.render_to_string')
        def test_creates_stringio_with_encoded_rendered_template(self, render_to_string, string_io, pisa_document):
            pisa_document.return_value.err = None
            helpers.render_to_pdf(mock.Mock(), mock.Mock())
            string_io.assert_called_with(render_to_string.return_value.encode.return_value)

        @mock.patch('response_helpers.helpers.render_to_string', mock.Mock())
        @mock.patch('xhtml2pdf.pisa.pisaDocument', spec="xhtml2pdf.pisa.pisaDocument")
        @mock.patch('response_helpers.helpers.StringIO', spec='cStringIO.StringIO')
        def test_creates_pisa_document_from_stringio(self, string_io, pisa_document):
            pdf_stream = mock.Mock()
            rendered_template = mock.Mock()

            io_streams = [pdf_stream, rendered_template]
            def side_effect(*args):
                return io_streams.pop(0) if io_streams else mock.Mock()
            string_io.side_effect = side_effect

            pisa_document.return_value.err = None
            helpers.render_to_pdf(mock.Mock(), mock.Mock())
            pisa_document.assert_called_once_with(rendered_template, pdf_stream)

        @mock.patch('response_helpers.helpers.render_to_string', mock.Mock())
        @mock.patch('response_helpers.helpers.StringIO', mock.Mock(spec='cStringIO.StringIO'))
        @mock.patch('xhtml2pdf.pisa.pisaDocument', spec="xhtml2pdf.pisa.pisaDocument")
        def test_raises_exception_when_pdf_error_occurs(self, pisa_document):
            pisa_document.return_value.err = 1
            pisa_document.return_value.log = [('This is an error', 'some_value')]
            self.assertRaises(Exception, helpers.render_to_pdf, mock.Mock(), mock.Mock())

        @mock.patch('response_helpers.helpers.render_to_string', mock.Mock())
        @mock.patch('response_helpers.helpers.HttpResponse', spec='django.http.HttpResponse')
        @mock.patch('response_helpers.helpers.StringIO', spec='cStringIO.StringIO')
        @mock.patch('xhtml2pdf.pisa.pisaDocument', spec="xhtml2pdf.pisa.pisaDocument")
        def test_returns_http_response_with_pdf_and_mimetype(self, pisa_document, string_io, http_response):
            pisa_document.return_value.err = None
            response = helpers.render_to_pdf(mock.Mock(), mock.Mock())
            http_response.assert_called_once_with(string_io.return_value.getvalue.return_value, mimetype='application/pdf')
            self.assertEqual(http_response.return_value, response)


class RenderTests(TestCase):

    def test_renders_an_http_response_by_default(self):
        with mock.patch('response_helpers.helpers.render_to_string'):
            response = helpers.render(None, mock.Mock())
            self.assertTrue(isinstance(response, helpers.HttpResponse))

    def test_renders_response_type_with_content_and_kwargs(self):
        with mock.patch('response_helpers.helpers.render_to_string') as render_to_string:
            kwargs = {'some': 'kwargs'}
            response_type = mock.Mock()
            response = helpers.render(None, mock.Mock(), response_type=response_type, **kwargs)
            self.assertEqual(response_type.return_value, response)
            response_type.assert_called_once_with(render_to_string.return_value, **kwargs)

    @mock.patch('response_helpers.helpers.RequestContext')
    def test_gives_template_name_context_and_request_context_to_render_to_string(self, request_context):
        with mock.patch('response_helpers.helpers.render_to_string') as render_to_string:
            template_name = "my_template"
            context_data = mock.sentinel.context
            request = mock.Mock()

            helpers.render(template_name, request, context_data)
            render_to_string.assert_called_once_with(template_name, context_data, context_instance=request_context.return_value)
            request_context.assert_called_once_with(request)


class RenderToTests(TestCase):

    def test_render_to_wraps_function(self):

        @helpers.render_to("")
        def some_func():
            pass

        self.assertEqual('some_func', some_func.__name__)

class JSONResponseTests(TestCase):

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

    def test_property_translates_dates_into_json(self):
        date = datetime.date.today()
        expected = {'this': "thing", 'date': date}
        response = http.JSONResponse(expected)
        self.assertEqual('{"this": "thing", "date": "' + str(date) + '"}', response.content)

    def test_property_translates_times_into_json(self):
        time = datetime.time()
        expected = {'this': "thing", 'time': time}
        response = http.JSONResponse(expected)
        self.assertEqual('{"this": "thing", "time": "' + str(time) + '"}', response.content)

    def test_property_translates_datetimes_into_json(self):
        dt = datetime.datetime(year=2011, month=01, day=01, hour=10, minute=10, second=10)
        expected = {'this': "thing", 'datetime': dt}
        response = http.JSONResponse(expected)
        self.assertEqual('{"this": "thing", "datetime": "' + str(dt) + '"}', response.content)

