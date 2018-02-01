@pytest.fixture
def stream():
    return mock.Mock(spec=Stream)

@pytest.fixture
def output():
    return open('test.txt', 'w')

@pytest.fixture
def tailer(self, stream, output):
    with mock.patch('logging.getLogger', autospec=True):
        yield Tailer(stream, output, mock.sentinel.lines)

@mock.patch('consumer.read_lines', autospec=True)
def test_tailer(mock_read, tailer, stream):
    stream.fetch.return_value = "test\n"
    tailer.run()
    mock_read.assert_called_once_with(stream, mock.sentinel.lines)
    with open('test.txt', 'r') as f:
        assert f.read() == "test"