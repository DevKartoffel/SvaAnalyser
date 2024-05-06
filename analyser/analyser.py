from .sva_requests import SvaRequests
from .flyover import Flyover
from .nutmegs import Nutmeg
from .utils import get_saved_data
import pandas as pd
import matplotlib.pyplot as plt
import os
import json
from dotenv import load_dotenv
import locale
from datetime import date


class Analyser():
    excel_delimiter = ';'
    
    def __init__(self) -> None:
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF8')

        # Initialize test
        self.test = False

        # Read settings
        with open('./settings.json', 'r') as f:
            data = json.load(f)
            base_url = data['base_url']
            self.excel_path = data['excel_path']
            self.settings = data

        
        # Overw
        if os.path.exists('./local_settings.json'):
            with open('./local_settings.json', 'r') as f:
                data = json.load(f)
                base_url = data['base_url']
                if data['test']:
                    self.test = True
                    self.local_nutmeg_data_dir = data['local_nutmeg_data']
                    self.local_flyover_data_dir = data['local_flyover_data']
                if 'excel_path' in data:
                    self.excel_path = data['excel_path']
        

        load_dotenv()
        mail = os.getenv('EMAIL')
        pw = os.getenv('PW')

        self.sva_requ = SvaRequests(mail, pw, base_url)

        if not os.path.exists('./csv'):
            os.mkdir('./csv')

        if not self.test:
            self.sva_requ.get_token()
            

    def set_current_season(self):
        resp = self.sva_requ.get_seasons()

        if resp.status_code == 200:
            seasons = resp.json()
            self.current_season = seasons[-1]

        # print(str(self.current_season))

    def run_test(self):
        # self.save_json_data()
        nutmegs = get_saved_data(self.local_nutmeg_data_dir)
        flyovers = get_saved_data(self.local_flyover_data_dir)
        season = {'id':3}
        self.flyovers = Flyover(flyovers, self.excel_path)
        self.flyovers.analyse(season)

        self.nutmegs = Nutmeg(nutmegs, self.excel_path)
        self.nutmegs.analyse(season)
        # Current All Time
        self.nutmegs.excelPath = self.settings["excel_path_all_time"]
        self.nutmegs.analyse()

        plots = self.nutmegs.get_plots() + self.flyovers.get_plots()
        self.nutmegs.subplot(plots, 'graphs')
        # self.nutmegs.test()


    def run(self):

        # Alayse by local data 
        if self.test:
            self.run_test()
        
        # Alayse by requested data 
        elif self.sva_requ.token:

            self.set_current_season()

            print('Get Team Data')
            resp = self.sva_requ.get_team()
            if resp.status_code == 200:
                team = resp.json()
            else:
                team = None
            
            print('Analys flyover')
            resp = self.sva_requ.get_fylovers('')
            flyovers = resp.json()
            if resp.status_code == 200:
                print("Analyse current season flyover data.")
                self.flyovers = Flyover(flyovers, self.excel_path)
                self.flyovers.analyse(self.current_season, team)

                print("Analyse all time flyover data.")
                self.flyovers.excelPath = self.settings["excel_path_all_time"]
                self.flyovers.analyse()

            print('Analys nutmegs')
            resp = self.sva_requ.get_nutmegs('')
            if resp.status_code == 200:
                nutmegs = resp.json()
                # Current Season
                print("Analyse current season nutmeg data.")
                self.nutmegs = Nutmeg(nutmegs, self.excel_path)
                self.nutmegs.analyse(self.current_season, team)
                # Current All Time
                print("Analyse all time nutmeg data.")
                self.nutmegs.excelPath = self.settings["excel_path_all_time"]
                self.nutmegs.analyse(team=team)
                # self.analyse_nutmeg(nutmegs, team)
            
            # Print graphs
            print("Print plots")
            plots = self.nutmegs.get_plots() + self.flyovers.get_plots()
            self.nutmegs.subplot(plots, 'graphs')
        
        else:
            print('Token is missing')
    

    def save_json_data(self):
        if self.sva_requ.token == None:
            self.sva_requ.get_token()


        print('Print flyover')
        resp = self.sva_requ.get_fylovers('')
        if resp.status_code == 200:
            data = resp.json()
            # write data 
            with open('./test_data/zaun_all.json', 'w') as f:
                f.write(json.dumps(data))
                f.close()

        print('Print nutmegs')
        resp = self.sva_requ.get_nutmegs('')
        if resp.status_code == 200:
            data = resp.json()
            # write data 
            with open('./test_data/tunnler_all.json', 'w') as f:
                f.write(json.dumps(data))
                f.close()
        
        print('Print Team')
        resp = self.sva_requ.get_team()
        if resp.status_code == 200:
            data = resp.json()
            # write data 
            with open('./test_data/team_all.json', 'w') as f:
                f.write(json.dumps(data))
                f.close()


