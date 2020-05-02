import pandas as pd, operator
from yojirei_bot import drive_file

csvfile = 'yojirei.csv'

#例外一覧
class yojireiDupricateError(Exception):
  #既に登録されている用字例を追加しようとしたときに発生する例外
  pass

#CSVファイルに用字例を追加する関数
def add_yojirei(index, yojirei, tip):
  #ドライブからCSVファイルをダウンロード
  drive_file.dl_csv()
  
  try:
    #文字コード"utf_8_sig"でCSVファイルを読み込み
    csvdata = pd.read_csv(csvfile, sep = ',', header = 0, index_col = 0, encoding = 'utf_8_sig')
  except UnicodeDecodeError:
    #文字コードエラーを吐いたら文字コード"shift-jis"でCSVファイルを読み込み(外部からCSVファイルを編集された場合の対策)
    csvdata = pd.read_csv(csvfile, sep = ',', header = 0, index_col = 0, encoding = 'shift-jis')
  
  try:
    #用字例を検索
    csvdata.at[index, '用字例']
  except KeyError:
    #指定された語句がCSVファイルに存在しなかったら追加してアップロード
    csvdata.loc[index] = [yojirei, tip]
    csvdata_sorted = csvdata.sort_index()
    csvdata_sorted.to_csv(csvfile, encoding = 'utf_8_sig')
    drive_file.ul_csv()
  else:
    #ここまでプログラムが進んだら用字例がCSVファイルに存在したということなので、エラー
    raise yojireiDupricateError

#CSVファイルから用字例を削除する関数
def remove_yojirei(index):
  #ドライブからCSVファイルをダウンロード
  drive_file.dl_csv()

  try:
    #文字コード"utf_8_sig"でCSVファイルを読み込み
    csvdata = pd.read_csv(csvfile, sep = ',', header = 0, index_col = 0, encoding = 'utf_8_sig')
  except UnicodeDecodeError:
    #文字コードエラーを吐いたら文字コード"shift-jis"でCSVファイルを読み込み(外部からCSVファイルを編集された場合の対策)
    csvdata = pd.read_csv(csvfile, sep = ',', header = 0, index_col = 0, encoding = 'shift-jis')
  
  try:
    #用字例を検索して削除
    csvdata_removed = csvdata.drop(index)
  except KeyError:
    #指定された語句がCSVファイルに存在しなかったらエラー
    raise
  else:
    #ここまでプログラムが進んだら用字例を削除できたということなので、アップロード
    csvdata_removed.to_csv(csvfile, encoding = 'utf_8_sig')
    drive_file.ul_csv()

#CSVファイルに存在する用字例を更新する関数
def update_yojirei(index, yojirei, tip):
  #ドライブからCSVファイルをダウンロード
  drive_file.dl_csv()

  try:
    #文字コード"utf_8_sig"でCSVファイルを読み込み
    csvdata = pd.read_csv(csvfile, sep = ',', header = 0, index_col = 0, encoding = 'utf_8_sig')
  except UnicodeDecodeError:
    #文字コードエラーを吐いたら文字コード"shift-jis"でCSVファイルを読み込み(外部からCSVファイルを編集された場合の対策)
    csvdata = pd.read_csv(csvfile, sep = ',', header = 0, index_col = 0, encoding = 'shift-jis')
  
  try:
    #用字例を検索
    csvdata.at[index, '用字例']
  except KeyError:
    #指定された語句がCSVファイルに存在しなかったらエラー
    raise
  else:
    #指定された語句がCSVファイルに存在したらCSVを編集、アップロード
    csvdata.loc[index] = [yojirei, tip]
    csvdata.to_csv(csvfile, encoding = 'utf_8_sig')
    drive_file.ul_csv()

#CSVファイルをソートする関数(外部から編集したときに、気分的にソートしたければこれを使う)
def sort_yojirei():
  #ドライブからCSVファイルをダウンロード
  drive_file.dl_csv()

  try:
    #文字コード"utf_8_sig"でCSVファイルを読み込み
    csvdata = pd.read_csv(csvfile, sep = ',', header = 0, index_col = 0, encoding = 'utf_8_sig')
  except UnicodeDecodeError:
    #文字コードエラーを吐いたら文字コード"shift-jis"でCSVファイルを読み込み(外部からCSVファイルを編集された場合の対策)
    csvdata = pd.read_csv(csvfile, sep = ',', header = 0, index_col = 0, encoding = 'shift-jis')

  #CSVファイルをソートしてアップロード
  csvdata_sorted = csvdata.sort_index()
  csvdata_sorted.to_csv(csvfile, encoding = 'utf_8_sig')
  drive_file.ul_csv()

#CSVファイルから用字例を検索する関数
def search_yojirei(index):
  #ドライブからCSVファイルをダウンロード
  drive_file.dl_csv()

  try:
    #文字コード"utf_8_sig"でCSVファイルを読み込み
    csvdata = pd.read_csv(csvfile, sep = ',', header = 0, index_col = 0, encoding = 'utf_8_sig')
  except UnicodeDecodeError:
    #文字コードエラーを吐いたら文字コード"shift-jis"でCSVファイルを読み込み(外部からCSVファイルを編集された場合の対策)
    csvdata = pd.read_csv(csvfile, sep = ',', header = 0, index_col = 0, encoding = 'shift-jis')

  try:
    #用字例を検索
    return csvdata.at[index, '用字例'], csvdata.at[index, '解説/備考']
  except KeyError:
    #指定された語句がCSVファイルに存在しなかったらエラー
    raise
