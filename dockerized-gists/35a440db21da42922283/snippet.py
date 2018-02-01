class Recorder:
    def __init__(self):
        self.log = logging.getLogger('capturadio.recorder')
        self.start_time = None

    def capture(self, show):
        config = Configuration()

        self.log.info(u'capture "%s" from "%s" for %s seconds to %s' %\
                      (show.name, show.station.name, show.duration, config.destination))

        self.start_time = time.time()
        file_name = u"%s/capturadio_%s.mp3" % (config.tempdir, os.getpid())
        try:
            self._write_stream_to_file(show.get_stream_url(), file_name, show.duration)

            time_string = format_date(config.date_pattern, time.localtime(self.start_time))
            target_file = u"%(station)s/%(show)s/%(show)s_%(time)s.mp3" %\
                   { 'station' : show.station.name,
                     'show': show.name,
                     'time': time_string,
                   }
            target_file = os.path.join(config.destination, slugify(target_file))
            final_file_name = self._copy_file_to_destination(file_name, target_file)
            self._add_metadata(show, final_file_name)
            self.start_time = None
        except Exception as e:
            message = "Could not complete capturing, because an exception occured: %s" % e
            self.log.error(message)
            raise e
        finally:
            if os.path.exists(file_name):
                os.remove(file_name)

    def _write_stream_to_file(self, stream_url, file_name, duration):
        not_ready = True
        self.log.info("write %s to %s" % (stream_url, file_name))
        try:
            file = open(file_name, 'w+b')
            stream = urlopen(stream_url)
            while not_ready:
                file.write(stream.read(10240))
                if time.time() - self.start_time > duration:
                    not_ready = False
            file.close()
        except Exception as e:
            message = "Could not capture show, because an exception occured: %s" % e.message
            self.log.error("_write_stream_to_file: %s" % message)
            os.remove(file_name)
            raise e

    def _copy_file_to_destination(self, file_name, target_file):
        import shutil

        if not os.path.isdir(os.path.dirname(target_file)):
            os.makedirs(os.path.dirname(target_file))
        try:
            shutil.copyfile(file_name, target_file)
            self.log.info(u"file copied from %s to %s" % (file_name, target_file))
            return target_file
        except IOError as e:
            message = "Could not copy tmp file to %s: %s" % (target_file, e.message)
            self.log.error("_copy_file_to_destination: %s" % message)
            os.remove(file_name)
            raise IOError(message, e)

    def _add_metadata(self, show, file_name):
        if file_name is None:
            raise "file_name is not set - you cannot add metadata to None"

        config = Configuration()

        time_string = format_date(config.date_pattern, time.localtime(self.start_time))
        comment = config.comment_pattern % {
            'show': show.name,
            'date': time_string,
            'year': time.strftime('%Y', time.gmtime()),
            'station': show.station.name,
            'link_url': show.get_link_url()
        }

        audio = ID3()
        # See http://www.id3.org/id3v2.3.0 for details about the ID3 tags

        audio.add(TIT2(encoding=2, text=["%s, %s" % (show.name, time_string)]))
        audio.add(TDRC(encoding=2, text=[format_date('%Y-%m-%d %H:%M', self.start_time)]))
        audio.add(TCON(encoding=2, text=[u'Podcast']))
        audio.add(TALB(encoding=2, text=[show.name]))
        audio.add(TLEN(encoding=2, text=[show.duration * 1000]))
        audio.add(TPE1(encoding=2, text=[show.station.name]))
        audio.add(TCOP(encoding=2, text=[show.station.name]))
        audio.add(COMM(encoding=2, lang='eng', desc='desc', text=comment))
        audio.add(TCOM(encoding=2, text=[show.get_link_url()]))
        self._add_logo(show, audio)
        audio.save(file_name)

    def _add_logo(self, show, audio):
        # APIC part taken from http://mamu.backmeister.name/praxis-tipps/pythonmutagen-audiodateien-mit-bildern-versehen/
        url = show.station.logo_url
        if url is not None:
            request = Request(url)
            request.get_method = lambda: 'HEAD'
            try:
                response = urlopen(request)
                logo_type = response.info().gettype()

                if logo_type in ['image/jpeg', 'image/png']:
                    img_data = urlopen(url).read()
                    img = APIC(
                        encoding=3,  # 3 is for utf-8
                        mime=logo_type,
                        type=3,  # 3 is for the cover image
                        desc=u'Station logo',
                        data=img_data
                    )
                    audio.add(img)
            except (HTTPError, URLError) as e:
                message = "Error during capturing %s - %s" % (url, e)
                self.log.error(message)
            except Exception as e:
                raise e