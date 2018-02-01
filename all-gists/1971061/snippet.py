import putio
import logging
from flexget import validator
from flexget.plugin import register_plugin

log = logging.getLogger('putio')

class PutIOPlugin(object):
    """
    Plugin to add and fetch your torrents on put.io
    Place this file and the putio.py file from https://put.io/service/api
    in your flexget plugins folder (usually $HOME/.flexget/plugins/)
    Sample config usage (in $HOME/.flexget/config.yml)

        presets:
          tv: 
            putio:
              key: <API_KEY>
              secret: <API_SECRET>
    """

    def validator(self):
        root = validator.factory('root')
        root.accept('boolean')
        config = root.accept('dict')
        config.accept('text', key='key')
        config.accept('text', key='secret')
        return root

    def on_feed_output(self, feed, config):
        if config is True:
            config = {}
        elif config is False:
            return

        api = putio.Api(config.get('key'), config.get('secret'))
        bucket = api.create_bucket()

        urls = [ entry['url'] for entry in feed.accepted ]
        if urls:
            log.info('Put.io: analyzing accepted urls')
            bucket.analyze(urls)
            log.info('Put.io: fetching accepted urls')
            bucket.fetch()

register_plugin(PutIOPlugin, 'putio', api_ver=2)
