import logging

from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials


class CloudLoggingHandler(logging.Handler):
    def __init__(self, project_id):
        logging.Handler.__init__(self)
        self.project_id = project_id
        credentials = GoogleCredentials.get_application_default()
        self.logging_api = build('logging', 'v2beta1', credentials=credentials)

    def emit(self, record):
        print(str(record))
        self.logging_api.entries().write(
                body={
                    "entries": [
                        {
                            "severity": record.levelname,
                            "jsonPayload": {
                                "module": record.module,
                                "message": record.getMessage()
                            },
                            "logName": "projects/" + self.project_id + "/logs/" + record.name,
                            "resource": {
                                "type": "global",
                            }
                        }
                    ]
                }
        ).execute()
