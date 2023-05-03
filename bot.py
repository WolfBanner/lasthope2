import os
import time
import zipfile
import multiFile
import asyncio
import traceback
import humanize
import datetime
from mediafire import DownloadDirectLink, GetFileName, GetFileSize
import aiohttp

from gddl import DownloadGDrive, GetFileData
from utiles import Progress, listar_archivos, GetFileNameMega, get_system_info
from pymegatools import Megatools, MegaError
from NextCloudClient import NexCloudClient
from config import Config
from zipfile import ZipFile
from pyrogram import Client, filters
from aiohttp import web
from search import buscar_archivo
from zipstream import AioZipStream
# from megadl import download_url


class Bot():
    def __init__(self):
        self.cfg = Config()
        self.bot_token = self.cfg.bot_token
        self.api_id = self.cfg.api_id
        self.api_hash = self.cfg.api_hash
        self.client = Client('bot', bot_token=self.bot_token,
                             api_id=self.api_id, api_hash=self.api_hash)
        self.chat_id = 1028272649
        self.tasks = []
        self.semaphore = asyncio.Semaphore(2)
        self.speed = 0.0
        self.progress = 0
        # Name Size Percent/Elapsed
        self.download_msg = "#download\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]"
        # Name Size Percent
        self.compress_msg = "#compress\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]"
        # Name Size Result
        self.upload_msg = "#upload\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]"
        # Name Size Status
        self.uploaded_msg = "#uploaded\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]"
        self.upload_msg_error = "#uploaded\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]\n<b>[{}]</b>"
        self.app_name = "last1.3"
        self.ExcludeFiles = ['ProxyCloud.py', 'NextCloudClient.py', 'bot.py', 'mediafire_dl.py', 'multiFile.py',
                             'Client.py', 'requirements.txt', 'Procfile', '__pycache__', '.git', '.profile.d',
                             '.heroku', 'bot.session', 'bot.session-journal', 'output', 'Actualizar heroku.bat',
                             'runtime.txt', 'config.py', '.env', 'README.md', '.gitignore', 'config.json', 'downloads', 'utils', 'utiles.py','./downloads/l']
        self.routes = [web.get("/", self.hello)]
        self.web_host = None
        self.current = 0
        self.percent = 0
        self.time = 0
        self.cont = 10
        self.default_dir = os.path.abspath("")
        self.downloaded_files = []
        self.stats = "Server Stats:\n<b>CPU: {}%\nMEM: {}/{}\nDisk: {}/{}</b>\n\nCloud Stats:\n<b>Free: {}\nUsed: {}\nTotal: {}\n Used Percent: {}</b>"

        @self.client.on_message(filters.all & filters.private)
        async def Handler(client, event):
            # print(event)
            if self.chat_id == 0:
                self.chat_id = event.chat.id
            if self.time == 0:
                self.time = datetime.datetime.now()

            if event.chat.id == self.chat_id or event.chat.id == 6099400516:
                if event.text == "/start":
                    elapsed_time = datetime.datetime.now() - self.time
                    days = elapsed_time.days
                    hours, remainder = divmod(elapsed_time.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    await client.send_message(event.chat.id, f"Hi, this is a welcome message... \n\n<b>Time alive:</b>\n<b>Days: {(days)}</b>\n<b>Hours: {(hours)}</b>\n<b>Minutes: {(minutes)}</b>\n<b>Seconds: {(seconds)}</b>")
                elif event.text == "/slow":
                    self.cfg.slow_mode = True
                    self.cfg.waitTime = None
                    msg = await client.send_message(event.chat.id, f"<b>Config Changed:\n\n</b>Slow mode: <code>Enabled</code>\nUpload time: ♾️", reply_to_message_id=event.id)   
    
                elif event.text == "/fast":
                    self.cfg.slow_mode = False
                    self.cfg.waitTime = 1800
                    msg = await client.send_message(event.chat.id, f"<b>Config Changed:\n\n</b>Slow mode: <code>Disabled</code>\nUpload time: <code>1800s</code>", reply_to_message_id=event.id)  
                                     
                elif str(event.text).startswith("/up "):
                    file_name = str(event.text).replace("/up ", "")
                    file_size = 0
                    self.downloaded_files = sorted(await listar_archivos())
                    if file_name in self.downloaded_files:
                        file_size = (
                            os.stat(f"./downloads/{file_name}")).st_size
                        msg = await client.send_message(event.chat.id, self.download_msg.format(file_name, humanize.naturalsize(file_size), "Pending"), reply_to_message_id=event.id)
                        task_up = asyncio.create_task(
                            self.ProcessUpload(file_name, file_size, msg, True))
                        self.tasks.append(task_up)
                        self.cont = 10
                    else:
                        msg = await client.send_message(event.chat.id, f"<b>ERROR:</b>\n\n<code>File: {file_name}\nInfo: The file does not exists in that directory</code>", reply_to_message_id=event.id)
                
                elif str(event.text).startswith("/zip "):
                    try:
                        zipzize = str(event.text).replace("/zip ", "")
                        zipzize = int(zipzize)
                        older_size = self.cfg.zip_size
                        self.cfg.zip_size = zipzize
                        msg = await client.send_message(event.chat.id, f"<b>Config Changed:\n\n</b>Older Size: <code>{older_size}</code>\nNew Size: <code>{zipzize}</code>", reply_to_message_id=event.id)
                    except Exception as ex:
                        msg = await client.send_message(event.chat.id, f"<b>ERROR:\n\n</b><code>{ex}</code>", reply_to_message_id=event.id)
                    
                
                # Implementar esta funcionalidad
                elif str(event.text).startswith("/bulk_up "):
                    pass

                elif event.text == "/ls":
                    self.downloaded_files = sorted(await listar_archivos())
                    text = "<b>Files in directory:</b>\n\n"
                    cont = 0
                    for file in self.downloaded_files:
                        text += f"<b>{str(cont)}</b> - <code>{str(file)}</code>\n"
                        cont += 1
                    await client.send_message(event.chat.id, text, reply_to_message_id=event.id)

                elif event.text == "/stats":
                    stats = await get_system_info()
                    nex = NexCloudClient(self.cfg.alteruser, self.cfg.alterpassword)
                    free, used, total, percent = await nex.GetSpace()
                    msg = await client.send_message(event.chat.id,
                                                    self.stats.format(stats.get("cpu_percent"),
                                                                      stats.get(
                                                                          "mem_used"),
                                                                      stats.get(
                                                                          "mem_total"),
                                                                      stats.get(
                                                                          "disk_used"),
                                                                      stats.get(
                                                                          "disk_total"),
                                                                      humanize.naturalsize(
                                                                          free),
                                                                      humanize.naturalsize(
                                                                          used),
                                                                      humanize.naturalsize(
                                                                          total),
                                                                      f"{str(percent)}/100.00"), reply_to_message_id=event.id)

                elif event.document != None:
                    msg = await client.send_message(event.chat.id, self.download_msg.format(event.document.file_name, humanize.naturalsize(event.document.file_size), "Pending"), reply_to_message_id=event.id)
                    # Creamos una tarea para descargar el archivo
                    task_document = asyncio.create_task(self.DownloadFile(
                        event.document.file_name, event.document.file_size, msg, client, event, "document"))
                    # Añadimos la tarea a la lista
                    self.tasks.append(task_document)
                    self.cont = 10

                elif event.video != None:
                    msg = await client.send_message(event.chat.id, self.download_msg.format(event.video.file_name, humanize.naturalsize(event.video.file_size), "Pending"), reply_to_message_id=event.id)
                    # Creamos una tarea para descargar el archivo
                    task_video = asyncio.create_task(self.DownloadFile(
                        event.video.file_name, event.video.file_size, msg, client, event, "media"))
                    # Añadimos la tarea a la lista
                    self.tasks.append(task_video)
                    self.cont = 10
                    
                elif "drive.google.com" in event.text:
                    msg = await client.send_message(event.chat.id, self.download_msg.format("GoogleDrive", "Link", "Pending"), reply_to_message_id=event.id)
                    task_gdrive = asyncio.create_task(
                            self.DownloadGoogleDrive(event.text, msg))
                    self.tasks.append(task_gdrive)
                    self.cont = 10
                    
                elif "mega" in event.text:
                    if "folder" in event.text:
                        msg = await client.send_message(event.chat.id, self.download_msg.format("MegaFolder", "Link", "Pending"), reply_to_message_id=event.id)
                        task_mega = asyncio.create_task(
                            self.DownloadMegaFolder(event.text, msg))
                        self.tasks.append(task_mega)
                        self.cont = 10
                        pass
                    else:
                        msg = await client.send_message(event.chat.id, self.download_msg.format("Mega", "Link", "Pending"), reply_to_message_id=event.id)
                        task_mega = asyncio.create_task(
                            self.DownloadMega(event.text, msg))
                        self.tasks.append(task_mega)
                        self.cont = 10

                elif "http" in event.text or "https" in event.text:
                    msg = await client.send_message(event.chat.id, self.download_msg.format("MediaFire", "Link", "Pending"), reply_to_message_id=event.id)
                    task_mediafire = asyncio.create_task(
                        self.DownloadMediaFire(event.text, self.client, event, msg))
                    self.tasks.append(task_mediafire)
    
    # Modelo de descargas...
    async def DownloadFile(self, file_name, file_size, msg, client, event, type):
        # Esperamos a que haya disponibilidad en el Semaphore
        await self.semaphore.acquire()
        try:
            start_time = time.time()
            if type == "document":
                recv_data = await client.download_media(event.document, progress=self.progress_bar, progress_args=(file_name, file_size, msg, start_time))
            elif type == "media":
                recv_data = await client.download_media(event.video, progress=self.progress_bar, progress_args=(file_name, file_size, msg, start_time))
            self.tasks.remove(asyncio.current_task())
            await msg.edit(self.download_msg.format(file_name, humanize.naturalsize(file_size), "Finished"))
            self.semaphore.release()
            await self.ProcessUpload(file_name, file_size, msg)
        except:
            self.semaphore.release()
            print(traceback.print_exc())
        finally:
            # Liberamos el Semaphore
            self.semaphore.release()
        
    async def DownloadMegaFolder(self, url: str, msg):
        await self.semaphore.acquire()
        mega = Megatools()
        prog = Progress()
        start_time = time.time()
        if not os.path.exists('./downloads'):
            os.mkdir('./downloads')
        if not os.path.exists("./downloads/MegFolder"):
            os.mkdir('./downloads/MegFolder')
        try:
            await mega.download(url, assume_async=True, progress=prog.megaprogress, progress_arguments=(msg, start_time), path="./downloads/MegFolder")
            self.task.remove(asyncio.current_task())
            self.semaphore.release()
            files = sorted(await listar_archivos("./downloads/MegFolder/"))
            for file in files:
                file_size = os.path.getsize(
                    f"./downloads/MegFolder/{str(file)}")
                await self.ProcessUpload(file, file_size, msg)
        except MegaError as ex:
            print("Error: ", str(ex))
        finally:
            self.semaphore.release()

    async def DownloadMega(self, url: str, msg):
        await self.semaphore.acquire()
        mega = Megatools()
        file_name = mega.filename(url)
        prog = Progress()
        start_time = time.time()
        if not os.path.exists('./downloads'):
            os.mkdir('./downloads')
        self.downloaded_files = sorted(await listar_archivos("./downloads/"))
        try:
            # os.chdir(f"./downloads")
            await mega.download(url, assume_async=True, progress=prog.megaprogress, progress_arguments=(msg, start_time), path="./downloads")
            self.tasks.remove(asyncio.current_task())
            self.semaphore.release()
            file = await GetFileNameMega(self.downloaded_files)
            file_size = os.path.getsize(f"./downloads/{str(file)}")
            await self.ProcessUpload(file_name, file_size, msg)
        except MegaError as ex:
            print("Error: ", str(ex))
        finally:
            self.semaphore.release()
            
    async def DownloadGoogleDrive(self, url, msg):
        await self.semaphore.acquire()
        try:
            data = await GetFileData(url)
            file_name = data.get('fileName')
            file_size = int(data.get('fileSize'))
            downloadURL = data.get('url')
            await msg.edit(self.download_msg.format(file_name, humanize.naturalsize(file_size), "Starting"))
            await DownloadGDrive(file_name, file_size, downloadURL, msg)
            self.tasks.remove(asyncio.current_task())
            self.semaphore.release()
            await self.ProcessUpload(file_name, file_size, msg)
        except Exception as ex:
            self.semaphore.release()
            await msg.edit(traceback.format_exc())
            
    async def DownloadMediaFire(self, url, client, event, msg):
        await self.semaphore.acquire()
        try:
            file_name = await GetFileName(url)
            file_size = await GetFileSize(url)
            await msg.edit(self.download_msg.format(file_name, humanize.naturalsize(file_size), "Starting"))
            await DownloadDirectLink(url, msg)
            self.tasks.remove(asyncio.current_task())
            if self.cfg.slow_mode:
                await self.ProcessUpload(file_name, file_size, msg)
            else:
                self.semaphore.release()
                await self.ProcessUpload(file_name, file_size, msg)
        except:
            self.semaphore.release()
            await msg.edit(traceback.format_exc())
        finally:
            self.semaphore.release()

    async def progress_bar(self, current, total, file_name, file_size, msg, start_time):
        # Función callback para mostrar el progreso de la descarga
        percent = current * 100 / total
        if self.cont < time.time() - start_time:
            await msg.edit(self.download_msg.format(file_name, humanize.naturalsize(file_size), (str(round(percent, 2)))+" %"))
            self.cont += 10

    # Modelo de subidas...

    async def ProcessUpload(self, file_name, file_size, msg, is_up=False):
        if is_up:
            await self.semaphore.acquire()
        try:
            timeout = self.cfg.waitTime
            file_path = await buscar_archivo(file_name, "./")
            # chunk_size = self.cfg.zip_size
            chunk_size = 1024 * 1024 * self.cfg.zip_size
            if file_size > chunk_size:
                # file_path = f"./downloads/{file_name}"
                await msg.edit(self.compress_msg.format(str(file_name), str(humanize.naturalsize(file_size)), len(multiFile.files) + 1 if (len(multiFile.files)) == 0 else len(multiFile.files)))
                mult_file = multiFile.MultiFile(file_path+'.7z', chunk_size)
                async with AioZipStream(mult_file, 'w') as zip:
                    with open(file_path, 'rb') as f:
                        await zip.write(f.read(), arcname=os.path.basename(file_path))
                mult_file.close()
                #zip = ZipFile(mult_file,  mode='w',
                #              compression=zipfile.ZIP_DEFLATED)
                #zip.write(file_path)
                #zip.close()
                #mult_file.close()
                for file in multiFile.files:
                    await msg.edit(self.upload_msg.format(str(file_name), str(humanize.naturalsize(file_size)), len(multiFile.files) + 1 if (len(multiFile.files)) == 0 else len(multiFile.files)))
                    nex = NexCloudClient(self.cfg.user, self.cfg.password)
                    print(file)
                    resp = asyncio.create_task(
                        nex.upload_file(file_path, timeout))
                    resp = await resp
                    # print(resp)
                    # data=data+'\n\n'+str(resp).replace('\\','')
                await msg.edit(self.uploaded_msg.format(str(file_name), str(humanize.naturalsize(file_size)), "OK"))
            else:
                await msg.edit(self.upload_msg.format(str(file_name), str(humanize.naturalsize(file_size)), "Uploading"))
                nex = NexCloudClient(self.cfg.user, self.cfg.password)
                free, used, total, used_percent = await nex.GetSpace()
                if free >= file_size:
                    print(file_name)
                    resp = asyncio.create_task(
                        nex.upload_file(file_path, timeout))
                    resp = await resp
                    await msg.edit(self.uploaded_msg.format(str(file_name), str(humanize.naturalsize(file_size)), f"OK \n {resp}"))
                else:
                    nex2 = NexCloudClient(
                        self.cfg.alteruser, self.cfg.alterpassword)
                    free, used, total, used_percent = await nex2.GetSpace()
                    if free >= file_size:
                        resp = asyncio.create_task(
                            nex2.upload_file(file_path, timeout))
                        resp = await resp
                        await msg.edit(self.uploaded_msg.format(str(file_name), str(humanize.naturalsize(file_size)), f"OK Alter \n {resp}"))
                    else:
                        await msg.edit("None of your cloud accounts have space, please delete some files and retry...")

        except Exception as e:
            await msg.edit(self.uploaded_msg.format(str(file_name), str(humanize.naturalsize(file_size)), f"{str(traceback.format_exc())}"))
            print(traceback.format_exc(), 'Error en el upload')

    # Server Section...
    async def hello(self, request):
        html = """
    <head>
    <title>CLOUDBOT</title>
    <meta charset="UTF-8">
    </head>
    <body>
    </body>
        """
        return web.Response(text=html, content_type="text/html")

    async def web_server(self):
        web_app = web.Application(logger=None)
        web_app.add_routes(self.routes)
        return web_app

    async def create_server(self, route, file_path=None):
        await self.semaphore.acquire()
        global web_host
        app = web.AppRunner(await self.web_server())
        await app.setup()
        web_host = web.TCPSite(app, "0.0.0.0", int(os.getenv("PORT", 8000)))
        return web_host

    async def start_server(self):
        print("------------------- Initalizing Web Server -------------------")
        server = await self.create_server("/")
        await server.start()
        print("----------------------- Service Started -----------------------")
        URL = "https://{}/".format(self.app_name)
        print(URL)
        # tasks.append(loop.create_task(ping_server(URL)))
        # self.tasks.append(loop.create_task(bot.send_message(1028272649, "Bot Runing!.")))
        # await asyncio.gather(*self.tasks)

    # END Server Section...

    def run(self):
        loop = asyncio.get_event_loop()
        if self.time == 0:
            self.time = datetime.datetime.now()
        self.tasks.append(loop.create_task(self.start_server()))
        asyncio.gather(*self.tasks)
        self.client.run()


if __name__ == '__main__':
    bot = Bot()
    bot.run()
