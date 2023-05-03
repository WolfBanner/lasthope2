import asyncio
import aiohttp
import re

async def DownloadGDrive(url):
    try:
        file_id = await GetFileId(url)
        directURL = await GetDirectURL(file_id)
        #url = f"https://drive.google.com/uc?id={file_id}&export=download&confirm=None"
        async with aiohttp.ClientSession() as session:
            async with session.get(directURL) as response:
                headers = response.headers
                file = re.search(
                  'filename="(.*)"', response.headers['Content-Disposition']  
                )
                file_name = file.groups()[0]
                print(file_name)
                file_size = int(headers.get('Content-Length'), 0)
                print(file_size) #en bytes
                content_type = headers['Content-Type']
                if 'text/html' in content_type:
                    raise Exception("Got HTML page instead of file.")
                with open(f'./downloads/{file_name}', 'wb') as f:
                    while True:
                        chunk = await response.content.read(2048)
                        if not chunk:
                            break
                        f.write(chunk)
                f.close()
                await session.close()
    except Exception as e:
        print(f'An error occurred: {e}')

async def GetDirectURL(file_id):
    return f"https://drive.google.com/uc?id={file_id}&export=download&confirm=None"


async def GetFileId(url):
    if "view?usp=sharing" in url:
        file_id = url.split('/')[-2]
    elif "export=download" in url:
        file_id = (re.search(r"id=([^&]+)", url)).group(1)
    return file_id

#### testear esto es para archivos que piden confirmacion
async def get_confirm_token(headers):
    for key, value in headers.items():
        if key.startswith('Set-Cookie') and 'download_warning' in value:
            return value.split('download_warning=')[1].split(';')[0]
    return None
  
async def main():
    url = "https://drive.google.com/file/d/19A-IWkcWlYKd-vbyelsShQOzPJoSHcwP/view?usp=sharing"
    #url = "https://drive.google.com/uc?id=19A-IWkcWlYKd-vbyelsShQOzPJoSHcwP&export=download"
    
    await DownloadGDrive(url)

asyncio.run(main())
