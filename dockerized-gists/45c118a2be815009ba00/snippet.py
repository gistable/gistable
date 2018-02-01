
def test_something(now):
    # now is a mock returned by a custom pytest fixture
    with TimeTravel(now, datetime(2010, 1, 1)):
         do_something_in_the_past()
    do_something_at_the_regular_mocked_time()


class TimeTravel(object):

    def __init__(self, mock, whereto):
        self.mock = mock
        self.whereto = whereto

    def __enter__(self):
        self.old = self.mock.return_value
        self.mock.return_value = self.whereto

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.mock.return_value = self.old

