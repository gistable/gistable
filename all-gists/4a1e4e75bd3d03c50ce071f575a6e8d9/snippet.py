"""Google spreadsheet related.
Packages required: oauth2client, google-api-python-client
* https://gist.github.com/miohtama/f988a5a83a301dd27469
"""

from oauth2client.service_account import ServiceAccountCredentials
from apiclient import discovery


def get_credentials(scopes: list) -> ServiceAccountCredentials:
    c = ServiceAccountCredentials.from_json_keyfile_name('auth.json', scopes)
    return c


class API:
    def __init__(self, credentials):
        self._credentials = credentials

    def build(self, service, version):
        return discovery.build(service, version, credentials=self._credentials)

    def get_api_kwargs(self):
        return {
            'credentials': self._credentials,
        }


class Spreadsheet(API):
    def __init__(self, info, **kwargs):
        self._info = info
        super().__init__(**kwargs)

    @property
    def id(self):
        return self._info['spreadsheetId']

    @property
    def permissions(self):
        permissions = self._get_permissions()
        anyone = None
        writers = []
        readers = []
        for x in permissions:
            type = x['type']  #: 'user', 'anyone', 'group', 'domain'
            role = x['role']  #: 'owner', 'commenter', 'reader', 'writer'
            if type == 'anyone':
                if role in ['owner', 'writer']:
                    anyone = 'write'
                elif role in ['reader']:
                    anyone = 'read'
                elif role in ['commenter']:
                    anyone = 'comment'
            elif type == 'user':
                x = self._get_permission(x['id'])
                if role in ['owner', 'writer']:
                    lst = writers
                elif role in ['reader', 'commenter']:
                    lst = readers
                else:
                    raise RuntimeError('Protocol role unknown!')
                lst.append(x['emailAddress'])
        return {
            'anyone': anyone,
            'writers': writers,
            'readers': readers,
        }

    def set_permissions(self, anyone=None, writers=None, readers=None):
        assert anyone in [None, 'writer', 'write',
                          'reader', 'read', 'w', 'r'], 'not in ["r", "w"]'

        drive = self.build('drive', 'v3')
        if anyone:
            role = {
                'r': 'reader',
                'read': 'reader',
                'reader': 'reader',
                'w': 'writer',
                'write': 'writer',
                'writer': 'writer',
            }
            body = {
                'role': role[anyone],
                'type': 'anyone',
            }
            drive.permissions().create(fileId=self.id, body=body).execute()
        if writers:
            body = {
                'role': 'writer',
                'type': 'user',
                'emailAddress': writers,
            }
            drive.permissions().create(fileId=self.id, body=body).execute()
        if readers:
            body = {
                'role': 'reader',
                'type': 'user',
                'emailAddress': readers,
            }
            drive.permissions().create(fileId=self.id, body=body).execute()

    def _get_permissions(self):
        drive = self.build('drive', 'v3')
        r = drive.permissions().list(fileId=self.id).execute()
        permissions = r.get('permissions', [])
        return permissions

    def _get_permission(self, id):
        drive = self.build('drive', 'v3')
        fields = 'allowFileDiscovery,displayName,domain,emailAddress,' \
                 'expirationTime,id,kind,photoLink,role,type'
        permission = drive.permissions().get(
            fileId=self.id, permissionId=id, fields=fields)
        return permission.execute()

    def append(self, data, gray=False, sheet=0):
        spreadsheets = self.build('sheets', 'v4').spreadsheets()
        value = lambda x: {  # noqa
            "userEnteredValue": {"stringValue": str(x)},
            "userEnteredFormat": {"backgroundColor": {
                "red": 0.8, "green": 0.8, "blue": 0.8, "alpha": 0.5}
            }
        } if gray else {
            "userEnteredValue": {"stringValue": str(x)}
        }

        rows = [{"values": [value(cell) for cell in row]} for row in data]
        body = {
            "requests": [
                {
                    "appendCells": {
                        "sheetId": sheet,
                        "rows": rows,
                        "fields": "*",
                    }
                }
            ],
        }

        return spreadsheets.batchUpdate(spreadsheetId=self.id, body=body) \
            .execute()

    def __str__(self):
        return "Sheet(%s)" % self.id


class Spreadsheets(API):
    def create(self, title, anyone=None, writers=None, readers=None):
        assert anyone in [None, 'write', 'read', 'comment', 'w', 'r', 'c'], \
            'not in ["r", "w", "c"]'
        sheets = self.build('sheets', 'v4')
        body = {'properties': {'title': title}}
        res = sheets.spreadsheets().create(body=body).execute()
        spreadsheer = Spreadsheet(res, **self.get_api_kwargs())
        spreadsheer.set_permissions(anyone=anyone, writers=writers,
                                    readers=readers)
        return spreadsheer

    def get(self, id):
        sheets = self.build('sheets', 'v4')
        res = sheets.spreadsheets().get(spreadsheetId=id).execute()
        return Spreadsheet(res, **self.get_api_kwargs())


def create_example():
    credentials = get_credentials([
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'])
    api = Spreadsheets(credentials=credentials)
    sheet = api.create('test1', writers=['pahaz.blinov@gmail.com'])
    print(sheet)


def append_data_example():
    credentials = get_credentials([
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'])
    api = Spreadsheets(credentials=credentials)
    sheet = api.get('1jSHsmPTOOiPXdYQlrVBwbo3MO1vp64lmi5R_Ld_duKo')
    sheet.append([[1, 2], [3, 4]])


if __name__ == '__main__':
    append_data_example()
