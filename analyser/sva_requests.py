from typing import Any
import requests

class SvaRequests():

    def __init__(self, email:str, password:str, base_url:str) -> None:
        self.email = email
        self.password = password
        self.base_url = base_url

    def get_token(self) -> Any:
        endpoint = 'accounts/apis/login/'
        data = {
            'username': self.email,
            'password': self.password
        }
        resp = requests.post(url=self.base_url + endpoint, data=data )

        if resp.status_code == 200:
            self.token = resp.json().get('token')
            return resp.json
        
        return resp.json
    

    def get_fylovers(self, filter:str) -> Any:
        endpoint = 'sva/apis/flyovers/'
        header = {
            'Authorization': 'Token ' + self.token
        }
        resp = requests.get(url=self.base_url + endpoint, headers=header)

        return resp.json()

    def get_nutmegs(self, filter:str) -> Any:
        endpoint = 'sva/apis/nutmegs/'
        header = {
            'Authorization': 'Token ' + self.token
        }
        resp = requests.get(url=self.base_url + endpoint, headers=header)

        return resp.json()