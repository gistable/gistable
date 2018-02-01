import os
import time
import datetime
import pickle
import webbrowser
import codecs
import subprocess
import sys

# Quick little function that opens the default web browser and displays the HTML of your choice
def preview_html(html, filename=None):
    if filename:
        with open(filename, "w", "utf-8") as f:
            f.write(html)
        if sys.platform == 'darwin':    # in case of OS X
            subprocess.Popen(['open', filename])
        else:
            webbrowser.open_new_tab(filename)
    else:
        # If no filename is given, use test.debug.html
        with codecs.open("test.debug.html", "w", "utf-8") as f:
            f.write(html)
        if sys.platform == 'darwin':    # in case of OS X
            subprocess.Popen(['open', "test.debug.html"])
        else:
            webbrowser.open_new_tab("test.debug.html")


# For use with EditThisCookie Chrome extension, converts into a dict for use in Requests
def cookies_from_file(path):
    cookies = {}
    with open(path) as f:
        for c in json.loads(f.read()):
            cookies[c['name']] = c['value']
    return cookies


# Convert a dict of integers, floats, and strings into a CSV with the keys as the headers
def dictcsv(data):
    headers = []
    for d in data:
        for col in d:
            if col not in headers:
                headers.append(col)
    header_string = ''
    for h in headers:
        header_string += h + ','
    header_string = header_string[:-1]
    data_string = ''
    for d in data:
        line = ''
        for h in headers:
            if h in d:
                line += str(d[h]) + ','
        line = line[:-1]
        data_string += line + '\n'
    return header_string + '\n' + data_string[:-1]


# Grab the first YouTube URL it can find, if any
def extract_youtube_info(text):
    t = None
    if 'youtube.com/watch?v=' in text:
        t = text.split('youtube.com/watch?v=')[1]
    elif 'youtu.be/' in text:
        t = text.split('youtu.be/')[1]
    if t:
        return t.split('&')[0].split(' ')[0]
    else:
        return None


def cacheable(cachetime, method, *method_params, **method_kword):
    # Raise exception if cache time is less than 1 second
    if cachetime < 1:
        raise ValueError('Cache time must be at least 1 second')

    # Create the cachable directory if it doesn't exist
    if not os.path.exists('.cachable'):
        os.makedirs('.cachable')

    # If the cache timestamp exists
    if os.path.isfile(os.path.join('.cachable', __name__ + '-' + method.__name__)):
        with open(os.path.join('.cachable', __name__ + '-' + method.__name__)) as f:
            s = pickle.load(f)
            time_left = (datetime.datetime.fromtimestamp(float(s[0])) - datetime.datetime.now()).total_seconds()

            # Return the cached data if it isn't expired
            if (time_left > 0):
                print 'cached'
                return s[1]
            # Or re-run the method and return that
            else:
                print 'expired'

    # If it doesn't run the method and cache it
    run_method = method(*method_params, **method_kword)

    with open(os.path.join('.cachable', __name__ + '-' + method.__name__), 'w') as f:
        future_time = time.mktime((datetime.datetime.now() + datetime.timedelta(seconds=cachetime)).timetuple())
        pickle.dump((future_time, run_method), f)
        #f.write(str(future_time) + '\n' + run_method)

    return run_method