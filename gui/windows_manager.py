from .gui_analyser import GUI_Analyser
from pandastable import Table, TableModel
from tkinter import messagebox, ttk
import tkinter as tk


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
