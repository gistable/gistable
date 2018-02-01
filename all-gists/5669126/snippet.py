from indico.util.fossilize import IFossil
from MaKaC.common.Announcement import getAnnoucementMgrInstance 


@HTTPAPIHook.register
class RangeHook(HTTPAPIHook):
    TYPES = ('num', 'char')
    RE = r'(?P<start>[0-9]+|[a-z])-(?P<end>[0-9]+|[a-z])'
    DEFAULT_DETAIL = 'simple'
    MAX_RECORDS = {
        'simple': 10,
        'palindrome': 5
    }

    def _getParams(self):
        super(RangeHook, self)._getParams()
        self._start = self._pathParams['start']
        self._end = self._pathParams['end']

    def export_num(self, aw):
        try:
            start = int(self._start)
            end = int(self._end)
        except ValueError:
            raise HTTPAPIError('Invalid value', 400)
        return RangeFetcher(aw, self).numbers(start, end)

    def export_char(self, aw):
        if len(self._start) != 1 or len(self._end) != 1:
            raise HTTPAPIError('Invalid character', 400)
        return RangeFetcher(aw, self).chars(self._start, self._end)


class DummyObject(object):
    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value


class IDummyFossil(IFossil):
    def getValue(self):
        pass


class IDummyPalindromeFossil(IDummyFossil):
    def getPalindrome(self):
        pass
    getPalindrome.produce = lambda x: x.value + x.value[::-1]


class RangeFetcher(IteratedDataFetcher):
    DETAIL_INTERFACES = {
        'simple': IDummyFossil,
        'palindrome': IDummyPalindromeFossil
    }

    def numbers(self, start, end):
        iterable = xrange(int(start), int(end) + 1)
        iterable = itertools.imap(str, iterable)
        iterable = itertools.imap(DummyObject, iterable)
        return self._process(iterable)

    def chars(self, start, end):
        iterable = xrange(ord(start), ord(end) + 1)
        iterable = itertools.imap(chr, iterable)
        iterable = itertools.imap(str, iterable)
        iterable = itertools.imap(DummyObject, iterable)
        return self._process(iterable)




@HTTPAPIHook.register
class AnnouncementHook(HTTPAPIHook):
    PREFIX = 'api'
    TYPES = ('announcement',)
    RE = r'set'
    GUEST_ALLOWED = False
    VALID_FORMATS = ('json', 'xml')
    COMMIT = True
    HTTP_POST = True

    def _getParams(self):
        super(AnnouncementHook, self)._getParams()
        self._message = get_query_parameter(self._queryParams, ['message'], '')

    def _hasAccess(self, aw):
        return HelperMaKaCInfo.getMaKaCInfoInstance().getAdminList().isAdmin(aw.getUser())

    def api_announcement(self, aw):
        am = getAnnoucementMgrInstance()
        am.setText(self._message)
        return {'message': self._message}