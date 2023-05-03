import os
import humanize
import asyncio

async def bulk_d():
    files = search_files()
    texto = ""
    tareas = []
    for file in files:
        texto += f"[{file}] [{humanize.naturalsize(os.stat('./downloads/{file}')).st_size}] [{}]\n"
    
    msg = await client.send_message(event.chat.id, texto)
    
    while True:
        if len(tareas) == 0:
            break
        
        
async def download_with_aria2c(url, ruta_destino):
    # Ejecutar el comando de Aria2c en segundo plano
    process = await asyncio.create_subprocess_exec("aria2c", url, "-d", ruta_destino)

    # Esperar a que el proceso termine
    await process.wait()
        
    
    