import os.path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError



"""
    Main function
"""
def main():
    SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
    res = service_account.Credentials.from_service_account_file(
    filename='source/creds.json', 
    scopes=SCOPES)  
    try:
        service = build('drive', 'v3', credentials=res)
        results = service.files().list(
                pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')
  
    

if __name__ == "__main__":
  main()