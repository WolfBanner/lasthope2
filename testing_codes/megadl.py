import aiohttp
import asyncio
import base64
import re

async def download_file_from_mega(file_url, file_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            print(response.headers)
            data = await response.read()
            #with open(file_name, 'wb') as f:
            #    f.write(data)

#file_url = 'https://mega.nz/file/yuZ0QJ6J#jFc2HL6rIoDVU9kECBpMEIAbcv2WQcz6le9kS_bb2gc'
file_url = 'https://mega.nz/#!RHAFDbZA!KSCMSu9e01sOuog-WSgV4SO_mSIzDQLjSZzz3MmU99s'
file_id, file_key = re.findall(r'!([\w-]+)', file_url)
file_key = base64.urlsafe_b64decode(file_key + '=' * (4 - len(file_key) % 4))
file_key = base64.urlsafe_b64encode(file_key[0:32]).decode()

file_url = f'https://mega.nz/file/{file_id}#{file_key}'
file_name = 'archivo.txt'

loop = asyncio.get_event_loop()
loop.run_until_complete(download_file_from_mega(file_url, file_name))

#asyncio.run(download_url("https://mega.nz/folder/3Kxj2RBK#DTAwT6UYLi6e7gv6TJ2Meg"))

