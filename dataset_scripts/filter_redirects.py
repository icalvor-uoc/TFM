import os
import shutil

SOURCE_LOG =os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\fetch\\regular_raw_articles.txt'
DEST_LOG = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\fetch\\regular_raw_articles_no_redirect.txt'
SOURCE_DIR = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\fetch\\regular_raw_articles\\'
DEST_DIR = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\fetch\\regular_raw_articles_no_redirect\\'

with open(SOURCE_LOG, 'r', encoding='utf-8') as f:
  with open(DEST_LOG, 'a', encoding='utf-8') as g:
    for line in f.readlines():
      # If not redirect
      # Copy and add to the list
      with open(SOURCE_DIR+line[:-1], 'r', encoding='utf-8') as h:
        index = h.read().find('http-equiv="Refresh"')
      if index == -1:
        try:
          shutil.copy(SOURCE_DIR+line[:-1], DEST_DIR+line[:-1])
        except Exception as e:
          print(e)
          continue
        g.write(line)
        

