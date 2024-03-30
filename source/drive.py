from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def connection():
    SCOPES = ["https://www.googleapis.com/auth/drive.metadata"]
    res = service_account.Credentials.from_service_account_file(
    filename='creds.json', 
    scopes=SCOPES)  
    try:
        service = build('drive', 'v3', credentials=res)

    except HttpError as error:
        print(f'An Http error occurred: {error}')
    
    except Exception as generic_error:
        print(f'Fatal error happened in **func connection()** {generic_error}')

    return service

def get_files_query(query: str):
    service = connection()
    results = service.files().list(
                corpora='allDrives',
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                pageSize=1000, 
                fields="nextPageToken, files(id, name, parents, mimeType)", q=query).execute()
    items = results.get('files', [])
    return items

def get_files():
    service = connection()
    results = service.files().list(
                corpora='user',
                pageSize=1000, 
                fields="nextPageToken, files(id, name, parents, mimeType)"
                ).execute()
    items = results.get('files', [])
    return items

def get_all_files():
     params = {'pageToken':None}
     while True:
        response = connection().files().list(**params).execute()
        for f in response['files']:
            yield f
        try:
            params['pageToken'] = response['nextPageToken']
        except KeyError:
            return

def get_first_level():
    items = get_files()
    if not items:
        print('No files found.')
        return
    data = []
    for item in items:
        try:
            if item['parents']:
                continue
        except KeyError :
            data.append({'name': item['name'], 
                         'id': item['id'], 
                         'Type':item['mimeType']
                         })
    return data



def iterfiles(name=None, *, is_folder=None, parent=None, id=None,
              order_by='folder,name,createdTime'):
    q = []
    if name is not None:
        q.append("name = '{}'".format(name.replace("'", "\\'")))
    if is_folder is not None:
        q.append("mimeType {} '{}'".format('=' if is_folder else '!=', 'application/vnd.google-apps.folder'))
    if parent is not None:
        q.append("'{}' in parents".format(parent.replace("'", "\\'")))
    if id is not None:
        q.append("'{}' in id".format(id.replace("'", "\\'")))

    params = {'pageToken': None, 'orderBy': order_by}
    if q:
        params['q'] = ' and '.join(q)

    while True:
        response = connection().files().list(**params).execute()
        for f in response['files']:
            yield f
        try:
            params['pageToken'] = response['nextPageToken']
        except KeyError:
            return

def walk(top=None, *, by_name: bool = False, id=None, entity_name=None):
    try:
        if by_name:
            top = iterfiles(name=top, is_folder=True, id=id)
        else:
            top = connection().files().get(fileId=id).execute()
            if top['mimeType'] != 'application/vnd.google-apps.folder':
                raise ValueError(f'not a folder: {top!r}')

        stack = [((top['name'],), top)]
        while stack:
            path, top = stack.pop()

            dirs, files = is_file = [], []
            for f in iterfiles(parent=top['id']):
                is_file[f['mimeType'] != 'application/vnd.google-apps.folder'].append(f)

            yield path, top, dirs, files
            
            if dirs:
                stack.extend((path + (d['name'],), d) for d in reversed(dirs))
    except TypeError as type_error:
        print(f"Type Error in ***func walk()*** for entity: {entity_name} and type: {type_error}")

def get_folder_structure(func: tuple) -> list:
    data = []
    for id in func:
        for kwargs in [{'by_name': False, 'id': id['id'], 'entity_name': id['name']}, {}]:
            try:
                for path, root, dirs, files in walk(**kwargs):
                    data.append({'path':'/'.join(path), 'nbre_folders': f'{len(dirs):d}',  'nbre_files': f'{len(files):d}'})
            except Exception as e:
                print(id['name'], e)
    return data

def main():
    data= [i for i in get_first_level()]
    return data
    # data = [i for i in get_all_files()] 
    # return data

    
  
