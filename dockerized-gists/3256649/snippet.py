#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request, jsonify
import urllib2
from BeautifulSoup import BeautifulSoup 


app = Flask(__name__)


messages_metro = {
    "en": "Next metro on %s at %s to %s in %s",
    "fr": u"Prochain metro sur %s à %s vers %s dans %s"}

messages_tram = {
    "en": "Next tram on %s at %s to %s in %s",
    "fr": u"Prochain tram sur %s à %s vers %s dans %s"}

messages_bus = {
    "en": "Next bus on %s at %s to %s in %s",
    "fr": u"Prochain bus sur %s à %s vers %s dans %s"}

messages_rer = {
    "en": "'Next train on %s at %s to %s at %s",
    "fr": u"Prochain train sur %s à %s vers %s à %s"}


def fetch_ratp_schedule(url, schedule_parser=None, text=False):
    app.logger.debug('Fetching %s' % url)
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)

    div = soup.find('div', id='prochains_passages')
    line_details = div.find('div', {"class": 'line_details'})

    response = {
        "type": line_details.findAll('img')[0]['alt'],
        "line": line_details.findAll('img')[1]['alt'],
        "station": line_details.span.string,
        "direction": div.find('span', {"class": 'direction'}).string[12:], 
        "schedule": []}

    if schedule_parser is None:
        for tr in div.find('tbody').findAll('tr'):
            response['schedule'].append(tr.findAll('td')[1].string)
    else:
        for s in schedule_parser(div):
            response['schedule'].append(s)

    if text:
        return text % (response['line'], response['station'], 
            response['direction'], ', '.join(response['schedule']))

    return response


def fetch_metro_schedule(line, station, direction, text=False, lang='en'):
    url = "http://www.ratp.fr/horaires/fr/ratp/metro/prochains_passages/PP/%s/%s/%s" % (station, line, direction.upper())
    message = messages_metro.get(lang, 'en') if text else False
    return fetch_ratp_schedule(url, text=message)


def fetch_tram_schedule(line, station, direction, text=False, lang='en'):
    url = "http://www.ratp.fr/horaires/fr/ratp/tramway/prochains_passages/PP/T%s/%s/%s" % (line, station, direction.upper())
    message = messages_tram.get(lang, 'en') if text else False
    return fetch_ratp_schedule(url, text=message)


def fetch_bus_schedule(line, station, direction, text=False, lang='en'):
    url = "http://www.ratp.fr/horaires/fr/ratp/bus/prochains_passages/PP/B%s/%s/%s" % (line, station, direction.upper())

    def parse_schedule(div):
        for tr in div.find('tbody').findAll('tr'):
            yield {"terminus": tr.findAll('td')[0].string, "time": tr.findAll('td')[1].string}

    r = fetch_ratp_schedule(url, parse_schedule)

    if text:
        return messages_bus.get(lang, 'en') % (r['line'], r['station'], 
            r['schedule'][0]['terminus'], r['schedule'][0]['time'])
    return r


def fetch_rer_schedule(line, station, direction, text=False, lang='en'):
    url = "http://www.ratp.fr/horaires/fr/ratp/rer/prochains_passages/R%s/%s/%s" % (line.upper(), station, direction.upper())

    def parse_schedule(div):
        for tr in div.find('tbody').findAll('tr'):
            yield {"name": tr.findAll('td')[0].a.string, "time": tr.findAll('td')[2].string}

    r = fetch_ratp_schedule(url, parse_schedule)

    if text:
        return messages_rer.get(lang, 'en') % (r['line'], r['station'], r['direction'], 
            ', '.join(map(lambda i: "%s (%s)" % (i['time'], i['name']), r['schedule'])))
    return r


@app.route('/')
def index():
    return jsonify(message="RATP Schedule")


@app.route('/metro/<line>/<station>/<direction>')
def get_metro_schedule(line, station, direction):
    try:
        text = request.args.get('text') == '1'
        response = fetch_metro_schedule(line, station, direction, text, request.args.get('lang', 'en'))
        return response if text else jsonify(**response)
    except Exception as e:
        app.logger.debug(e)
        return '', 500


@app.route('/tram/<line>/<station>/<direction>')
def get_tram_schedule(line, station, direction):
    try:
        text = request.args.get('text') == '1'
        response = fetch_tram_schedule(line, station, direction, text, request.args.get('lang', 'en'))
        return response if text else jsonify(**response)
    except Exception as e:
        app.logger.debug(e)
        return '', 500


@app.route('/bus/<line>/<station>/<direction>')
def get_bus_schedule(line, station, direction):
    try:
        text = request.args.get('text') == '1'
        response = fetch_bus_schedule(line, station, direction, text, request.args.get('lang', 'en'))
        return response if text else jsonify(**response)
    except Exception as e:
        app.logger.debug(e)
        return '', 500


@app.route('/rer/<line>/<station>/<direction>')
def get_rer_schedule(line, station, direction):
    try:
        text = request.args.get('text') == '1'
        response = fetch_rer_schedule(line, station, direction, text, request.args.get('lang', 'en'))
        return response if text else jsonify(**response)
    except Exception as e:
        app.logger.debug(e)
        return '', 500


@app.route('/geckoboard')
def geckoboard():
    lang = request.args.get('lang', 'en')
    items = []
    for l in request.args.getlist('line'):
        try:
            mode, line, station, direction = l.split(',')
            if mode.lower() == 'rer':
                t = fetch_rer_schedule(line, station, direction, True, lang)
            else:
                t = fetch_metro_schedule(line, station, direction, True, lang)
            items.append({"text": t, "type": 0})
        except:
            pass
    return jsonify(item=items)


if __name__ == '__main__':
    app.run(port=8080)
