def getvideosize(url, verbose=False):
    try:
        if url.startswith('http:') or url.startswith('https:'):
            ffprobe_command = ['ffprobe', '-icy', '0', '-loglevel', 'repeat+warning' if verbose else 'repeat+error', '-print_format', 'json', '-select_streams', 'v', '-show_streams', '-timeout', '60000000', '-user-agent', BILIGRAB_UA, url]
        else:
            ffprobe_command = ['ffprobe', '-loglevel', 'repeat+warning' if verbose else 'repeat+error', '-print_format', 'json', '-select_streams', 'v', '-show_streams', url]
        logcommand(ffprobe_command)
        ffprobe_process = subprocess.Popen(ffprobe_command, stdout=subprocess.PIPE)
        try:
            ffprobe_output = json.loads(ffprobe_process.communicate()[0].decode('utf-8', 'replace'))
        except KeyboardInterrupt:
            logging.warning('Cancelling getting video size, press Ctrl-C again to terminate.')
            ffprobe_process.terminate()
            return 0, 0
        width, height, widthxheight, duration = 0, 0, 0, 0
        for stream in dict.get(ffprobe_output, 'streams') or []:
            if dict.get(stream, 'duration') > duration:
                duration = dict.get(stream, 'duration')
            if dict.get(stream, 'width')*dict.get(stream, 'height') > widthxheight:
                width, height = dict.get(stream, 'width'), dict.get(stream, 'height')
        if duration == 0:
            duration = 1800
        return [[int(width), int(height)], int(float(duration))+1]
    except Exception as e:
        logorraise(e)
        return [[0, 0], 0]