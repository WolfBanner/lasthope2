import humanize
import time
import os
import aiohttp
from bs4 import BeautifulSoup
import psutil

class Progress():
    def __init__(self):
        self.current = 0
        self.download_msg = "#download\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]" #Name Size Percent/Elapsed
        self.time = time.time()
        self.count = 10
        
    async def progress_bar(self,current, total, file_name, msg,start_time):
        # Función callback para mostrar el progreso de la descarga
        if current == total:
            await self.restore_count()
        percent = current * 100 / total
        if self.count < time.time() - start_time:
            await msg.edit(self.download_msg.format(file_name,humanize.naturalsize(total),(str(round(percent,2)))+" %"))
            self.count += 10
            
    async def megaprogress(self, stream, process, msg, start_time):
        if self.count < time.time() - start_time:
            await msg.edit(f"<b>{str(stream[-1])}</b>")
        #print(stream[-1])
        
    async def restore_count(self):
        self.count = 10
        
def mib_to_bytes(mib):
    bytes = mib * 1024 * 1024
    return bytes

async def GetFileNameMega(files: list, path: str = "./downloads/"):
    filename = ''
    #files = await listar_archivos(path)
    #print(files)
    actual_files = await listar_archivos(path)
    for file in actual_files:
        if not file in files:
            filename = file
            break
    return os.path.basename(f'./downloads/{str(filename)}')

async def listar_archivos(path: str = "./downloads/"):
    files = []
    with os.scandir(path) as directory:
        for file in directory:
            if file.is_file():
                if file.name == 'l':
                    pass
                else:
                    files.append(file.name)
    return files

async def GetMegaFolderName(url: str):
    async with aiohttp.ClientSession().get(url) as resp:
        soup = BeautifulSoup(await resp.text, 'html.parser')
        #print(soup)

async def get_system_info():
    # Obtener el uso de CPU
    cpu_percent = psutil.cpu_percent(interval=1)

    # Obtener el uso de memoria RAM
    mem = psutil.virtual_memory()
    mem_used = mem.used
    mem_total = mem.total

    # Obtener el uso de almacenamiento
    current_disk = psutil.disk_partitions(all=False)[0].mountpoint
    disk = psutil.disk_usage(current_disk)
    disk_used = disk.used
    disk_total = disk.total

    # Devolver un diccionario con la información obtenida
    return {
        'cpu_percent': cpu_percent,
        'mem_used': humanize.naturalsize(mem_used),
        'mem_total': humanize.naturalsize(mem_total),
        'disk_used': humanize.naturalsize(disk_used),
        'disk_total': humanize.naturalsize(disk_total)
    }

#import asyncio  
#x = asyncio.run(get_system_info())
#print(x)
#10MB.bin: 9.23% - 436.1 KiB (446600 bytes) of 4.6 MiB (20.2 KiB/s)
#10MB.bin: 0.00% - 0 bytes of 4.6 MiB

#10MB.bin: 3.01% - 293.9 KiB (301000 bytes) of 9.5 MiB (42.0 KiB/s)
