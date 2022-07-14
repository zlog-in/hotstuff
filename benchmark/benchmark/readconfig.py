import json

class readconfig:
    def __init__(self) -> None:
         with open('config.json') as f:
                config = json.load(f)
         replicas = config['replicas']
         servers = config['servers']
         local = config['local'] 
         duration = config['duration']   
         rate = config['input_rate']
    
        