import os

from oauth2client import client
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Google Driveの認証
gauth = GoogleAuth()
try:
    content = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
    credentials = client.Credentials.new_from_json(content)
    gauth.credentials = credentials
except KeyError:
    gauth.CommandLineAuth()

drive = GoogleDrive(gauth)
