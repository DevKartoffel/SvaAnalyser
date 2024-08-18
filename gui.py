from analyser.analyser import Analyser
from analyser.nutmegs import Nutmeg
from analyser.flyover import Flyover
from pandastable import Table, TableModel

from tkinter import messagebox, ttk
import tkinter as tk


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
            nutmegs = resp.json()
            excel_path = '{}Statistik_{}.xlsx'.format(self.settings['excel_path_folder'], selectedSeason['name'].replace('/','-') )
            self.currentData['nutmegs'] = Nutmeg(nutmegs, excel_path)
            self.logger.info('Tunner geladen')
        else:
            self.logger.error('Konnte Tunner nicht laden')
        
        resp = self.sva_requ.get_fylovers(filter)
        if resp.status_code == 200:
            nutmegs = resp.json()
            excel_path = '{}Statistik_{}.xlsx'.format(self.settings['excel_path_folder'], selectedSeason['name'].replace('/','-') )
            self.currentData['flyover'] = Flyover(nutmegs, excel_path)
            self.logger.info('Zaunschüsse geladen')
        else:
            self.logger.error('Zaunschüsse nicht laden')

        return False

    def analyse_selection(self):
        self.logger.info('Starte Analyse')
        self.currentData['flyover'].analyse(team=self.team)
        self.currentData['nutmegs'].analyse(team=self.team)
        self.logger.info('Analyse beendet. Schaue in Excel Liste und die Plots.')


class WinowManager():

    class Logger():

        class Log():

            def __init__(self, text, color) -> None:
                self.text = text
                self.color = color

        INFO_COLOR = 'black', 
        WARNING_COLOR = 'yellow',
        ERROR_COLOR = 'red'
        
        def __init__ (self, root:tk):
            self.logs = []
            self.logLabel = tk.Label(root, text="Starte app", bd=2)
            self.logLabel.pack(side='bottom', fill='x')

        def __add_log__(self, log:Log):
            self.logs.append(log)
            self.logLabel.config(text=log.text, fg=log.color)

        
        def info(self, text:str):
            log = self.Log(text, self.INFO_COLOR)
            self.__add_log__(log)
        
        def warning(self, text:str):
            log = self.Log(text, self.WARNING_COLOR)
            self.__add_log__(log)
            

        def error(self, text:str):
            log = self.Log(text, self.ERROR_COLOR)
            self.__add_log__(log)
        

        

    def __init__(self):
        self.root = tk.Tk()
        
        self.logger = self.Logger(self.root)
        self.root.minsize(width=800, height=400)
        self.root.title("SVA Analyser")
        
        self.table = None
        self.analyser = None

        self.topBar = tk.Frame(self.root, bd=2, height=84)
        self.topBar.pack(side='top', fill='x')
        self.dataArea = tk.Frame(self.root)
        self.dataArea.pack(side='top', fill='both', expand=1)

        self.dropdown = ttk.Combobox(
            master= self.topBar,
            state="readonly",
            values=[]
        )
        self.dropdown.grid(column=0, row=0)

        self.dataDropdownValue = tk.StringVar()
        self.dataDropdownValue.trace_add('write', self.set_table_frame)
        self.dataDropdown = ttk.Combobox(
            master= self.topBar,
            state="readonly",
            values=list(GUI_Analyser.DF_OPTIONS.values()),
            textvariable=self.dataDropdownValue
        )
        
        self.create_analyser()

        button = ttk.Button(master=self.topBar, text="Lade Daten", command=self.load_data)
        button.grid(column=1, row=0)
        
        self.analyseButton = ttk.Button(master=self.topBar, text="Analysiere geladene Daten", command=self.start_analyser)

        self.root.mainloop()
    
    def load_data(self):
        self.logger.info('Suchen Date für ' + self.dropdown.get())
        self.analyser.download_data(self.dropdown.get())
        self.dataDropdown.grid(column=3, row=0)
        if self.dataDropdownValue.get() == None or self.dataDropdownValue.get() == '':
            self.dataDropdown.current(1)
        self.analyseButton.grid(column=4, row=0)
        
        
    def set_table_frame(self, var, index, mode):
        selectedDataframeKey = self.analyser._df_options_swaped_()[self.dataDropdown.get()]
        df = self.analyser.currentData[selectedDataframeKey].df
        self.table = Table(self.dataArea, dataframe=df, showtoolbar=True, showstatusbar=True)
        self.table.show()
    

    def start_analyser(self):
        self.analyser.analyse_selection()

    
    def create_analyser(self):
        self.analyser = GUI_Analyser(self.logger)
        seasons = self.analyser.get_seasons()
        seasonsReversed = seasons[::-1]
        seasonsReversed.append('Alle')
        
        self.dropdown['values'] = seasonsReversed
        self.dropdown.current(0)


if __name__ == "__main__":
    w = WinowManager()
