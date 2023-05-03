import asyncio
import os
import httpx
import re
from utiles import Progress
import time
import traceback

async def DownloadDirectLink(url, msg,file_path=None):
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",'Connection': 'keep-alive'}
    ) as client:
        async with client.stream("GET", url, timeout=20, follow_redirects=True) as req:
            try:
                file_name = ""
                start_time = time.time()
                current = 0
                prog = Progress()
                file_size = int(req.headers.get("Content-Length", 0))
                if file_path == None:
                    try:
                        m = re.search(
                        'filename="(.*)"', req.headers['Content-Disposition']
                        )
                        file_name  = m.groups()[0]
                        file_path = f"./downloads/{file_name}"
                    except:
                        print(traceback.format_exc())
                with open(file_path, "wb") as f:
                    async for chunk in req.aiter_bytes(chunk_size=1024):
                        current += (len(chunk))
                        f.write(chunk)
                        await prog.progress_bar(current, file_size, file_name, msg, start_time)
            except Exception as ex:
                print("Error: " +  str(ex))        
    return file_name, file_size

async def GetFileName(url):
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0"}
    ) as client:
        async with client.stream("GET", url, timeout=20, follow_redirects=True) as req:
            try:
                file_name = ""
                file_name = (re.search(
                    'filename="(.*)"', req.headers['Content-Disposition']
                    )).groups()[0]
            except:
                print(traceback.format_exc())
    return file_name

async def GetFileSize(url):
    async with httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0"}
    ) as client:
        async with client.stream("GET", url, timeout=20, follow_redirects=True) as req:
            try:
                file_size = 0
                file_size = int(req.headers.get("Content-Length", 0))
            except:
                print(traceback.format_exc())
    return file_size

#async def main():
#    url = "https://www.mediafire.com/file/ym339qev22qto0x"
#    await DownloadDirectLink("https://download2389.mediafire.com/hzcym3s8jvugGW88AyK6A8jLQHMwPJC4pwtTSnRPsk5a7loWDze9abp0naMt5Zx5gaYz11DxH9RQkkSfMCOSpKf8qmSOo3E/ybpyveelg9fwj2x/MediaFire+-+Getting+Started.pdf",)#, file_path, file_size, file_name)

#asyncio.run(main())
