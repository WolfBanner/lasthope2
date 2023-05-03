import os
import asyncio

async def buscar_archivo(nombre_archivo, ruta='./'):
    # Recorrer recursivamente todos los directorios y subdirectorios
    for dirpath, dirnames, filenames in os.walk(ruta):
        # Buscar el archivo en la lista de archivos del directorio actual
        if nombre_archivo in filenames:
            # Devolver la ruta completa del archivo
            return f"{dirpath}/{nombre_archivo}"

    # Si el archivo no se encuentra en ningún directorio, devolver None
    return None

# Ejemplo de uso
#archivo_buscado = "MediaFire - Getting Started.pdf"

#ruta_archivo = asyncio.run(buscar_archivo(archivo_buscado))

#if ruta_archivo is not None:
#    print(f"El archivo {archivo_buscado} se encuentra en la ruta: {ruta_archivo}")
#else:
#    print(f"No se encontró el archivo {archivo_buscado} en ningún directorio.")