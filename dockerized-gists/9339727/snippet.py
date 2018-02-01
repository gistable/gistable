from mock import patch

@patch('path.to.module.S3Library')
def test_stores_data_in_s3(S3Library):
    my_method(data)
    assert S3Library.upload_file.called_once_with(data)

@patch('path.to.module.S3Library')
def test_data_contains_some_value(S3Library):
    S3Library.get_file.return_value = _stub_data()
    xml_file = S3Library.get_file('filename')
    data = XMLParser.parse(xml_file)
    assert data.value == 'something'

def _stub_data():
    return FakeXMLObject()