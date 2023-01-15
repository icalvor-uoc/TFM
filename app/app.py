from flask import Flask
from flask import render_template
from flask import jsonify
from flask import request
from flask import redirect, url_for
# pip install python-dotenv
from dotenv import load_dotenv

import requests

import json

import os
import sys

sys.setrecursionlimit(10000)

from app.utils import *

# pip install flask-sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
load_dotenv('./.flaskenv')

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
import app.backend as backend

from app.config import DATA_PATH, PRODUCTION, APP_PATH_PREFIX

def sanitize(inputs):
  if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
    raise Exception()
  res = {}
  if request.method == 'GET':
    user_input = request.args.to_dict()
  else:
    user_input = request.json
  for req in inputs:
    if req['name'] not in user_input:
      raise Exception()
    if req['type'] == int:
      user_input[req['name']] = int(user_input[req['name']])
    if type(user_input[req['name']]) != req['type']:      
      raise Exception()
    res[req['name']] = user_input[req['name']]
  return res

@app.route('/')
def index():
  return redirect(url_for('app_gui'))  

# /app
@app.route(f'{APP_PATH_PREFIX}/app', methods = ['GET'])
def app_gui():
  return render_template('app.html')

# /app/filters/grefinement
@app.route(f'{APP_PATH_PREFIX}/app/filters/grefinement', methods = ['GET'])
def filters_grefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_graph',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.filters_grefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/filters/extraction
@app.route(f'{APP_PATH_PREFIX}/app/filters/extraction', methods = ['GET'])
def filters_extraction():
  try:
    user_input = sanitize([
    {'name': 'selected_grefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.filters_extraction(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/filters/fetch
@app.route(f'{APP_PATH_PREFIX}/app/filters/fetch', methods = ['GET'])
def filters_fetch():
  try:
    user_input = sanitize([
    {'name': 'selected_extraction',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.filters_fetch(user_input)
    if reply == None:
      return "Client error", 400
  except Exception as e:
    return "Server error", 500
  return jsonify(reply), 200

# /app/filters/frefinement
@app.route(f'{APP_PATH_PREFIX}/app/filters/frefinement', methods = ['GET'])
def filters_frefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_fetch',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.filters_frefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception as e:
    return "Server error", 500
  return jsonify(reply), 200

# /app/filters/nerd
@app.route(f'{APP_PATH_PREFIX}/app/filters/nerd', methods = ['GET'])
def filters_nerd():
  try:
    user_input = sanitize([
    {'name': 'selected_frefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.filters_nerd(user_input)
    if reply == None:
      return "Client error", 400
  except Exception as e:
    print(e)
    return "Server error" + str(e), 500
  return jsonify(reply), 200

# /app/filters/nrefinement
@app.route(f'{APP_PATH_PREFIX}/app/filters/nrefinement', methods = ['GET'])
def filters_nrefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_nerd',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.filters_nrefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/filters/triplegen
@app.route(f'{APP_PATH_PREFIX}/app/filters/triplegen', methods = ['GET'])
def filters_triplegen():
  try:
    user_input = sanitize([
    {'name': 'selected_nrefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.filters_triplegen(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/filters/tgrefinement
@app.route(f'{APP_PATH_PREFIX}/app/filters/tgrefinement', methods = ['GET'])
def filters_tgrefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_triplegen',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.filters_tgrefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception as e:
    return "Server error", 500
  return jsonify(reply), 200

# /app/filters/tripleval
@app.route(f'{APP_PATH_PREFIX}/app/filters/tripleval', methods = ['GET'])
def filters_tripleval():
  try:
    user_input = sanitize([
    {'name': 'selected_tgrefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.filters_tripleval(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/filters/terefinement
@app.route(f'{APP_PATH_PREFIX}/app/filters/terefinement', methods = ['GET'])
def filters_terefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_tripleval',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.filters_terefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/read/grefinement
@app.route(f'{APP_PATH_PREFIX}/app/read/grefinement', methods = ['GET'])
def read_grefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_grefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.read_grefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/read/frefinement
@app.route(f'{APP_PATH_PREFIX}/app/read/frefinement', methods = ['GET'])
def read_frefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_frefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.read_frefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception as e:
    return "Server error", 500
  return jsonify(reply), 200

# /app/read/nrefinement
@app.route(f'{APP_PATH_PREFIX}/app/read/nrefinement', methods = ['GET'])
def read_nrefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_nrefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.read_nrefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception as e:
    return "Server error", 500
  return jsonify(reply), 200

# /app/read/tgrefinement             
@app.route(f'{APP_PATH_PREFIX}/app/read/tgrefinement', methods = ['GET'])
def read_tgrefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_tgrefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    import traceback
    reply = backend.read_tgrefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception as e:
    print(e)
    print(traceback.format_exc())
    return "Server error", 500
  return jsonify(reply), 200

# /app/read/terefinement
@app.route(f'{APP_PATH_PREFIX}/app/read/terefinement', methods = ['GET'])
def read_terefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_terefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.read_terefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/create/grefinement
@app.route(f'{APP_PATH_PREFIX}/app/create/grefinement', methods = ['POST'])
def create_grefinement():
  try:
    user_input = sanitize([
    {'name': 'name',
     'type': str},
    {'name': 'graph_refinement',
     'type': dict},
    {'name': 'selected_graph',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.create_grefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/create/extraction_prefix
@app.route(f'{APP_PATH_PREFIX}/app/create/extraction_prefix', methods=['POST'])
def create_extraction_prefix():
  try:
    user_input = sanitize([
    {'name': 'extraction_number',
     'type': int},
    {'name': 'extraction_prefix',
     'type': str},
    {'name': 'selected_grefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.create_extraction_prefix(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/create/extraction_url
@app.route(f'{APP_PATH_PREFIX}/app/create/extraction_url', methods=['POST'])
def create_extraction_url():
  try:
    user_input = sanitize([
    {'name': 'extraction_page',
     'type': str},
    {'name': 'selected_grefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.create_extraction_url(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/create/frefinement 
@app.route(f'{APP_PATH_PREFIX}/app/create/frefinement', methods=['POST'])
def create_frefinement():
  try:
    user_input = sanitize([
    {'name': 'name',
     'type': str},
    {'name': 'fetch_refinement',
     'type': dict},
    {'name': 'selected_fetch',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.create_frefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/create/nrefinement
@app.route(f'{APP_PATH_PREFIX}/app/create/nrefinement', methods=['POST'])
def create_nrefinement():
  try:
    user_input = sanitize([
    {'name': 'name',
     'type': str},
    {'name': 'nerd_refinement',
     'type': dict},
    {'name': 'selected_nerd',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.create_nrefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception as e:
    return "Server error", 500
  return jsonify(reply), 200

# /app/create/tgrefinement
@app.route(f'{APP_PATH_PREFIX}/app/create/tgrefinement', methods=['POST'])
def create_tgrefinement():
  try:
    user_input = sanitize([
    {'name': 'name',
     'type': str},
    {'name': 'triplegen_refinement',
     'type': dict},
    {'name': 'selected_triplegen',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.create_tgrefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/create/terefinement
@app.route(f'{APP_PATH_PREFIX}/app/create/terefinement', methods=['POST'])
def create_terefinement():
  try:
    user_input = sanitize([
    {'name': 'name',
     'type': str},
    {'name': 'tripleval_refinement',
     'type': dict},
    {'name': 'selected_tripleval',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.create_terefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/update/grefinement
@app.route(f'{APP_PATH_PREFIX}/app/update/grefinement', methods = ['POST'])
def update_grefinement():
  try:
    user_input = sanitize([
    {'name': 'name',
     'type': str},
    {'name': 'graph_refinement',
     'type': dict},
    {'name': 'selected_grefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.update_grefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/update/frefinement  
@app.route(f'{APP_PATH_PREFIX}/app/update/frefinement', methods=['POST'])
def update_frefinement():
  try:
    user_input = sanitize([
    {'name': 'fetch_refinement',
     'type': dict},
    {'name': 'selected_frefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.update_frefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/update/nrefinement
@app.route(f'{APP_PATH_PREFIX}/app/update/nrefinement', methods=['POST'])
def update_nrefinement():
  try:
    user_input = sanitize([
    {'name': 'nerd_refinement',
     'type': dict},
    {'name': 'selected_nrefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.update_nrefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/update/tgrefinement
@app.route(f'{APP_PATH_PREFIX}/app/update/tgrefinement', methods=['POST'])
def update_tgrefinement():
  try:
    user_input = sanitize([
    {'name': 'triplegen_refinement',
     'type': dict},
    {'name': 'selected_tgrefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.update_tgrefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/update/terefinement
@app.route(f'{APP_PATH_PREFIX}/app/update/terefinement', methods=['POST'])
def update_terefinement():
  try:
    user_input = sanitize([
    {'name': 'tripleval_refinement',
     'type': dict},
    {'name': 'selected_terefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.update_terefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/remove/grefinement
@app.route(f'{APP_PATH_PREFIX}/app/remove/grefinement', methods = ['POST'])
def remove_grefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_grefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.remove_grefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/remove/frefinement
@app.route(f'{APP_PATH_PREFIX}/app/remove/frefinement', methods=['POST'])
def remove_frefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_frefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.remove_frefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/remove/nrefinement
@app.route(f'{APP_PATH_PREFIX}/app/remove/nrefinement', methods=['POST'])
def remove_nrefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_nrefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.remove_nrefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/remove/tgrefinement
@app.route(f'{APP_PATH_PREFIX}/app/remove/tgrefinement', methods=['POST'])
def remove_tgrefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_tgrefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.remove_tgrefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

# /app/remove/terefinement
@app.route(f'{APP_PATH_PREFIX}/app/remove/terefinement', methods=['POST'])
def remove_terefinement():
  try:
    user_input = sanitize([
    {'name': 'selected_terefinement',
     'type': int}
    ])
  except Exception:
    return "Client error", 400
  try:
    reply = backend.remove_terefinement(user_input)
    if reply == None:
      return "Client error", 400
  except Exception:
    return "Server error", 500
  return jsonify(reply), 200

if __name__ == '__main__':
  app.run()

from app.tables import FRefinement
from app.tables import NRefinement
from app.tables import TGRefinement
from app.tables import NExecution
from app.tables import TGExecution
from app.tables import TEExecution

from app.tables import Nerd
from app.tables import NRefinement
from app.tables import Triplegen
from app.tables import TGRefinement
from app.tables import Tripleval
from app.tables import TERefinement
from app.tables import Fetch

import app.fetch as fetch
import app.nerd as nerd
import app.triplegen as triplegen
import app.tripleval as tripleval
import app.graph as graph

@app.route(f'{APP_PATH_PREFIX}/app/bg/nerd', methods=['POST', 'GET'])
def bg_WP():
  in_process = db.session.query(FRefinement).filter(~FRefinement.id.in_(db.session.query(NExecution.frefinement))).all()
  for frefinement in in_process:
    fStage = fetch.Fetch(filename=frefinement.filename)
    nStage = nerd.WP.generate(fStage, None)
    filename = f'{DATA_PATH}/nerd/{getuuid()}.ttl'
    nStage.asGraph().save(filename)
    n = Nerd(model=1, frefinement=frefinement.id)
    db.session.add(n)
    db.session.commit()
    db.session.refresh(n)
    db.session.add(NRefinement(nerd=n.id, name='None', filename=filename, is_none=True))
    db.session.add(NExecution(frefinement=frefinement.id))
    db.session.commit()
    
    if not PRODUCTION:    

        fStage = fetch.Fetch(filename=frefinement.filename)
        nStage = nerd.Spotlight.generate(fStage, None)
        filename = f'{DATA_PATH}/nerd/{getuuid()}.ttl'
        nStage.asGraph().save(filename)
        n = Nerd(model=2, frefinement=frefinement.id)
        db.session.add(n)
        db.session.commit()
        db.session.refresh(n)
        db.session.add(NRefinement(nerd=n.id, name='None', filename=filename, is_none=True))
        db.session.add(NExecution(frefinement=frefinement.id))
        db.session.commit()
        
        fStage = fetch.Fetch(filename=frefinement.filename)
        nStage = nerd.SpacyNER.generate(fStage, None)
        filename = f'{DATA_PATH}/nerd/{getuuid()}.ttl'
        nStage.asGraph().save(filename)
        n = Nerd(model=3, frefinement=frefinement.id)
        db.session.add(n)
        db.session.commit()
        db.session.refresh(n)
        db.session.add(NRefinement(nerd=n.id, name='None', filename=filename, is_none=True))
        db.session.add(NExecution(frefinement=frefinement.id))
        db.session.commit()
        
        fStage = fetch.Fetch(filename=frefinement.filename)
        nStage = nerd.FullNerd.generate(fStage, None)
        filename = f'{DATA_PATH}/nerd/{getuuid()}.ttl'
        nStage.asGraph().save(filename)
        n = Nerd(model=4, frefinement=frefinement.id)
        db.session.add(n)
        db.session.commit()
        db.session.refresh(n)
        db.session.add(NRefinement(nerd=n.id, name='None', filename=filename, is_none=True))
        db.session.add(NExecution(frefinement=frefinement.id))
        db.session.commit()

  return '{}', 200


import threading
import atexit

t_ = threading.Thread()  # ???

def t_bg_WP():
  global t_
  print("Running WP")
  bg_WP()
  print("Running gamma")
  bg_gamma()
  print("Running bart")
  bg_bart()
  t_ = threading.Timer(3, t_bg_WP, ())
  t_.start()
  

# t_ = threading.Timer(3, t_bg_WP, ())
# t_.start()

def interrupt():
  global t_
  t_.cancel()
  
# atexit.register(interrupt)
  
@app.route(f'{APP_PATH_PREFIX}/app/bg/triplegen', methods=['POST', 'GET'])
def bg_gamma():
  in_process = db.session.query(NRefinement).filter(~NRefinement.id.in_(db.session.query(TGExecution.nrefinement))).all()
  for nrefinement in in_process:
    nStage = nerd.Nerd(filename=nrefinement.filename)
    
    if not PRODUCTION:
    
        tgStage = triplegen.Alpha.generate(nStage, graph.GroundTruth.dbpedia_kb())
        filename = f'{DATA_PATH}/triplegen/{getuuid()}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=1, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()

        tgStage = triplegen.Beta.generate(nStage, graph.GroundTruth.dbpedia_kb())
        filename = f'{DATA_PATH}/triplegen/{getuuid()}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=2, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()

    
    tgStage = triplegen.Gamma.generate(nStage, graph.GroundTruth.dbpedia_kb())
    filename = f'{DATA_PATH}/triplegen/{getuuid()}.ttl'
    tgStage.asGraph().save(filename)
    tg = Triplegen(model=3, nrefinement=nrefinement.id)
    db.session.add(tg)
    db.session.commit()
    db.session.refresh(tg)
    db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
    db.session.add(TGExecution(nrefinement=nrefinement.id))
    db.session.commit()
    
    if not PRODUCTION:
    
        tgStage = triplegen.Delta.generate(nStage, graph.GroundTruth.dbpedia_kb())
        filename = f'{DATA_PATH}/triplegen/{getuuid()}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=4, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()  
        
        tgStage = triplegen.Epsilon.generate(nStage, graph.GroundTruth.dbpedia_kb())
        filename = f'{DATA_PATH}/triplegen/{getuuid()}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=5, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()  
        
        tgStage = triplegen.Zeta.generate(nStage, graph.GroundTruth.dbpedia_kb())
        filename = f'{DATA_PATH}/triplegen/{getuuid()}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=6, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()
        
  return '{}', 200

  
@app.route(f'{APP_PATH_PREFIX}/app/bg/tripleval', methods=['POST', 'GET'])
def bg_bart():
  in_process = db.session.query(TGRefinement).filter(~TGRefinement.id.in_(db.session.query(TEExecution.tgrefinement))).all()[:3]
  for tgrefinement in in_process:
    if not PRODUCTION:
    
        tgStage = triplegen.Triplegen(filename=tgrefinement.filename)
        teStage = tripleval.BartLargeMNLI.generate(tgStage, None)
        filename = f'{DATA_PATH}/tripleval/{getuuid()}.ttl'
        teStage.asGraph().save(filename)
        te = Tripleval(model=1, tgrefinement=tgrefinement.id)
        db.session.add(te)
        db.session.commit()
        db.session.refresh(te)
        db.session.add(TERefinement(tripleval=te.id, name='None', filename=filename, is_none=True))
        db.session.add(TEExecution(tgrefinement=tgrefinement.id))
        db.session.commit()    
  return '{}', 200

import csv  
import time
  
@app.route(f'{APP_PATH_PREFIX}/app/batch/fetch', methods=['POST', 'GET'])
def fetcher():
  articles = fetch.FetchModel.random_articles(500)
  
  
  for title in articles:
    print(f'Fetching {title}:', end=' ')
    try:
      article = fetch.FetchModel.fetchWP(title)
      start_time = time.time()
      f = fetch.WikipediaHTML.generate(article, None)
      end_time = time.time()
      print(f'{f.uuid}')
      f.asGraph().save(f'C:/Users/calvo/TFM/app/data/fetch/{f.uuid}.ttl')
      fe = Fetch(extraction=999)
      db.session.add(fe)
      db.session.commit()
      fr = FRefinement(is_none=True, name='None', fetch=fe.id, filename=f'C:/Users/calvo/TFM/app/data/fetch/{f.uuid}.ttl')
      db.session.add(fr)
      db.session.commit()
      with open(f'fetcher.csv', 'a', encoding='utf-8') as file:
        c = csv.writer(file)
        c.writerow([f.uuid, f.mainSection.title,
                        os.path.getsize(f'C:/Users/calvo/TFM/app/data/fetch/{f.uuid}.ttl'),
                        end_time - start_time,
                    len(list(f.mainSection.sections())), len(list(f.mainSection.lists()))])
    except Exception as e:
      print('failed')
      print(e)
  return '{}', 200

@app.route(f'{APP_PATH_PREFIX}/app/batch/nerd', methods=['POST', 'GET'])
def nerder():

  in_process = db.session.query(FRefinement).filter(~FRefinement.id.in_(db.session.query(NExecution.frefinement))).all()
  for frefinement in in_process:
    try:
        fStage = fetch.Fetch(filename=frefinement.filename)
        print(f'Nerding {fStage.mainSection.title}:', end=' ')
        print(fStage.uuid)
        start_time = time.time()
        nStage = nerd.WP.generate(fStage, None)
        end_time = time.time()
        nStage.uuid = fStage.uuid
        filename = f'{DATA_PATH}/nerd/WP-{fStage.uuid}.ttl'
        nStage.asGraph().save(filename)
        n = Nerd(model=1, frefinement=frefinement.id)
        db.session.add(n)
        db.session.commit()
        db.session.refresh(n)
        db.session.add(NRefinement(nerd=n.id, name='None', filename=filename, is_none=True))
        db.session.add(NExecution(frefinement=frefinement.id))
        db.session.commit()
        with open(f'nerder.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in nStage.mainSection.texts():
            c.writerow([fStage.uuid,
                        nStage.mainSection.title,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "WP",
                        t.text,
                        len(list(t._annotations))])
    except Exception as e:
      print('failed')
      print(e)


    try:
        fStage = fetch.Fetch(filename=frefinement.filename)
        print(f'Nerding {fStage.mainSection.title}:', end=' ')
        print(fStage.uuid)
        start_time = time.time()
        nStage = nerd.Spotlight.generate(fStage, None)
        end_time = time.time()
        nStage.uuid = fStage.uuid
        filename = f'{DATA_PATH}/nerd/Spotlight-{fStage.uuid}.ttl'
        nStage.asGraph().save(filename)
        n = Nerd(model=2, frefinement=frefinement.id)
        db.session.add(n)
        db.session.commit()
        db.session.refresh(n)
        db.session.add(NRefinement(nerd=n.id, name='None', filename=filename, is_none=True))
        db.session.add(NExecution(frefinement=frefinement.id))
        db.session.commit()
        with open(f'nerder.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in nStage.mainSection.texts():
            c.writerow([fStage.uuid,
                        nStage.mainSection.title,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "Spotlight",
                        t.text,
                        len(list(t._annotations))])
    except Exception as e:
      print('failed')
      print(e)


    try:
        fStage = fetch.Fetch(filename=frefinement.filename)
        print(f'Nerding {fStage.mainSection.title}:', end=' ')
        print(fStage.uuid)
        start_time = time.time()
        nStage = nerd.SpacyNER.generate(fStage, None)
        end_time = time.time()
        nStage.uuid = fStage.uuid
        filename = f'{DATA_PATH}/nerd/SpacyNER-{fStage.uuid}.ttl'
        nStage.asGraph().save(filename)
        n = Nerd(model=3, frefinement=frefinement.id)
        db.session.add(n)
        db.session.commit()
        db.session.refresh(n)
        db.session.add(NRefinement(nerd=n.id, name='None', filename=filename, is_none=True))
        db.session.add(NExecution(frefinement=frefinement.id))
        db.session.commit()
        with open(f'nerder.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in nStage.mainSection.texts():
            c.writerow([fStage.uuid,
                        nStage.mainSection.title,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "SpacyNER",
                        t.text,
                        len(list(t._annotations))])
    except Exception as e:
      print('failed')
      print(e)


    try:
        fStage = fetch.Fetch(filename=frefinement.filename)
        print(f'Nerding {fStage.mainSection.title}:', end=' ')
        print(fStage.uuid)
        start_time = time.time()
        nStage = nerd.FullNerd.generate(fStage, None)
        end_time = time.time()
        nStage.uuid = fStage.uuid
        filename = f'{DATA_PATH}/nerd/FullNerd-{fStage.uuid}.ttl'
        nStage.asGraph().save(filename)
        n = Nerd(model=4, frefinement=frefinement.id)
        db.session.add(n)
        db.session.commit()
        db.session.refresh(n)
        db.session.add(NRefinement(nerd=n.id, name='None', filename=filename, is_none=True))
        db.session.add(NExecution(frefinement=frefinement.id))
        db.session.commit()
        with open(f'nerder.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in nStage.mainSection.texts():
            c.writerow([fStage.uuid,
                        nStage.mainSection.title,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "FullNerd",
                        t.text,
                        len(list(t._annotations))])
    except Exception as e:
      print('failed')
      print(e)
      
      
#


#

#


  return '{}', 200

@app.route(f'{APP_PATH_PREFIX}/app/batch/triplegen', methods=['POST', 'GET'])
def triplegener():
  import traceback
  in_process = db.session.query(NRefinement).filter(~NRefinement.id.in_(db.session.query(TGExecution.nrefinement))).all()
  for nrefinement in in_process:
    nStage = nerd.Nerd(filename=nrefinement.filename)

    try:
        print(f'Triplegening {nStage.mainSection.title}:', end=' ')
        print(nStage.uuid)
        start_time = time.time()
        tgStage = triplegen.Alpha.generate(nStage, graph.GroundTruth.dbpedia_kb())
        end_time = time.time()
        tgStage.uuid = nStage.uuid
        filename = f'{DATA_PATH}/triplegen/alpha-{nStage.uuid}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=1, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()
        with open(f'triplegener.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in tgStage.units:
            c.writerow([nStage.uuid,
                        nStage.mainSection.title,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "Alpha",
                        len(t.evidence.split(' ')),
                        len(t.description.split(' ')),
                        len(t.evidence),
                        len(t.description),
                        len(t.statements)])
    except Exception as e:
      traceback.format_exc()
      print('failed')
      print(e)
      
    try:
        print(f'Triplegening {nStage.mainSection.title}:', end=' ')
        print(nStage.uuid)
        start_time = time.time()
        tgStage = triplegen.Beta.generate(nStage, graph.GroundTruth.dbpedia_kb())
        end_time = time.time()
        tgStage.uuid = nStage.uuid
        filename = f'{DATA_PATH}/triplegen/beta-{nStage.uuid}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=2, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()
        with open(f'triplegener.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in tgStage.units:
            c.writerow([nStage.uuid,
                        nStage.mainSection.title,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "Beta",
                        len(t.evidence.split(' ')),
                        len(t.description.split(' ')),
                        len(t.evidence),
                        len(t.description),
                        len(t.statements)])
    except Exception as e:
      traceback.format_exc()
      print('failed')
      print(e)
    
    try:
        print(f'Triplegening {nStage.mainSection.title}:', end=' ')
        print(nStage.uuid)
        start_time = time.time()
        tgStage = triplegen.Gamma.generate(nStage, graph.GroundTruth.dbpedia_kb())
        end_time = time.time()
        tgStage.uuid = nStage.uuid
        filename = f'{DATA_PATH}/triplegen/gamma-{nStage.uuid}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=3, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()
        with open(f'triplegener.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in tgStage.units:
            c.writerow([nStage.uuid,
                        nStage.mainSection.title,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "Gamma",
                        len(t.evidence.split(' ')),
                        len(t.description.split(' ')),
                        len(t.evidence),
                        len(t.description),
                        len(t.statements)])
    except Exception as e:
      traceback.format_exc()
      print('failed')
      print(e)
    try:
        print(f'Triplegening {nStage.mainSection.title}:', end=' ')
        print(nStage.uuid)
        start_time = time.time()
        tgStage = triplegen.Delta.generate(nStage, graph.GroundTruth.dbpedia_kb())
        end_time = time.time()
        tgStage.uuid = nStage.uuid
        filename = f'{DATA_PATH}/triplegen/delta-{nStage.uuid}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=4, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()
        with open(f'triplegener.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in tgStage.units:
            c.writerow([nStage.uuid,
                        nStage.mainSection.title,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "Delta",
                        len(t.evidence.split(' ')),
                        len(t.description.split(' ')),
                        len(t.evidence),
                        len(t.description),
                        len(t.statements)])
    except Exception as e:
      traceback.format_exc()
      print('failed')
      print(e)
    try:
        print(f'Triplegening {nStage.mainSection.title}:', end=' ')
        print(nStage.uuid)
        start_time = time.time()
        tgStage = triplegen.Epsilon.generate(nStage, graph.GroundTruth.dbpedia_kb())
        end_time = time.time()
        tgStage.uuid = nStage.uuid
        filename = f'{DATA_PATH}/triplegen/epsilon-{nStage.uuid}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=5, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()
        with open(f'triplegener.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in tgStage.units:
            c.writerow([nStage.uuid,
                        nStage.mainSection.title,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "Epsilon",
                        len(t.evidence.split(' ')),
                        len(t.description.split(' ')),
                        len(t.evidence),
                        len(t.description),
                        len(t.statements)])
    except Exception as e:
      traceback.format_exc()
      print('failed')
      print(e)
    try:
        print(f'Triplegening {nStage.mainSection.title}:', end=' ')
        print(nStage.uuid)
        start_time = time.time()
        tgStage = triplegen.Zeta.generate(nStage, graph.GroundTruth.dbpedia_kb())
        end_time = time.time()
        tgStage.uuid = nStage.uuid
        filename = f'{DATA_PATH}/triplegen/zeta-{nStage.uuid}.ttl'
        tgStage.asGraph().save(filename)
        tg = Triplegen(model=6, nrefinement=nrefinement.id)
        db.session.add(tg)
        db.session.commit()
        db.session.refresh(tg)
        db.session.add(TGRefinement(triplegen=tg.id, name='None', filename=filename, is_none=True))
        db.session.add(TGExecution(nrefinement=nrefinement.id))
        db.session.commit()
        with open(f'triplegener.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in tgStage.units:
            c.writerow([nStage.uuid,
                        nStage.mainSection.title,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "Zeta",
                        len(t.evidence.split(' ')),
                        len(t.description.split(' ')),
                        len(t.evidence),
                        len(t.description),
                        len(t.statements)])
    except Exception as e:
      traceback.format_exc()
      print('failed')
      print(e)

  return '{}', 200
  
@app.route(f'{APP_PATH_PREFIX}/app/batch/tripleval', methods=['POST', 'GET'])
def triplevaler():
  in_process = db.session.query(TGRefinement).filter(~TGRefinement.id.in_(db.session.query(TEExecution.tgrefinement))).all()
  for tgrefinement in in_process:
    try:
        tgStage = triplegen.Triplegen(filename=tgrefinement.filename)
        print(f'Triplevaling:', end=' ')
        print(tgStage.uuid)
        start_time = time.time()
        teStage = tripleval.BartLargeMNLI.generate(tgStage, None)
        end_time = time.time()
        filename = f'{DATA_PATH}/tripleval/{tgStage.uuid}.ttl'
        teStage.asGraph().save(filename)
        te = Tripleval(model=1, tgrefinement=tgrefinement.id)
        db.session.add(te)
        db.session.commit()
        db.session.refresh(te)
        db.session.add(TERefinement(tripleval=te.id, name='None', filename=filename, is_none=True))
        db.session.add(TEExecution(tgrefinement=tgrefinement.id))
        db.session.commit()
        with open(f'triplevaler.csv', 'a', encoding='utf-8') as file:
          c = csv.writer(file)
          for t in teStage.units:
            c.writerow([tgStage.uuid,
                        os.path.getsize(filename),
                        end_time - start_time,
                        "Bart",
                        t.quality,
                        t.certainty])
    except Exception as e:
      print('failed')
      print(e)
  return '{}', 200