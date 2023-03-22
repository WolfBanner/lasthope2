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

import socket
import socks

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
    
    async def login(self):
        print("Login")
        loginurl = self.path + 'index.php/login'
        async with self.session.get(loginurl, proxy=self.proxy, headers=self.baseheaders, timeout = 10) as resp:
            soup = BeautifulSoup(await resp.text(), 'html.parser')
            requesttoken = soup.find('head')['data-requesttoken']
            timezone = 'America/Havana'
            timezone_offset = '-5'
            payload = {'user': self.user, 'password': self.password, 'timezone': timezone, 'timezone_offset': timezone_offset, 'requesttoken': requesttoken}
            async with self.session.post(loginurl, data=payload, proxy=self.proxy, headers=self.baseheaders) as resp:
                soup = BeautifulSoup(await resp.text(), 'html.parser')
                title = soup.find('div', attrs={'id': 'settings'})
                if title:
                    print('E Iniciado Correctamente')
                    return True
                print('Error al Iniciar Correctamente')
                return False
    
    async def upload_file(self, file_path, path=None):
        if not await self.login():
            return
        if not path:
            path = '/'
        files = self.path + 'index.php/apps/files/'
        async with self.session.get(files,headers=self.baseheaders) as respo:
            soup = BeautifulSoup(await respo.text(),'html.parser')
            requesttoken = soup.find('head')['data-requesttoken']
        upload_url = self.path + 'remote.php/webdav/' + path + os.path.basename(file_path)
        async with self.session.put(upload_url, data=open(file_path, 'rb'),headers = {'requesttoken': requesttoken, **self.baseheaders,'Connection': 'keep-alive','User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0',"Content-Type": 'application/octet-stream','Slug': os.path.basename(file_path)}, proxy=self.proxy) as resp:
            if resp.status == 201 or resp.status == 204:
                await self.session.close()
                return resp.url
            else:
                print(resp.status)
                print(await resp.text())
                await self.session.close()
                return f"Ha ocurrido un error al subir {str(traceback.format_exc())}"
                
#async def main():
#    # Crea una instancia de NexCloudClient
#    client = NexCloudClient(user='maralonso', password='lorena#5')
#    print("Logueado y subiendo")
#    await client.upload_file('config.json')

#loop = asyncio.get_event_loop()
#loop.run_until_complete(main())

