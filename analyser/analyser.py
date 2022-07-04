from .sva_requests import SvaRequests
import pandas as pd
import os
import io

class Analyser():

    def __init__(self) -> None:
        mail = os.environ.get('EMAIL')
        pw = os.environ.get('PW')
        base_url = os.environ.get('BASE_URL')

        self.sva_requ = SvaRequests(mail, pw,base_url)

        self.sva_requ.get_token()
        
    def run(self):
        self.analyse_flyover()
        self.analyse_netmeg()
        pass
    
    def analyse_flyover(self):
        data = self.sva_requ.get_fylovers('')
        df = pd.json_normalize(data)
        df.to_csv('./flyover.csv')
        return True
        
    
    def analyse_netmeg(self):
        data = self.sva_requ.get_nutmegs('')
        df = pd.json_normalize(data)
        df.to_csv('./nutmegs.csv')
        return True


