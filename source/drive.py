from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def connection():
    SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    res = service_account.Credentials.from_service_account_file(
    filename='creds.json', 
    scopes=SCOPES)  
    try:
        service = build('drive', 'v3', credentials=res)

    except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
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
                         'Type':item['mimeType']})
    return data

"""
    Main function
"""
def main():
    folders = []
    document = []
    pdf = []
    mp4 = []

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
 

if __name__ == "__main__":
  main()