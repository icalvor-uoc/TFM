import os
import app.fetch as fetch
import app.nerd as nerd
import app.triplegen as triplegen
import app.tripleval as tripleval
import app.graph as graph
import csv
import json
import uuid
import time

def get_uuid():
  return str(uuid.uuid4())

BASE_DIR = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\'

FIRST_ARTICLE = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaa'


SOURCE_FOLDER =  'articles_with_lists' # 'random_articles_with_lists' # 'imported_articles'  #'articles_with_lists'

GT = graph.GroundTruth.dbpedia_kb()

def save_n(stage, model, source_uuid, dest_uuid):
  with open(BASE_DIR+'nerd\\'+model+'.csv', 'a', encoding='utf-8') as g:
    writer = csv.writer(g) 
    writer.writerow([source_uuid, model, dest_uuid])
  stage.asGraph().save(BASE_DIR+'nerd\\'+model+'\\'+dest_uuid+'.ttl')
  with open(BASE_DIR+'nerd\\'+model+'\\'+dest_uuid+'.json', 'w', encoding='utf-8') as i:          
    json.dump(stage.exportJSON(), i)

  
def save_tg(stage, model, source_uuid, dest_uuid):
  with open(BASE_DIR+'triplegen\\'+model+'.csv', 'a', encoding='utf-8') as g:
    writer = csv.writer(g) 
    writer.writerow([source_uuid, model, dest_uuid])
  stage.asGraph().save(BASE_DIR+'triplegen\\'+model+'\\'+dest_uuid+'.ttl')
  with open(BASE_DIR+'triplegen\\'+model+'\\'+dest_uuid+'.json', 'w', encoding='utf-8') as i:          
    json.dump(stage.exportJSON(), i)

  
# def save_te(datapoints):
#   pass

def run_triplegen_models(n_stage, n_uuid, client):
  productive = False
  for model in [(triplegen.Alpha, 'Alpha'),(triplegen.Beta, 'Beta'),(triplegen.Gamma, 'Gamma'),
                (triplegen.Delta, 'Delta'),(triplegen.Zeta, 'Zeta')]:  # (triplegen.Epsilon, 'Epsilon'),
    a = time.time()
    tg_stage = model[0].generate(n_stage, GT, client)
    b = time.time()
    print(model[1]+': '+str(b-a))
    tg_uuid = get_uuid()
    if tg_stage.units != []:
      productive = True
      save_tg(tg_stage, model[1], n_uuid, tg_uuid)
  
  return productive

def run_nerd_models(f_stage, f_uuid, client):
  for model in [(nerd.FullNerd, 'FullNerd')]: #[(nerd.WP, 'WP'), (nerd.Spotlight, 'Spotlight'),
                #(nerd.SpacyNER, 'SpacyNER'), (nerd.FullNerd, 'FullNerd')]:
    a = time.time()
    n_stage = model[0].generate(f_stage, GT)
    b = time.time()
    print(model[1]+': '+str(b-a))
    n_uuid = get_uuid()
    productive = False
    for li in n_stage.mainSection.lists():
      for text in li.texts():
        if list(text.annotations()) != []:
          productive = True
          break
    if productive and run_triplegen_models(n_stage, n_uuid, client):
      save_n(n_stage, model[1], fetch_uuid, n_uuid)    

from openie import StanfordOpenIE 
properties = {
   'openie.affinity_probability_cap': 2 / 3,
}
client = StanfordOpenIE(properties=properties)

with open(BASE_DIR+'fetch\\'+SOURCE_FOLDER+'.csv', 'r', encoding='utf-8') as f:  # List of all articles with lists
  reader = csv.reader(f)
  with StanfordOpenIE(properties=properties) as client:
    #a,b = next(reader)
    #print(a)
    for fetch_html, fetch_uuid in reader:
      if fetch_html.lower() < FIRST_ARTICLE.lower():
        continue
 
  
#    N_DATAPOINTS = {} # CSV schema: source uuid, model name, destination uuid + stage itself
#    TG_DATAPOINTS = {}
#    TE_DATAPOINTS = {}
#    N_PRODUCTIVE = []
#    TG_PRODUCTIVE = []
    
      try:
        f_stage = fetch.Fetch(filename=BASE_DIR+'fetch\\'+SOURCE_FOLDER+'\\'+fetch_uuid+'.ttl')
      
        run_nerd_models(f_stage, fetch_uuid, client)
      
      
      
#      for te in TE_DATAPOINTS:
#        for i, tg in enumerate(TG_DATAPOINTS):
#          if # TBD
#            TG_PRODUCTIVE[i] = True
#            for j, n in enumerate(N_DATAPOINTS):
#              if # TBD
#                N_PRODUCTIVE = True              
      
#      save_n(N_DATAPOINTS)#, N_PRODUCTIVE)
#      save_tg(TG_DATAPOINTS)#, TG_PRODUCTIVE)
#      save_te(TE_DATAPOINTS)      
      
      except Exception as e:
        print(e)
        continue
