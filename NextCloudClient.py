import os
import traceback
import aiohttp
from aiohttp import MultipartWriter
from functools import partial
import time
import re
from bs4 import BeautifulSoup
import uuid
import asyncio
import os
from search import buscar_archivo


class CloudUpload:
    def __init__(self, func, filename, args):
        self.func = func
        self.args = args
        self.filename = filename
        self.time_start = time.time()
        self.time_total = 0
        self.speed = 0
        self.last_read_byte = 0
    
    def __call__(self, monitor):
        self.speed += monitor.bytes_read - self.last_read_byte
        self.last_read_byte = monitor.bytes_read
        tcurrent = time.time() - self.time_start
        self.time_total += tcurrent
        self.time_start = time.time()
        if self.time_total >= 1:
            clock_time = (monitor.len - monitor.bytes_read) / (self.speed)
            if self.func:
                self.func(self.filename, monitor.bytes_read, monitor.len, self.speed, clock_time, self.args)
            self.time_total = 0
            self.speed = 0

class NexCloudClient:
    def __init__(self, user, password, path='https://nube.uclv.cu/'):
        self.user = user
        self.password = password
        self.session = aiohttp.ClientSession()
        self.path = path
        self.tokenize_host = 'https://tguploader.url/'
        self.proxy=None
        self.baseheaders = {'user-agent':'Mozilla/5.0 (Linux; Android 10; dandelion) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36'}
        self.requesttoken = None
    
    async def login(self):
        loginurl = self.path + 'index.php/login'
        async with self.session.get(loginurl, proxy=self.proxy, headers=self.baseheaders, timeout = 20) as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser')
            self.requesttoken = soup.find('head')['data-requesttoken']
            timezone = 'America/Havana'
            timezone_offset = '-5'
            payload = {'user': self.user, 'password': self.password, 'timezone': timezone, 'timezone_offset': timezone_offset, 'requesttoken': self.requesttoken}
            async with self.session.post(loginurl, data=payload, proxy=self.proxy, headers=self.baseheaders, timeout = 10) as resp:
                soup = BeautifulSoup(await resp.text(), 'html.parser')
                title = soup.find('div', attrs={'id': 'settings'})
                if title:
                    print('Inició sesión')
                    return True
                print('No inició sesión')
                return False
    


    async def upload_file(self, file_path, timeout,path=None):
            
        if not await self.login():
            return
        
        if not path:
            path = '/'
            
        files = self.path + 'index.php/apps/files/'
        
        try:
            async with self.session.get(files,headers=self.baseheaders, timeout = 20) as respo:
                soup = BeautifulSoup(await respo.text(),'html.parser')
                requesttoken = soup.find('head')['data-requesttoken']
        except:
            print(f"Error al obtener el requests token en la def upload_file {traceback.format_exc()}")
            
        upload_url = self.path + 'remote.php/webdav/' + path + os.path.basename(file_path)
        try:
            async with self.session.put(upload_url, data=open(file_path, 'rb'),headers = {'requesttoken': requesttoken, **self.baseheaders,'Connection': 'keep-alive','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',"Content-Type": 'application/octet-stream','Slug': os.path.basename(file_path)}, proxy=self.proxy, timeout = timeout) as resp:
                if resp.status == 201 or resp.status == 204:
                    await self.session.close()
                    print(resp)
                    return resp.url
                else:
                    print(resp.status)
                    print(await resp.text())
                    await self.session.close()
                    return f"Ha ocurrido un error al subir {str(traceback.format_exc())}"
        except:
            await self.session.close()
            print(f"Error al intentar subir el archivo {traceback.format_exc()}")
    
    async def Close(self):
        await self.session.close()
        
    async def GetDirectLink(self):
        if not await self.login():
            return
        url_soli = "https://nube.uclv.cu/ocs/v2.php/apps/password_policy/api/v1/generate"
        async with self.session.get(url_soli, headers = {'requesttoken': self.requesttoken, **self.baseheaders,'Connection': 'keep-alive','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'}, timeout = 20) as resp:
            print(await resp.text)
    #recibir por parametros el espacio y retornar true si se puede subir, si no retornar falso, sugiero una variable de control.       
    async def GetSpace(self):
        if not await self.login():
            return
        
        files = self.path + 'index.php/apps/files/'
        
        try:
            try:
                async with self.session.get(files,headers=self.baseheaders, timeout = 20) as respo:
                    soup = BeautifulSoup(await respo.text(),'html.parser')
                    requesttoken = soup.find('head')['data-requesttoken']
            except:
                print("Error al obtener el requests token")
            params = {
                'dir' : '/'
                }
            files = "https://nube.uclv.cu/index.php/apps/files/ajax/getstoragestats"
            async with self.session.get(files,params = params, headers = {'requesttoken': requesttoken, **self.baseheaders,'Connection': 'keep-alive','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0'}, timeout = 20) as respo:
                response = await respo.json()
                #soup = BeautifulSoup(await respo.text(),'html.parser')
                #print(soup)
                print(response)
                free = response['data']['freeSpace']
                total = response['data']['total']
                used = response['data']['used']
                used_percent = response['data']['usedSpacePercent']
                return free, used, total, used_percent
        except:
            print(f"Error al obtener el requests token en la def upload_file {traceback.format_exc()}")
               
#async def main():
#    #Crea una instancia de NexCloudClient
#    client = NexCloudClient(user='llmoreno', password='l56488851*')
#    print("Logueado y subiendo")
#    file_name = ''
#    x = await client.upload_file('./aria2c.exe',20)
#    print(x)

#loop = asyncio.get_event_loop()
#loop.run_until_complete(main())
