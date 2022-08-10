import graphlib
from telnetlib import RSP
from tkinter.font import names
from .sva_requests import SvaRequests
import pandas as pd
import os
import json
from dotenv import load_dotenv



class Analyser():
    excel_delimiter = ';'

    def __init__(self) -> None:

        # Read settings
        with open('./settings.json', 'r') as f:
            data = json.load(f)
            base_url = data['base_url']

        load_dotenv()
        mail = os.getenv('EMAIL')
        pw = os.getenv('PW')

        self.sva_requ = SvaRequests(mail, pw, base_url)

        if not os.path.exists('./csv'):
            os.mkdir('./csv')

        self.sva_requ.get_token()
        
    def run(self):
        if self.sva_requ.token:
            print('Analys flyover')
            self.analyse_flyover()

            print('Analys nutmegs')
            self.analyse_netmeg()
        else:
            print('Token is missing')
        
    
    def analyse_flyover(self):
        resp = self.sva_requ.get_fylovers('')

        if resp.status_code == 200:

            df = pd.json_normalize(resp.json()).drop(columns=['season.picture', 'striker.member.date_of_birth',  'striker.member.picture', 'striker_name', 'striker.member.is_active', 'striker.member.seasons', 'striker.name', 'striker.id'])
            df['striker.member.full_name'] = df['striker.member.name'] + ' ' + df['striker.member.surename']
            df.to_csv('./csv/zaun_all.csv', sep=self.excel_delimiter)

            # group or filter?

            # vc = df['striker.member.id'].value_counts()
            # print(vc)

            # for (label, value) in df['striker.member.id'].unique.iteritems():
            #     # info to striker
            #     data = df['striker.member.id'] == label

            # Analys by groups
            grp = df.groupby(['striker.member.full_name'], as_index=False)
            simple_data = grp['striker.member.full_name'].value_counts().sort_values('count', ascending=False)
            simple_data.to_csv('./csv/simple_zaunkoenig.csv', index=False, header=['Name', 'Zaunschüsse'], sep=self.excel_delimiter)

            return True

        return False
        
    
    def analyse_netmeg(self):
        resp = self.sva_requ.get_nutmegs('')

        if resp.status_code == 200:

            # Store Data
            df = pd.json_normalize(resp.json()).drop(
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

            # write final csvs
            striker.to_csv('./csv/simple_tunnelkoenig.csv', index=False, header=['Name', 'Tunnler'], sep=self.excel_delimiter)
            victoms.to_csv('./csv/simple_elbtunnel.csv', index=False, header=['Name', 'Tunnler'], sep=self.excel_delimiter)

            return True

        return True


