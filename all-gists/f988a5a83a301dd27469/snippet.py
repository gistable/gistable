"""Google spreadsheet related.

Packages required: gspread, cryptography, oauth2client, google-api-python-client

For OSX see

* http://stackoverflow.com/a/33508676/315168
"""
import logging

from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

import gspread
from gspread.models import Spreadsheet

logger = logging.getLogger(__name__)


def get_credentials(scopes: list) -> ServiceAccountCredentials:
    """Read Google's JSON permission file.

    https://developers.google.com/api-client-library/python/auth/service-accounts#example

    :param scopes: List of scopes we need access to
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name('conf/google.json', scopes)
    return credentials


def open_google_spreadsheet(spreadsheet_id: str) -> Spreadsheet:
    """Open sheet using gspread.

    :param spreadsheet_id: Grab spreadsheet id from URL to open. Like *1jMU5gNxEymrJd-gezJFPv3dQCvjwJs7QcaB-YyN_BD4*.
    """
    credentials = get_credentials(['https://spreadsheets.google.com/feeds'])
    gc = gspread.authorize(credentials)
    return gc.open_by_key(spreadsheet_id)


def create_google_spreadsheet(title: str, parent_folder_ids: list=None, share_domains: list=None) -> Spreadsheet:
    """Create a new spreadsheet and open gspread object for it.

    .. note ::

        Created spreadsheet is not instantly visible in your Drive search and you need to access it by direct link.

    :param title: Spreadsheet title

    :param parent_folder_ids: A list of strings of parent folder ids (if any).

    :param share_domains: List of Google Apps domain whose members get full access rights to the created sheet. Very handy, otherwise the file is visible only to the service worker itself. Example:: ``["redinnovation.com"]``.
    """

    credentials = get_credentials(['https://www.googleapis.com/auth/drive'])

    drive_api = build('drive', 'v3', credentials=credentials)

    logger.info("Creating Sheet %s", title)
    body = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.spreadsheet',
    }

    if parent_folder_ids:
        body["parents"] = [
            {
                'kind': 'drive#fileLink',
                'id': parent_folder_ids
            }
        ]

    req = drive_api.files().create(body=body)
    new_sheet = req.execute()

    # Get id of fresh sheet
    spread_id = new_sheet["id"]

    # Grant permissions
    if share_domains:
        for domain in share_domains:

            # https://developers.google.com/drive/v3/web/manage-sharing#roles
            # https://developers.google.com/drive/v3/reference/permissions#resource-representations
            domain_permission = {
                'type': 'domain',
                'role': 'writer',
                'domain': domain,
                # Magic almost undocumented variable which makes files appear in your Google Drive
                'allowFileDiscovery': True,
            }

            req = drive_api.permissions().create(
                fileId=spread_id,
                body=domain_permission,
                fields="id"
            )

            req.execute()

    spread = open_google_spreadsheet(spread_id)

    return spread
