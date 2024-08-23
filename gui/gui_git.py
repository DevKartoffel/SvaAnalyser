from tkinter import messagebox, ttk
import tkinter as tk
from git import Repo
import re
import subprocess
import sys


class GitGUI():

    def __init__(self, updateButton:tk.Button) -> None:
        self.__repo = Repo()
        self.masterButton = updateButton
        self.masterButton.config(command=self.open_popup)
        self.status = {
            'textOrigin': self.__repo.git.status()
            }
        self.analyse_status()
    
    def set_update_btn_text(self):
        self.masterButton.config(text=("({}|{}) Updates".format(self.status['behind'], self.status['ahead'])))
    
    
    def analyse_status(self):
        text = self.status['textOrigin']
        match = re.search(r'branch is up to date', text)
        # No updates
        if match:
            self.status.update({'behind': '0'})
            self.status.update({'ahead': '0'})
            self.status.update({'updateAvailable': False})
            self.set_update_btn_text()
            return True

        # Behind
        match = re.search(r'behind.*by\s(\d+)\scommit', text)
        if match:
            self.status.update({'behind': match.group(1)})
            self.status.update({'ahead': '0'})
            self.status.update({'updateAvailable': True})
            self.set_update_btn_text()
            return True
        
        # Ahead
        match = re.search(r'ahead.*by\s(\d+)\scommit', text)
        if match:
            self.status.update({'behind': '0'})
            self.status.update({'ahead': match.group(1)})
            self.status.update({'updateAvailable': True})
            self.set_update_btn_text()
            return True
        
        # Ahead and front
        match = re.search(r'have\s(\d+)\sand\s(\d+)\sdifferent\scommit', text)
        if match:
            self.status.update({'behind': match.group(2)})
            self.status.update({'ahead': match.group(1)})
            self.status.update({'updateAvailable': True})
            self.set_update_btn_text()
            return True
        
        self.status.update({'behind': '?'})
        self.status.update({'ahead': '?'})
        self.status.update({'updateAvailable': False})
        self.set_update_btn_text()
        return False


    def install_packages(self):
        resp = subprocess.run(["pip", "install", "-r", "requirements.txt"])
        print(str(resp))
        
    
    def open_popup(self):

        self.popup = tk.Toplevel()
        self.popup.wm_title('Git Updater')
        self.popup.minsize(width=100, height=200)
        self.popup.iconphoto(False, tk.PhotoImage(file='assets/logo.png'))
        self.popup.title("SVA Analyser")
        self.statusText = tk.Text(self.popup)
        self.statusText.pack(expand=1)
        
        self.commandBar = tk.Frame(self.popup, bd=2, height=84)
        self.commandBar.pack(side='bottom', fill='x')
        self.statusButton = tk.Button(self.commandBar, text="Check status", command=self._set_status_text_)
        self.statusButton.grid(column=0, row=0)
        self.updateButton = tk.Button(self.commandBar, text="Update(s) herunterladen", command=self._pull_)
        self.updateButton.grid(column=1, row=0)
        self._set_status_text_()
    
    def _pull_(self):
        self.__repo.git.restore('.')
        self.__repo.git.clean('-df')
        self.__repo.remotes.origin.pull()
        self.install_packages()
        self._set_status_text_()


    def _set_status_text_(self):
        self.__repo.remotes.origin.fetch()
        text = self.__repo.git.status()
        self.status['textOrigin'] = text
        self.statusText.delete("1.0", "end")
        self.statusText.insert(tk.END, text)
        self.analyse_status()
        if self.status['updateAvailable'] and int(self.status['behind']) > 0 :
            self.updateButton.config(state='active')
        else:
            self.updateButton.config(state='disabled')
        