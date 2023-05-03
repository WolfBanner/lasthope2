import asyncio
import aiohttp
import json
import re
import time
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from utiles import Progress

# Define the scopes you want to authorize
SCOPES = ['https://www.googleapis.com/auth/drive']


async def DownloadGDrive(file_name, file_size, url, msg):
    try:
        progress = Progress()
        current = 0
        downURL = f"{url}&confirm=None"
        #url = f"https://drive.google.com/uc?id={file_id}&export=download&confirm=None"
        async with aiohttp.ClientSession() as session:
            async with session.get(downURL) as response:
                headers = response.headers
                content_type = headers['Content-Type']
                if 'text/html' in content_type:
                    raise Exception("Got HTML page instead of file.")
                start_time = time.time()
                with open(f'./downloads/{file_name}', 'wb') as f:
                    while True:
                        chunk = await response.content.read(2048)
                        current += len(chunk)
                        await progress.progress_bar(current, file_size, file_name, msg, start_time)
                        if not chunk:
                            break
                        f.write(chunk)
                f.close()
                await session.close()
        return file_name
    except Exception as e:
        await session.close()
        print(f'An error occurred: {e}')

async def GetFileData(url):
    # Build the credentials object
    service_credentials = await GetCredentials()
    file_id = await GetFileId(url)
    
    creds = service_account.Credentials.from_service_account_info(
        service_credentials, scopes=SCOPES)

    # Refresh the access token if necessary
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Create a Drive API client using the service account credentials
    service = build('drive', 'v2', credentials=creds)

    # Get file metadata
    data = service.files().get(fileId=file_id).execute()
    fileSize = data['fileSize']
    originalFilename = data['originalFilename']
    webContentLink = data['webContentLink']
    
    return {
        'fileName' : originalFilename, 
        'fileSize' : fileSize, 
        'url' : webContentLink, 
        'fileID' : file_id 
        }
            
async def GetCredentials():
    with open('service-account.json', 'r') as f:
        service_credentials = json.load(f)
    f.close()
    return service_credentials

async def GetFileId(url):
    if "view?usp=sharing" in url:
        file_id = url.split('/')[-2]
    elif "export=download" in url:
        file_id = (re.search(r"id=([^&]+)", url)).group(1)
    return file_id

#### test
async def get_confirm_token(headers):
    for key, value in headers.items():
        if key.startswith('Set-Cookie') and 'download_warning' in value:
            return value.split('download_warning=')[1].split(';')[0]
    return None
  
#async def main():
#    # Load the service account credentials from a JSON file
#    url = "https://drive.google.com/file/d/19A-IWkcWlYKd-vbyelsShQOzPJoSHcwP/view?usp=sharing"
#    #url = "https://drive.google.com/uc?id=19A-IWkcWlYKd-vbyelsShQOzPJoSHcwP&export=download"
#    
#    # Download the file using the service account credentials
#    await DownloadGDrive(url)
#
#asyncio.run(main())
