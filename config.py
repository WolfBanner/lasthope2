import asyncio
import json

class Config():
    def __init__(self):
        ### Dev
        self.owner = 1028272649
        self.api_id = 8261024
        self.api_hash = "9ae649018806673ef946ebf228e8625b"
        self.bot_token = "6106476283:AAEXsd3J8_PDzOKApLAE0h5nVMN7zzYxfBY"#"6106476283:AAEXsd3J8_PDzOKApLAE0h5nVMN7zzYxfBY"
        
        ### Nube
        self.zip_size = 4096
        self.user = "maralonso"
        self.password = "lorena#5"
        self.url = "https://nube.uclv.cu/"
        
        ### Mega
        self.mega_user = "yanco148@gmail.com"
        self.mega_password = "yancarlos1482005"
        
    ### Getting Configuration from JSON file.
    async def GetDevConfig():
        with open("config.json", 'r') as dev:
            dev_data = json.load(dev)
        dev.close()
        return dev_data['dev']

    async def GetNubeConfig():
        with open("config.json", 'r') as nube:
            nube_data = json.load(nube)
        nube.close()
        return nube_data['nube']

    async def GetMegaConfig():
        with open("config.json", 'r') as mega:
            mega_data = json.load(mega)
        mega.close()
        return mega_data['mega']
    
    ### Setting Configuration
    ### Not necesary