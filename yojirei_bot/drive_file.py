from google_auth import drive

#"共有フォルダ/09.その他"のフォルダID(URLの末端文字列)
folder_id = '0B6UTBGc4fcPNLTFKYkp6U3I1VWc'
#ListFileメソッドでファイル種別を指定するための工夫。"folder_id"で指定したフォルダ内かつ、削除されていないファイルのみを抽出する
query = "'{}' in parents and trashed=false".format(folder_id)

#settings.yamlの設定によって、このAPIからアップロードしたファイルしか読み書きできないので、最初にyojirei.csvをアップロードしたときの名残
#f = drive.CreateFile({'title': 'yojirei.csv', 'mimeType': 'text/csv', 'parents': [{'kind': 'drive#fileLink', 'id':folder_id}]})

#yojirei.csvのダウンロードをする関数
def dl_csv():
  file_list = drive.ListFile({'q': query}).GetList()
  for target_file in file_list:
    if target_file['title'] == 'yojirei.csv':
      f = target_file
  f.GetContentFile('yojirei.csv')

#yojirei.csvのアップロードをする関数
def ul_csv():
  file_list = drive.ListFile({'q': query}).GetList()
  for target_file in file_list:
    if target_file['title'] == 'yojirei.csv':
      f = target_file
  f.SetContentFile('yojirei.csv')
  f.Upload()