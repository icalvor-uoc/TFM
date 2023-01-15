import json
import os
import sqlite3
import app.fetch
import app.nerd
import app.triplegen

STATIC_DIR = os.path.realpath(os.path.dirname(os.path.realpath(__file__))+'\\..\\app\\static\\')

con = sqlite3.connect('app/db.sqlite')

# /filters/extraction
cur = con.cursor()
ID = '2'
filters = []
for name, page, value in cur.execute('select name, page, id from extraction where grefinement == ?', ID):
  filters = filters + [{'name': name, 'value': value, 'page': page}]
with open(STATIC_DIR+'\\filters\\extraction\\'+ID, 'w', encoding='utf-8') as file:
  json.dump(filters, file)

# /filters/fetch
cur = con.cursor()
cur2 = con.cursor()
for ID in cur.execute('select distinct id from extraction'):
  ID = str(ID[0])
  filters = []
  for value in cur2.execute('select id from fetch where extraction == ?', [ID]):
    filters = filters + [{'name': 'WP', 'value': value}]
  with open(STATIC_DIR+'\\filters\\fetch\\'+ID, 'w', encoding='utf-8') as file:
    json.dump(filters, file)
    
# /filters/frefinement
cur = con.cursor()
cur2 = con.cursor()
for ID in cur.execute('select distinct id from fetch'):
  ID = str(ID[0])
  filters = []
  for name, value, is_none in cur2.execute('select name, id, is_none from f_refinement where fetch == ?', [ID]):
    filters = filters + [{'name': name, 'value': value, 'is_none': is_none}]
  with open(STATIC_DIR+'\\filters\\frefinement\\'+ID, 'w', encoding='utf-8') as file:
    json.dump(filters, file)

# /filters/nerd
cur = con.cursor()
cur2 = con.cursor()
for ID in cur.execute('select distinct id from f_refinement'):
  ID = str(ID[0])
  filters = []
  for name, value in cur2.execute('select model, id from nerd where frefinement == ?', [ID]):
    filters = filters + [{'name': name, 'value': value}]
  with open(STATIC_DIR+'\\filters\\nerd\\'+ID, 'w', encoding='utf-8') as file:
    json.dump(filters, file)
  
# /filters/nrefinement
cur = con.cursor()
cur2 = con.cursor()
for ID in cur.execute('select distinct id from nerd'):
  ID = str(ID[0])
  filters = []
  for name, value, is_none in cur2.execute('select name, id, is_none from n_refinement where nerd == ?', [ID]):
    filters = filters + [{'name': name, 'value': value, 'is_none': is_none}]
  with open(STATIC_DIR+'\\filters\\nrefinement\\'+ID, 'w', encoding='utf-8') as file:
    json.dump(filters, file)

# /filters/triplegen
cur = con.cursor()
cur2 = con.cursor()
for ID in cur.execute('select distinct id from n_refinement'):
  ID = str(ID[0])
  filters = []
  for name, value in cur2.execute('select model, id from triplegen where nrefinement == ?', [ID]):
    filters = filters + [{'name': name, 'value': value}]
  with open(STATIC_DIR+'\\filters\\triplegen\\'+ID, 'w', encoding='utf-8') as file:
    json.dump(filters, file)

# /filters/tgrefinement
cur = con.cursor()
cur2 = con.cursor()
for ID in cur.execute('select distinct id from triplegen'):
  ID = str(ID[0])
  filters = []
  for name, value, is_none in cur2.execute('select name, id, is_none from tg_refinement where triplegen == ?', [ID]):
    filters = filters + [{'name': name, 'value': value, 'is_none': is_none}]
  with open(STATIC_DIR+'\\filters\\tgrefinement\\'+ID, 'w', encoding='utf-8') as file:
    json.dump(filters, file)
    
# /read/frefinement
cur = con.cursor()
for ID, filename in cur.execute('select id, filename from f_refinement'):
  with open(STATIC_DIR+'\\read\\frefinement\\'+str(ID), 'w', encoding='utf-8') as file:
    try:
      json.dump(app.fetch.Fetch(filename=filename).exportJSON(), file)
    except Exception:
      print(f'failed {filename}')

# /read/nrefinement
cur = con.cursor()
for ID, filename in cur.execute('select id, filename from n_refinement'):
  with open(STATIC_DIR+'\\read\\nrefinement\\'+str(ID), 'w', encoding='utf-8') as file:
    try:
      json.dump(app.nerd.Nerd(filename=filename).exportJSON(), file)
    except Exception:
      print(f'failed {filename}')

# /read/tgrefinement
cur = con.cursor()
for ID, filename in cur.execute('select id, filename from tg_refinement'):
  with open(STATIC_DIR+'\\read\\tgrefinement\\'+str(ID), 'w', encoding='utf-8') as file:
    try:
      json.dump(app.triplegen.Triplegen(filename=filename).exportJSON(), file)
    except Exception:
      print(f'failed {filename}')
