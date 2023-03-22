import os
import time
import zipfile
import multiFile
import asyncio
import traceback
import humanize

from NextCloudClient import NexCloudClient
from config import Config
from zipfile import ZipFile
from pyrogram import Client, filters
from aiohttp import web

class Bot():
    def __init__(self):
        self.cfg = Config()
        self.bot_token = self.cfg.bot_token
        self.api_id = self.cfg.api_id
        self.api_hash = self.cfg.api_hash
        self.client = Client('bot',bot_token = self.bot_token, api_id=self.api_id, api_hash=self.api_hash)
        self.chat_id = 0
        self.tasks = []
        self.semaphore = asyncio.Semaphore(2)
        self.speed = 0.0
        self.progress = 0
        self.download_msg = "#download\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]" #Name Size Percent/Elapsed
        self.compress_msg = "#compress\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]" #Name Size Percent
        self.upload_msg = "#upload\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]" #Name Size Result
        self.uploaded_msg = "#uploaded\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]" #Name Size Status
        self.upload_msg_error = "#uploaded\n[<b>{}</b>] [<b>{}</b>] [<b>{}</b>]\n<b>[{}]</b>"
        self.app_name = "lasthope"
        self.ExcludeFiles = ['ProxyCloud.py','NextCloudClient.py','bot.py','mediafire_dl.py','multiFile.py',
                'Client.py','requirements.txt','Procfile','__pycache__','.git','.profile.d',
                '.heroku','bot.session','bot.session-journal','output','Actualizar heroku.bat',
                'runtime.txt','config.py','.env', 'README.md','.gitignore', 'config.json','downloads','utils']
        self.routes = [web.get("/", self.hello)]
        self.web_host = None

        @self.client.on_message(filters.all & filters.private)
        async def Handler(client, event):
            #print(event)
            if self.chat_id == 0:
                self.chat_id = event.chat.id
                
            if event.document != None:
                msg = await client.send_message(self.chat_id, self.download_msg.format(event.document.file_name,humanize.naturalsize(event.document.file_size),"-"), reply_to_message_id = event.id)
                # Creamos una tarea para descargar el archivo
                task_document = asyncio.create_task(self.DownloadFile(event.document.file_name, event.document.file_size, msg, client, event, "document"))
                # Añadimos la tarea a la lista
                self.tasks.append(task_document)
                   
            elif event.video != None:
                msg = await client.send_message(self.chat_id, self.download_msg.format(event.video.file_name,humanize.naturalsize(event.video.file_size),"-"), reply_to_message_id = event.id)
                # Creamos una tarea para descargar el archivo
                task_video = asyncio.create_task(self.DownloadFile(event.video.file_name, event.video.file_size, msg, client, event, "media"))
                # Añadimos la tarea a la lista
                self.tasks.append(task_video)
    ### Modelo de descargas...   
    async def DownloadFile(self,file_name, file_size, msg, client, event, type):
        # Esperamos a que haya disponibilidad en el Semaphore
        await self.semaphore.acquire()
        try:
            start_time =  time.process_time()
            if type == "document":
                recv_data = await client.download_media(event.document,progress = self.progress_bar, progress_args = (file_name, file_size, msg))
            elif type == "media":
                recv_data = await client.download_media(event.video,progress = self.progress_bar, progress_args = (file_name, file_size, msg))
            self.tasks.remove(asyncio.current_task())
            finished_time = time.process_time()
            await msg.edit(self.download_msg.format(file_name, humanize.naturalsize(file_size), humanize.naturaldelta(finished_time-start_time)))
            await self.ProcessUpload(file_name, file_size, msg)
        except:
            traceback.print_exc()
        finally:
            # Liberamos el Semaphore
            
            self.semaphore.release()
            
    async def progress_bar(self,current, total, file_name, file_size, msg):
        # Función callback para mostrar el progreso de la descarga
        percent = current * 100 / total
        #print(f"Progress: {current}/{total} Speed: {humanize.naturalsize(speed)} ")
        await msg.edit(self.download_msg.format(file_name,humanize.naturalsize(file_size),(str(round(percent)))+" %"))

    ### Modelo de subidas...
    async def ProcessUpload(self, file_name, file_size, msg):
        await self.semaphore.acquire()
        try:
            #chunk_size = self.cfg.zip_size
            chunk_size = 1024 * 1024 * self.cfg.zip_size
            if file_size > chunk_size:
                file_path = f"./downloads/{file_name}"
                await msg.edit(self.compress_msg.format(str(file_name), str(humanize.naturalsize(file_size)),len(multiFile.files) + 1 if(len(multiFile.files))==0 else len(multiFile.files)))
                mult_file =  multiFile.MultiFile(file_path+'.7z',chunk_size)
                zip = ZipFile(mult_file,  mode='w', compression=zipfile.ZIP_DEFLATED)
                zip.write(file_path)
                zip.close()
                mult_file.close()
                os.unlink(file_path)
                for file in multiFile.files:
                    await msg.edit(self.upload_msg.format(str(file_name), str(humanize.naturalsize(file_size)), len(multiFile.files) + 1 if(len(multiFile.files))==0 else len(multiFile.files)))
                    nex = NexCloudClient(self.cfg.user,self.cfg.password)
                    print(file)
                    resp = asyncio.create_task(nex.upload_file(file))
                    resp = await resp
                    #print(resp)
                    #data=data+'\n\n'+str(resp).replace('\\','')
                await msg.edit(self.uploaded_msg.format(str(file_name), str(humanize.naturalsize(file_size)), "OK"))
            else:
                await msg.edit(self.upload_msg.format(str(file_name), str(humanize.naturalsize(file_size)),"Subiendo"))
                nex = NexCloudClient(self.cfg.user,self.cfg.password)
                resp = asyncio.create_task(nex.upload_file(f"./downloads/{file_name}"))    
                resp = await resp
                await msg.edit(self.uploaded_msg.format(str(file_name), str(humanize.naturalsize(file_size)), "OK"))
                
        except Exception as e:
                await msg.edit(self.uploaded_msg.format(str(file_name), str(humanize.naturalsize(file_size)), "ERROR"))
                print(traceback.format_exc(),'Error en el upload')


    async def hello(request):
        html = """
    <head>
    <title>CLOUDBOT</title>
    <meta charset="UTF-8">
    </head>
    <body>
    </body>
        """
        return web.Response(text=html, content_type="text/html")


    #######VARIABLES TEMP#######
    
    ############################


    async def web_server(self):
        web_app = web.Application(logger=None)
        web_app.add_routes(self.routes)
        return web_app


    async def create_server(self,route, file_path=None):
        await self.semaphore.acquire()
        global web_host
        app = web.AppRunner(await self.web_server())
        await app.setup()
        web_host = web.TCPSite(app, "0.0.0.0", int(os.getenv("PORT", 8000)))
        return web_host

    async def start_server(self,bot, loop):
        print("------------------- Initalizing Web Server -------------------")
        server = await self.create_server("/")
        await server.start()
        print("----------------------- Service Started -----------------------")
        URL = "https://{}/".format(self.app_name)
        print(URL)
        #tasks.append(loop.create_task(ping_server(URL)))
        self.tasks.append(loop.create_task(bot.send_message(1028272649, "Bot Runing!.")))
        await asyncio.gather(*self.tasks)
    
    def run(self):
        print("Staring server")
        loop = asyncio.get_event_loop()
        self.tasks.append(loop.create_task(self.start_server(self.client,loop)))
        print("Server Started")
        self.client.run()
        
if __name__ == '__main__':
    bot = Bot()
    
    bot.run()
    

