import re
from enum import Enum
from yojirei_bot import yojirei_pandas

class Mode(Enum):
  SEARCH = 0
  ADD = 1
  REMOVE = 2
  UPDATE = 3
  SORT = 4

#コマンド一覧
order_add = '追加'
order_remove = '削除'
order_update = '更新'
order_sort = 'ソート'
order = [0, 0, 0, 0]

#例外一覧
class callMultiCommandsError(Exception):
  #複数コマンドを指定されたときに発生する例外
  pass
class commandSyntaxError(Exception):
  #構文の形式が不正なときに発生する例外
  pass
class yojireiDupricateError(Exception):
  #既に登録されている用字例を追加しようとしたときに発生する例外
  pass

#テキストを引数にとり、どのコマンドかを判断して返す関数
def mode_analysis(text):
  #引数のテキストに各コマンド名が含まれていたら、対応する配列位置に出現回数を記録
  order[0] = order_add in text
  order[1] = order_remove in text
  order[2] = order_update in text
  order[3] = order_sort in text

  #配列内の数値合計が1より大きい場合は、複数コマンドが含まれているためエラー
  if sum(order) > 1:
    raise callMultiCommandsError

  #コマンドによって返り値を分岐
  if order[0]:
    return Mode.ADD #追加
  elif order[1]:
    return Mode.REMOVE #削除
  elif order[2]:
    return Mode.UPDATE #更新
  elif order[3]:
    return Mode.SORT #ソート
  else:
    return Mode.SEARCH #検索

#テキスト文から、"1:"などの不要部分を省いて語句/説明のみ返す関数
def match_to_text(match_object, start, end, mode):
  #追加,更新の場合(1:"語句"のようになるため、先頭を3字、後ろを1字省く)
  if mode in {Mode.ADD, Mode.UPDATE}:
    return match_object[start + 3 : end - 1]
  #削除,検索の場合("語句"のようになるため、先頭と後ろを1字ずつ省く)
  else:
    return match_object[start + 1 : end - 1]

#テキストとコマンド値を引数にとり、リプライ文を返す関数
def execute(mode, text):
  index = None
  yojirei = None
  tip = None

  #追加,更新の場合
  if mode in {Mode.ADD, Mode.UPDATE}:
    #テキストから語句/説明が含まれる箇所を抜き出す
    index_match = re.search(r'1:"(.*?)"', text)
    yojirei_match = re.search(r'2:"(.*?)"', text)
    tip_match = re.search(r'3:"(.*?)"', text)
    
    #正しく抜き出せないときはエラー
    if index_match == yojirei_match == tip_match == None:
      raise commandSyntaxError

    #各箇所から語句/説明のみを抜き出し
    index = match_to_text(text, *index_match.span(), mode)
    yojirei = match_to_text(text, *yojirei_match.span(), mode)
    tip = match_to_text(text, *tip_match.span(), mode)

    #CSV処理にまわす
    if mode == Mode.ADD:
      try:
        yojirei_pandas.add_yojirei(index, yojirei, tip)
      except yojirei_pandas.yojireiDupricateError:
        raise yojireiDupricateError
    else:
      try:
        yojirei_pandas.update_yojirei(index, yojirei, tip)
      except KeyError:
        raise
  
  #削除の場合
  elif mode == Mode.REMOVE:
    #テキストから語句が含まれる箇所を抜き出す
    index_match = re.search(r'"(.*?)"', text)

    #正しく抜き出せないときはエラー
    if index_match == None:
      raise commandSyntaxError
    
    #語句のみを抜き出し
    index = match_to_text(text, *index_match.span(), mode)

    #CSV処理にまわす
    try:
      yojirei_pandas.remove_yojirei(index)
    except KeyError:
      raise
  
  #ソートの場合
  elif mode == Mode.SORT:
    #CSV処理にまわす
    try:
      yojirei_pandas.sort_yojirei()
    except KeyError:
      raise
  
  #検索の場合
  else:
    #テキストから語句が含まれる箇所を抜き出す
    index_match = re.search(r'"(.*?)"', text)

    #正しく抜き出せないときはエラー
    if index_match == None:
      raise commandSyntaxError
    
    #語句のみを抜き出し
    index = match_to_text(text, *index_match.span(), mode)

    #CSV処理にまわす
    try:
      yojirei, tip = yojirei_pandas.search_yojirei(index)
    except KeyError:
      raise
  
  return index, yojirei, tip