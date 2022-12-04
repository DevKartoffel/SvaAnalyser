from .sva_requests import SvaRequests
from .utils import get_saved_data
import pandas as pd
import os
import json
from dotenv import load_dotenv




class Analyser():
    excel_delimiter = ';'

    def __init__(self) -> None:

        # Initialize test
        self.test = False

        # Read settings
        with open('./settings.json', 'r') as f:
            data = json.load(f)
            base_url = data['base_url']
        
        # Overw
        if os.path.exists('./local_settings.json'):
            with open('./local_settings.json', 'r') as f:
                data = json.load(f)
                base_url = data['base_url']
                if data['test']:
                    self.test = True
                    self.local_nutmeg_data_dir = data['local_nutmeg_data']
                    self.local_flyover_data_dir = data['local_flyover_data']
                    

        load_dotenv()
        mail = os.getenv('EMAIL')
        pw = os.getenv('PW')

        self.sva_requ = SvaRequests(mail, pw, base_url)

        if not os.path.exists('./csv'):
            os.mkdir('./csv')

        if not self.test:
            self.sva_requ.get_token()
        
    def run(self):

        # Alayse by local data 
        if self.test:
            data = get_saved_data(self.local_nutmeg_data_dir)
            self.analyse_nutmeg(data)

        # Alayse by requested data 
        elif self.sva_requ.token:
            print('Analys flyover')
            resp = self.sva_requ.get_fylovers('')
            if resp.status_code == 200:
                self.analyse_flyover(resp.json())

            print('Analys nutmegs')
            resp = self.sva_requ.get_nutmegs('')
            if resp.status_code == 200:
                self.analyse_nutmeg(resp.json())
        else:
            print('Token is missing')
        
    
    def analyse_flyover(self, data):
        """
        data: dict or list[dict]
        """

        df = pd.json_normalize(data).drop(columns=['season.picture', 'striker.member.date_of_birth',  'striker.member.picture', 'striker_name', 'striker.member.is_active', 'striker.member.seasons', 'striker.name', 'striker.id'])
        df['striker.member.full_name'] = df['striker.member.name'] + ' ' + df['striker.member.surename']
        df.to_csv('./csv/zaun_all.csv', sep=self.excel_delimiter)

        # Analys by groups
        grp = df.groupby(['striker.member.full_name'], as_index=False)
        simple_data = grp['striker.member.full_name'].value_counts().sort_values('count', ascending=False)
        simple_data.to_csv('./csv/simple_zaunkoenig.csv', index=False, header=['Name', 'Zaunschüsse'], sep=self.excel_delimiter)

        return True
        
    
    def analyse_nutmeg(self, data):
        """
        data: 
        """
        # Store Data
        df = pd.json_normalize(data).drop(
            columns=[
                'season.picture', 'striker.member.date_of_birth',  'striker.member.picture', 'striker_name', 'striker.member.is_active', 'striker.member.seasons', 'striker.name', 'striker.id',
                'victom.member.date_of_birth',  'victom.member.picture', 'victom_name', 'victom.member.is_active', 'victom.member.seasons', 'victom.name', 'victom.id'
                ]
            )
        df['striker.full_name'] = df['striker.member.name'] + ' ' + df['striker.member.surename']
        df['victom.full_name'] = df['victom.member.name'] + ' ' + df['victom.member.surename']
        
        # Write data to csv
        df.to_csv('./csv/tunnler_all.csv')

        # grup data 
        striker = df.groupby(['striker.full_name'], as_index=False)['striker.full_name'].value_counts().sort_values('count', ascending=False)
        victoms = df.groupby(['victom.full_name'], as_index=False)['victom.full_name'].value_counts().sort_values('count', ascending=False)
        crosstab = pd.crosstab(index=df['striker.full_name'],columns=df['victom.full_name'], margins=True, margins_name='Summe') # cross tabele

        # write final csvs
        striker.to_csv('./csv/simple_tunnelkoenig.csv', index=False, header=['Name', 'Tunnler'], sep=self.excel_delimiter)
        victoms.to_csv('./csv/simple_elbtunnel.csv', index=False, header=['Name', 'Tunnler'], sep=self.excel_delimiter)
        crosstab.to_csv('./csv/tunnler_kreuztabelle.csv',index_label="Verteiler", sep=self.excel_delimiter)

        

        return True

    def save_json_data(self):
        if self.sva_requ.token == None:
            self.sva_requ.get_token()


        print('Analys flyover')
        resp = self.sva_requ.get_fylovers('')
        if resp.status_code == 200:
            data = resp.json()
            # write data 
            with open('./test_data/zaun_all.json', 'w') as f:
                f.write(json.dumps(data))
                f.close()

        print('Analys nutmegs')
        resp = self.sva_requ.get_nutmegs('')
        if resp.status_code == 200:
            data = resp.json()
            # write data 
            with open('./test_data/tunnler_all.json', 'w') as f:
                f.write(json.dumps(data))
                f.close()



    