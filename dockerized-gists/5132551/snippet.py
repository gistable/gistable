# -*- coding: utf-8 -*-
# http://360percents.com/posts/php-random-user-agent-generator/
from datetime import timedelta, date
from random import randint, randrange, choice

PROCESSORS = {
    'linux': ['i686', 'x86_64'],
    'mac': ['Intel', 'PPC', 'U; Intel', 'U; PPC']
}

try:
    import babel
    LANG = [l.replace('_', '-') for l in babel.localedata.list()]
except ImportError:
    LANG = ['en-US', 'en']



def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    from http://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return (start + timedelta(seconds=random_second))


class Browser(object):
    def get_suffix(self):
        return "Mozilla/5.0"

    def get_version(self):
        return ''

    def get_platform(self):
        return ''

    def get_user_agent(self):
        return " ".join([self.get_suffix(), self.get_platform(), self.get_version()])


class Firefox(Browser):
    def get_version(self):
        versions = [
            ['Gecko/', random_date(date(2011, 1, 1), date.today()).strftime('%Y%m%d'),
             ' Firefox/', randint(5, 7), '.0'],
            ['Gecko/', random_date(date(2011, 1, 1), date.today()).strftime('%Y%m%d'),
             ' Firefox/', randint(5, 7), '.0.1'],
            ['Gecko/', random_date(date(2010, 1, 1), date.today()).strftime('%Y%m%d'),
             ' Firefox/3.6.', randint(1, 20)],
            ['Gecko/', random_date(date(2010, 1, 1), date.today()).strftime('%Y%m%d'),
             ' Firefox/3.8'],
        ]
        return ''.join(map(str, choice(versions)))

    def get_platform(self):
        lang = choice(LANG)
        platforms = [
            ['(Windows NT ', randint(5, 6), '.',
             randint(0, 1), '; ', lang, '; rv:1.9.', randint(0, 2), '.20)'],

            ['(X11; Linux ', choice(PROCESSORS['linux']), '; rv:', randint(5, 7), '.0)'],
            ['(Macintosh; ', choice(PROCESSORS['mac']),
             ' Mac OS X 10_', randint(5, 7), '_', randint(0, 9), ' rv:', randint(2, 6), '.0)']
        ]
        return ''.join(map(str, choice(platforms)))


class Chrome(Browser):
    def get_version(self):
        saf_version = "{}{}".format(randint(531, 536), randint(0, 2))
        return "AppleWebKit/{safari_version} (KHTML, like Gecko) Chrome/{}.0.{}.0 Safari/{safari_version}".format(
            randint(13, 17), randint(800, 899), safari_version=saf_version)

    def get_platform(self):
        platforms = [
            '(X11; Linux {})'.format(choice(PROCESSORS['linux'])),
            '(Windows NT {}.{})'.format(randint(5, 6), randint(0, 1)),
            '(Macintosh; U; {} Mac OS X 10_{}_{})'.format(choice(PROCESSORS['mac']), randint(5, 7), randint(0, 9)),
        ]
        return choice(platforms)


class Safari(Browser):
    def get_version(self):
        safari_version = '.'.join(map(str, [randint(531, 535), randint(1, 50), randint(1, 7)]))

        version_range = [randint(4, 5), randint(0, 1)]
        if randint(0, 1) == 0:
            version = "{}.{}".format(*version_range)
        else:
            version = "{}.0.{}".format(*version_range)

        versions = [
            "AppleWebKit/{0} (KHTML, like Gecko) Version/{1} Safari/{0}".format(safari_version, version)
        ]

        return choice(versions)

    def get_platform(self):
        platforms = [
            '(Windows; U; Windows NT {}.{})'.format(randint(5, 6), randint(0, 1)),
            '(Macintosh; U; {} Mac OS X 10_{}_{} rv:{}.0; {})'.format(
                choice(PROCESSORS['mac']), randint(5, 7), randint(0, 9), randint(2, 6), choice(LANG)),
        ]
        return choice(platforms)


class IExplorer(Browser):
    def get_suffix(self):
        return "Mozilla/{}.0".format(randint(4, 5))

    def get_platform(self):
        ie_extra = ['', '; .NET CLR 1.1.' + str(randint(4320, 4325)), '; WOW64']
        platforms = [
            '(compatible; MSIE {}.0; Windows NT {}.{}; Trident/{}.{}{})'.format(randint(5, 9), randint(5, 6),
                                                                              randint(0, 1), randint(3, 5),
                                                                              randint(0, 1), choice(ie_extra))
        ]
        return choice(platforms)


class Opera(Browser):
    def get_suffix(self):
        return "Opera/{}.{}".format(randint(8, 9), randint(10, 99))

    def get_platform(self):
        platforms = [
            '(X11; Linux {proc}; U; {lang})'.format(proc=choice(PROCESSORS['linux']), lang=choice(LANG)),
            '(Windows NT {}.{}; U; {lang})'.format(randint(5, 6), randint(0, 1), lang=choice(LANG))
        ]
        return choice(platforms)

    def get_version(self):
        return "Presto/2.9.{} Version/{}.00".format(randint(160, 190), randint(10, 12))


def get_user_agent():
    return choice(Browser.__subclasses__())().get_user_agent()


if __name__ == '__main__':
    for b in [Firefox, Chrome, Safari, IExplorer, Opera]:
        print b().get_user_agent()

    print get_user_agent()
