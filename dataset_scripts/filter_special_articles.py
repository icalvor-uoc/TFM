import os
import shutil

SOURCE_LOG =os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\fetch\\raw_flat.txt'
DEST_LOG = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\fetch\\regular_raw_articles.txt'
SOURCE_DIR = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\fetch\\raw_flat\\'
DEST_DIR = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\fetch\\regular_raw_articles\\'

with open(SOURCE_LOG, 'r', encoding='utf-8') as f:
  with open(DEST_LOG, 'a', encoding='utf-8') as g:
    for line in f.readlines():
      if line.find('~') == -1:
        try:
          shutil.copy(SOURCE_DIR+line[6:-1], DEST_DIR+line[6:-1])
        except Exception as e:
          print(e)
          continue
        g.write(line[6:])
#        print(line[6:-1])
