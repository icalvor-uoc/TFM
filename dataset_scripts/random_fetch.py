import os
import app.fetch as fetch
import csv
import json
import uuid

def get_uuid():
  return str(uuid.uuid4())


DEST_LOG=os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\fetch\\random_articles2.txt'
DEST_DIR=os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\fetch\\random_articles2\\'


while True:
  articles = fetch.FetchModel.random_articles(10)
  with open(DEST_LOG, 'a', encoding='utf-8') as f:
    for title in articles:
      try:
        article = fetch.FetchModel.fetchWP(title)
        with open(DEST_DIR+title+'.html', 'w', encoding='utf-8') as g:
          g.write(article)
        f.write(title+'.html\n')
      except Exception as e:
        print(e)