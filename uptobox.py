import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import json

token = '3bf2cfea5f6e4dca446bacd12d426ce9ceu6j'
baseheaders = {'user-agent':'Mozilla/5.0 (Linux; Android 10; dandelion) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36'}

import aiohttp
import asyncio

async def get_download_link(token, file_code):
    async with aiohttp.ClientSession() as session:
        url = f"https://uptobox.com/api/link"
        payload = {
            'token': token,
            'file_code': file_code,
            'return_url': '0'
        }
        try:
            async with session.post(url, data=payload) as resp:
                data = await resp.json()
                if data['status'] == 'ok':
                    return data['data']['dlLink']
                else:
                    print(f"Error al obtener el enlace de descarga: {data['message']}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Error en la solicitud a la API de Uptobox: {e}")
            return None

async def download_file(download_link, file_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(download_link) as resp:
            if resp.status == 200:
                with open(file_path, 'wb') as f:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
            else:
                print(f"Error al descargar el archivo: {resp.status}")
                return None

async def GetWaitingtoken(token,file_code):
    async with aiohttp.ClientSession() as session:
        url = f"https://uptobox.com/api/link"
        payload = {
            'token': token,
            'file_code': file_code,
            'password':''
        }
        try:
            async with session.post(url, data=payload) as resp:
                data = await resp.read()
                print(data)
                if data['status'] == 'ok':
                    return data['data']['dlLink']
                else:
                    print(f"Error al obtener el enlace de descarga: {data['message']}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Error en la solicitud a la API de Uptobox: {e}")
            return None

# Ejemplo de uso
async def main():
    #https://uptobox.com/wrc7x6l4yhd8
    token = '3bf2cfea5f6e4dca446bacd12d426ce9ceu6j'
    file_code = "wrc7x6l4yhd8"
    download_link = await GetWaitingtoken(token, file_code)
    if download_link:
        await download_file(download_link, "mi_archivo_descargado.zip")
        print("Archivo descargado exitosamente")
        
asyncio.run(main())