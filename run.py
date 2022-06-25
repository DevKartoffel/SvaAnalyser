from analyser.sva_requests import SvaRequests
import os

mail = os.environ.get('EMAIL')
pw = os.environ.get('PW')
base_url = os.environ.get('BASE_URL')

sva_requ = SvaRequests(mail, pw,base_url)

token_resp = sva_requ.get_token()
flyovers = sva_requ.get_fylovers('')
nutmegs =sva_requ.get_nutmegs('')

print('end')
