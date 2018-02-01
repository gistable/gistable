class FFMPegRunner(object):
    """
    Usage:

        runner = FFMpegRunner()
        def status_handler(old, new):
            print "From {0} to {1}".format(old, new)

        runner.run('ffmpeg -i ...', status_handler=status_handler)

    """
    re_duration = re.compile('Duration: (\d{2}):(\d{2}):(\d{2}).(\d{2})[^\d]*', re.U)
    re_position = re.compile('time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})\d*', re.U | re.I)

    def run_session(self, command, status_handler=None):
        pipe = subprocess.Popen(command, shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines = True)

        duration = None
        position = None
        percents = 0

        while True:
            line = pipe.stdout.readline().strip()

            if line == '' and pipe.poll() is not None:
                break

            if duration is None:
                duration_match = self.re_duration.match(line)
                if duration_match:
                    duration = self.time2sec(duration_match)

            if duration:
                position_match = self.re_position.search(line)
                if position_match:
                    position = self.time2sec(position_match)

            new_percents = self.get_percent(position, duration)

            if new_percents != percents:
                if callable(status_handler):
                    status_handler(percents, new_percents)
                percents = new_percents

    def get_percent(self, position, duration):
        if not position or not duration:
            return 0
        percent = int(math.floor(100 * position / duration))
        return 100 if percent > 100 else percent

    def time2sec(self, search):
        return sum([i**(2-i) * int(search.group(i+1)) for i in xrange(3)])
