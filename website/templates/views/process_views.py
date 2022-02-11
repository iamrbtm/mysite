import requests
from website import db
from website.models import *

def console_update():
    TOKEN = db.session.query(APIKeys).filter(APIKeys.name == "pythonanywhere").first().key
    API = 'https://www.pythonanywhere.com/api/v0/user/rbtm2006/'

    res = requests.get(f'{API}consoles/',
                    headers={'Authorization': f'Token {TOKEN}'})
    cnid = res.json()[0]['id']

    res = requests.post(f'{API}consoles/{cnid}/send_input/',
                    json={'input': 'cd\nbash update.sh\n'},
                    headers={'Authorization': f'Token {TOKEN}'})
    
    return res.text