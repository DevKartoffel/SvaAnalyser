

from analyser.analyser import Analyser
from analyser.nutmegs import Nutmeg
from analyser.flyover import Flyover


class GUI_Analyser(Analyser):

    DF_OPTIONS = {'flyover':'Zaunschüsse', 'nutmegs': 'Tunnler'}
    
    def __init__(self, logger) -> None:
        self.currentData = {}
        self.selectedSeason = None

        self.logger = logger
        self.logger.info('Melde mich an')
        super().__init__()
        self.logger.info('Habe mich angemeldet')
        self.logger.info('Lade Saisons')
        self.request_seasons()
        self.logger.info('Habe Saisons geladen')
        self.team = self.__request_Team__()
        self.logger.info('Manschafts Daten geladen')

    def request_seasons(self):
        resp = self.sva_requ.get_seasons()

        if resp.status_code == 200:
            self.seasons = resp.json()
            self.current_season = self.seasons[-1]
            return True
        return False
    
    @staticmethod
    def _df_options_swaped_():
        return {value: key for key, value in GUI_Analyser.DF_OPTIONS.items()}


    def __request_Team__(self):
        print('Get Team Data')
        resp = self.sva_requ.get_team()
        if resp.status_code == 200:
            team = resp.json()
        else:
            team = None
        return team

    def get_seasons(self):
        if self.seasons == None:
            self.request_seasons()
        if self.seasons:
            return [s['name'] for s in self.seasons]
        self.logger.error('Habe keine Saisons finden können')
        return []
    

    def set_selected_season(self, seasonName):

        for s in self.seasons:
            if s['name'] == seasonName:
                self.selectedSeason = s
                return s
        
        self.logger.error('Saison {} nicht gefunden'.format(seasonName))
        return False
    

    def download_data(self, seasonName):
        if seasonName != 'Alle':
            selectedSeason = self.set_selected_season(seasonName)
            filter = '?season=' + str(selectedSeason['id'])
            
        resp = self.sva_requ.get_nutmegs(filter)
        if resp.status_code == 200:
            data = resp.json()
            excel_path = '{}Statistik_{}.xlsx'.format(self.settings['excel_path_folder'], selectedSeason['name'].replace('/','-') )
            self.currentData['nutmegs'] = Nutmeg(data, excel_path)
            self.logger.info('Tunner geladen')
        else:
            self.logger.error('Konnte Tunner nicht laden')
        
        resp = self.sva_requ.get_fylovers(filter)
        if resp.status_code == 200:
            data = resp.json()
            excel_path = '{}Statistik_{}.xlsx'.format(self.settings['excel_path_folder'], selectedSeason['name'].replace('/','-') )
            self.currentData['flyover'] = Flyover(data, excel_path)
            self.logger.info('Zaunschüsse geladen')
        else:
            self.logger.error('Zaunschüsse nicht laden')

        return False

    def analyse_selection(self):
        self.logger.info('Starte Analyse')
        self.currentData['flyover'].analyse(team=self.team)
        self.currentData['nutmegs'].analyse(team=self.team)
        self.logger.info('Analyse beendet. Schaue in Excel Liste und die Plots.')