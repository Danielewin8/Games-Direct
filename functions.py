from flask import session
from secret import CLIENT_ID
import requests

def get_logos():

    headers = {'Accept': 'application/json','Client-ID': CLIENT_ID, 'Authorization': 'Bearer ' + session['token']}
    response = requests.post('https://api.igdb.com/v4/platform_logos', headers=headers, data='fields image_id;').json()

    logos = {platform_logo['id']: platform_logo['image_id'] for platform_logo in response}
    return logos