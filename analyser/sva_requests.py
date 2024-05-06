from lib2to3.pgen2 import token
from msilib.schema import Error
from typing import Any
import requests
import os

class SvaRequests():

    def __init__(self, email:str, password:str, base_url:str) -> None:
        self.email = email
        self.password = password
        self.base_url = base_url
        self.token = None

    def get_token(self) -> Any:
        print('Get Token')
        url = self.base_url + 'accounts/apis/login/'
        data = {
            'username': self.email,
            'password': self.password
        }

        try:
            resp = requests.post(url=url, data=data, timeout=10)

            if resp.status_code == 200:
                self.token = resp.json().get('token')
                os.putenv("TOKEN", self.token)
                
                return resp
            
            return resp
        except (ConnectionError, Exception) as err:
            print(err.args)
            

    def get_fylovers(self, filter:str) -> requests.Response:
        endpoint = 'sva/apis/flyovers/'
        header = {
            'Authorization': 'Token ' + self.token
        }
        resp = requests.get(url=self.base_url + endpoint, headers=header)

        return resp

    def get_nutmegs(self, filter:str) -> requests.Response:
        endpoint = 'sva/apis/nutmegs/'
        header = {
            'Authorization': 'Token ' + self.token
        }
        resp = requests.get(url=self.base_url + endpoint, headers=header)

        return resp

    def get_team(self):
        endpoint = 'sva/apis/members/'
        header = {
            'Authorization': 'Token ' + self.token
        }
        resp = requests.get(url=self.base_url + endpoint, headers=header)

        return resp

    def get_seasons(self):
        endpoint = 'sva/apis/seasons/'
        header = {
            'Authorization': 'Token ' + self.token
        }
        resp = requests.get(url=self.base_url + endpoint, headers=header)

        return resp
