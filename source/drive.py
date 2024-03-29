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
                fields="nextPageToken, files(id, name, parents, mimeType)").execute()
    items = results.get('files', [])
    return items

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

"""
    Main function
"""
def main():

    folders = []
    document = []
    pdf = []
    mp4 = []

    try:
        for i in get_first_level():
            match i['Type']:
                case 'application/vnd.google-apps.folder':
                    folders.append(i)
                case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    document.append(i)
                case 'application/pdf':
                    pdf.append(i)
                case 'video/mp4':
                    mp4.append(i)

            print('Number of pdf files {0}'.format(len(pdf)))
            print('Names:')
            [print(i['name'], i['id']) for i in pdf]
            print("---------------\n")
            print('Number of Folders {0}'.format(len(folders))) 
            print('Names:')
            [print(i['name'], i['id']) for i in folders]   
            print("---------------\n")
            print('Number of Other documents {0}'.format(len(document)))
            print('Names:')
            [print(i['name'], i['id']) for i in document]
            print("---------------\n")
            print('Number of Other documents {0}'.format(len(mp4)))
            print('Names:')
            [print(i['name'], i['id']) for i in mp4]
    
    except TypeError as type_error:        
        print(f'Type Error in ***func get_first_level()*** {type_error}')  
 

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

def walk(top=None, *, by_name: bool = False, id ='1-1ccqaNumWCBzNr0XXxueInrexA776bo'):
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
        print(f"Type Error in ***func walk()*** : {type_error}")

for kwargs in [{'top': 'spam', 'by_name': True}, {}]:
    for path, root, dirs, files in walk(**kwargs):
        print('/'.join(path), f'===> nbre folders: {len(dirs):d} nbre files: {len(files):d}', sep='\t')

if __name__ == "__main__":
    # main()
    walk()
