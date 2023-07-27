from .sva_requests import SvaRequests
from .utils import get_saved_data
import pandas as pd
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
            

    def get_current_season(self):
        resp = self.sva_requ.get_seasions()

        if resp.status_code == 200:
            seasons = resp.json()
            self.current_season = seasons[-1]
            # today = date.today()

            # for season in seasons:
            #     if date(season['start']) > today and date(season['end']) < today:
            #         self.current_season = season

        print(str(self.current_season))

    def prepare_nugtmag_data(sef, data):
        """
            data: in json format
        """

        df = pd.json_normalize(data).drop(
        columns=[
            'season.picture', 'striker.member.date_of_birth',  'striker.member.picture', 'striker_name', 'striker.member.is_active', 'striker.member.seasons', 'striker.name', 'striker.id',
            'victom.member.date_of_birth',  'victom.member.picture', 'victom_name', 'victom.member.is_active', 'victom.member.seasons', 'victom.name', 'victom.id'
            ]
        )
        df['striker.full_name'] = df['striker.member.name'] + ' ' + df['striker.member.surename']
        df['victom.full_name'] = df['victom.member.name'] + ' ' + df['victom.member.surename']
        df['date'] = pd.to_datetime(df['date'])
        df['weekday'] = df['date'].dt.day_name(locale='de_DE.utf-8')
        return df
    
    def prepare_flyover_data(sef, data):
        """
            data: in json format
        """
        df = pd.json_normalize(data).drop(columns=['season.picture', 'striker.member.date_of_birth',  'striker.member.picture', 'striker_name', 'striker.member.is_active', 'striker.member.seasons', 'striker.name', 'striker.id'])
        df['striker.member.full_name'] = df['striker.member.name'] + ' ' + df['striker.member.surename']
        return df
        
    def run(self):

        # Alayse by local data 
        if self.test:
            nutmegs = get_saved_data(self.local_nutmeg_data_dir)
            flyovers = get_saved_data(self.local_flyover_data_dir)
            self.analyse_player('Janis Voß', nutmegs, flyovers)
        
        # Alayse by requested data 
        elif self.sva_requ.token:

            self.get_current_season()

            print('Get Team Data')
            resp = self.sva_requ.get_team()
            if resp.status_code == 200:
                team = resp.json()
                print('Analys flyover')
                resp = self.sva_requ.get_fylovers('')
                flyovers = resp.json()
                if resp.status_code == 200:
                    self.analyse_flyover(flyovers, team)

                print('Analys nutmegs')
                resp = self.sva_requ.get_nutmegs('')
                if resp.status_code == 200:
                    nutmegs = resp.json()
                    self.analyse_nutmeg(nutmegs, team)
                
                self.analyse_player('Janis Voß', nutmegs, flyovers)
            
            else:
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
        
    
    def analyse_flyover(self, data, team):
        """
        data: dict or list[dict]
        """

        df = self.prepare_flyover_data(data)

        # Filter Data
        season_id = self.current_season['id']
        df = df.loc[df['season.id'] == season_id]

        # Analys by groups
        grp = df.groupby(['striker.member.full_name'], as_index=False)
        simple_data = grp['striker.member.full_name'].value_counts().sort_values('count', ascending=False)
        simple_data.to_csv('./csv/simple_zaunkoenig.csv', index=False, header=['Name', 'Zaunschüsse'], sep=self.excel_delimiter)

        return True
        
    
    def analyse_nutmeg(self, data, team=None):
        """
        data: in json format
        """
        # Store Data
        df = self.prepare_nugtmag_data(data)

        # Filter Data
        season_id = self.current_season['id']
        df = df.loc[df['season.id'] == season_id]
        
        # Write data to csv
        df.to_csv('./csv/tunnler_all.csv')

        # gruop data 
        striker = df.groupby(['striker.full_name'], as_index=False)['striker.full_name'].value_counts().sort_values('count', ascending=False)
        victoms = df.groupby(['victom.full_name'], as_index=False)['victom.full_name'].value_counts().sort_values('count', ascending=False)
        crosstab = pd.crosstab(index=df['striker.full_name'],columns=df['victom.full_name'], margins=True, margins_name='Summe') # cross tabele
        striker_weekday = pd.crosstab(index=df['striker.full_name'],columns=df['weekday'], margins=True, margins_name='Summe')
        victom_weekday = pd.crosstab(index=df['victom.full_name'],columns=df['weekday'], margins=True, margins_name='Summe')
        
        
        if team != None:
            # TODO: Add is Player
            dfTeam = pd.json_normalize(team)

            # Delete inactive members
            dfTeam = dfTeam.drop(dfTeam[~dfTeam['is_active']].index) # TODO: drop all !players

            # create names
            dfTeam['striker.full_name'] = dfTeam['name'] + ' ' + dfTeam['surename']
            dfTeam['victom.full_name'] = dfTeam['name'] + ' ' + dfTeam['surename']
            dfTeam['count'] = 0
            # Drop rest
            dfTeam = dfTeam.drop( columns=['name', 'is_active', 'surename'])

            # Filter missin players
            missing_strikers = dfTeam[~dfTeam['striker.full_name'].isin(striker['striker.full_name'])]
            missing_victoms = dfTeam[~dfTeam['victom.full_name'].isin(victoms['victom.full_name'])]

            # Add missing players to data
            striker = pd.concat([striker, missing_strikers], ignore_index=True).drop(columns=['victom.full_name'])
            victoms = pd.concat([victoms, missing_victoms], ignore_index=True).drop(columns=['striker.full_name'])




        # print(striker_weekday.head(15))

        # write final csvs
        striker.to_csv('./csv/simple_tunnelkoenig.csv', index=False, header=['Name', 'Tunnler'], sep=self.excel_delimiter)
        victoms.to_csv('./csv/simple_elbtunnel.csv', index=False, header=['Name', 'Tunnler'], sep=self.excel_delimiter)
        crosstab.to_csv('./csv/tunnler_kreuztabelle.csv',index_label="Verteiler", sep=self.excel_delimiter)
        striker_weekday.to_csv('./csv/simple_tunnelkoenig_wochentag_verteiler.csv', index_label="Verteiler", sep=self.excel_delimiter)
        victom_weekday.to_csv('./csv/simple_tunnelkoenig_wochetntag_opfer.csv', index_label="Opfer", sep=self.excel_delimiter)

        

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


    def analyse_player(self, playerName, nutmegsData, flyoverData):
        """
            data: in json format
        """
        print('Analyse Player: ' + playerName)
        dfNutmeg = self.prepare_nugtmag_data(nutmegsData)
        dfFlyover = self.prepare_flyover_data(flyoverData)


        strikes = dfNutmeg[ dfNutmeg['striker.full_name'] == playerName]
        victom = dfNutmeg[ dfNutmeg['victom.full_name'] == playerName]
        flyovers = dfNutmeg[ dfNutmeg['striker.full_name'] == playerName]

        strikesToCombine = strikes[['date', 'weekday']]
        print(strikesToCombine)
        strikesToCombine1 = strikesToCombine.groupby(['date'], as_index=False)['date'].count()
        strikesToCombine2 = strikesToCombine.groupby(['date'], as_index=False)['weekday'].count()



        print(strikesToCombine1)
        print(strikesToCombine2)



