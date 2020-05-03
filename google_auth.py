import os

from oauth2client import client
import oauth2client.clientsecrets as clientsecrets
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def load_client_config(gauth, client_config):
    client_type, client_info = clientsecrets.loads(client_config)

    config_index = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
    for config in config_index:
        gauth.client_config[config] = client_info[config]

    gauth.client_config['revoke_uri'] = client_info.get('revoke_uri')
    gauth.client_config['redirect_uri'] = client_info['redirect_uris'][0]

    service_auth_config = ['client_email']
    try:
      for config in service_auth_config:
        gauth.client_config[config] = client_info[config]
    except KeyError:
      pass

# Google Driveの認証
gauth = GoogleAuth()
try:
    content1 = os.environ['GOOGLE_CLIENT_CONFIG']
    content2 = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
    load_client_config(gauth, content1)
    credentials = client.Credentials.new_from_json(content2)
    gauth.credentials = credentials
except KeyError:
    gauth.CommandLineAuth()

drive = GoogleDrive(gauth)
