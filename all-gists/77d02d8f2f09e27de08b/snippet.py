import sys
import argparse
import logging
import os
import getpass
import pprint
import subprocess

import ftrack


class DJVViewer(ftrack.Action):
    '''Custom action.'''

    #: Action identifier.
    identifier = 'djvviewer'

    #: Action label.
    label = 'DJV Viewer'


    def __init__(self):
        '''Initialise action handler.'''
        self.log = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

    def register(self):
        '''Register action.'''
        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.action.discover and source.user.username={0}'.format(
                getpass.getuser()
            ),
            self.discover
        )

        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.action.launch and source.user.username={0} '
            'and data.actionIdentifier={1}'.format(
                getpass.getuser(), self.identifier
            ),
            self.launch
        )


    def discover(self, event):

        return {
            'items': [{
                'label': self.label,
                'actionIdentifier': self.identifier,
            }]
        }


    def launch(self, event):
        data = event['data']
        selection = data.get('selection', [])

        if 'values' in event['data']:
            # Do something with the values or return a new form.
            values = event['data']['values']

            for item in selection:
                version = None

                try:
                    task = ftrack.Task(item['entityId'])
                    asset = task.getAssets(assetTypes=['img'])[0]
                    version = asset.getVersions()[-1]
                except:
                    version = ftrack.AssetVersion(item['entityId'])

                if version.getAsset().getType().getShort() == 'img':

                    component = None
                    try:
                        component = version.getComponent(values['component'])
                    except:
                        pass

                    if component:
                        path = component.getFilesystemPath()
                        extension = os.path.splitext(path)

                        random_file = None
                        for f in os.listdir(os.path.dirname(path)):
                            if f.endswith(extension):
                                dir_path = os.path.dirname(path)
                                random_file = os.path.join(dir_path, f)
                        
                        djv_path = r'INTALL PATH\bin\djv_view.exe'
                        args = [djv_path, random_file]
                        subprocess.Popen(args)

            return {
                'success': True,
                'message': 'DJV Viewer launched.'
            }

        # finding components on version
        components = []
        for item in selection:
            version = None

            try:
                task = ftrack.Task(item['entityId'])
                asset = task.getAssets(assetTypes=['img'])[0]
                version = asset.getVersions()[-1]
            except:
                version = ftrack.AssetVersion(item['entityId'])

            if not version.get('ispublished'):
                version.publish()

            if version.getAsset().getType().getShort() == 'img':
                for c in version.getComponents():
                    components.append(c.getName())

        data = []
        for c in set(components):
            data.append({'label': c, 'value': c})

        return {
            'items': [
                {
                    'label': 'Component to view',
                    'type': 'enumerator',
                    'name': 'component',
                    'data': data
                }
            ]
        }


def register(registry, **kw):
    '''Register action. Called when used as an event plugin.'''
    logging.basicConfig(level=logging.INFO)
    action = DJVViewer()
    action.register()


def main(arguments=None):
    '''Set up logging and register action.'''
    if arguments is None:
        arguments = []

    parser = argparse.ArgumentParser()
    # Allow setting of logging level from arguments.
    loggingLevels = {}
    for level in (
        logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING,
        logging.ERROR, logging.CRITICAL
    ):
        loggingLevels[logging.getLevelName(level).lower()] = level

    parser.add_argument(
        '-v', '--verbosity',
        help='Set the logging output verbosity.',
        choices=loggingLevels.keys(),
        default='info'
    )
    namespace = parser.parse_args(arguments)

    '''Register action and listen for events.'''
    logging.basicConfig(level=loggingLevels[namespace.verbosity])

    ftrack.setup()
    action = DJVViewer()
    action.register()

    ftrack.EVENT_HUB.wait()


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
