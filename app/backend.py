import json
from app.app import app, db

from app.tables import GRefinement
from app.tables import Extraction
from app.tables import Fetch
from app.tables import Nerd
from app.tables import Triplegen
from app.tables import Tripleval
from app.tables import FRefinement
from app.tables import NRefinement
from app.tables import TGRefinement
from app.tables import TERefinement

import app.graph as graph
import app.fetch as fetch
import app.nerd as nerd
import app.triplegen as triplegen
import app.tripleval as tripleval

from app.utils import *

from app.config import DATA_PATH

def filters_grefinement(user_input):
  gr = GRefinement.query.filter_by(graph=user_input['selected_graph']).all()
  return {'grefinement_list' : [
            {'name': it.name, 'value': it.id} for it in gr
           ]}

def filters_extraction(user_input):
  e = Extraction.query.filter_by(grefinement=user_input['selected_grefinement']).all()
  return {'extraction_list': [
             {'name': it.name, 'page': it.page, 'value': it.id} for it in e
            ]}

def filters_fetch(user_input):
  f = Fetch.query.filter_by(extraction=user_input['selected_extraction']).all()
  return {'fetch_list': [
             {'name': 'FETCH', 'value': it.id} for it in f
            ]}


def filters_frefinement(user_input):
  fr = FRefinement.query.filter_by(fetch=user_input['selected_fetch']).all()
  return {'frefinement_list': [
             {'name': it.name, 'value': it.id, 'is_none': it.is_none} for it in fr
            ]}



nerd_dictionary = {1: 'WP',
                   2: 'Spotlight',
                   3: 'SpacyNER',
                   4: 'FullNerd'}

def filters_nerd(user_input):
  n = Nerd.query.filter_by(frefinement=user_input['selected_frefinement']).all()
  return {'nerd_list': [
             {'name': nerd_dictionary[it.model], 'value': it.id} for it in n
            ]}



def filters_nrefinement(user_input):
  nr = NRefinement.query.filter_by(nerd=user_input['selected_nerd']).all()
  return {'nrefinement_list': [
             {'name': it.name, 'value': it.id, 'is_none': it.is_none} for it in nr
            ]}

triplegen_dictionary = {1: 'Alpha',
                   2: 'Beta',
                   3: 'Gamma',
                   4: 'Delta',
                   5: 'Epsilon',
                   6: 'Zeta'}


def filters_triplegen(user_input):
  tg = Triplegen.query.filter_by(nrefinement=user_input['selected_nrefinement']).all()
  return {'triplegen_list': [
             {'name': triplegen_dictionary[it.model], 'value': it.id} for it in tg
            ]}



def filters_tgrefinement(user_input):
  tgr = TGRefinement.query.filter_by(triplegen=user_input['selected_triplegen']).all()
  return {'tgrefinement_list': [
             {'name': it.name, 'value': it.id, 'is_none': it.is_none} for it in tgr
            ]}


def filters_tripleval(user_input):
  te = Tripleval.query.filter_by(tgrefinement=user_input['selected_tgrefinement']).all()
  return {'tripleval_list': [
             {'name': 'TRIPLEVAL', 'value': it.id} for it in te
            ]}



def filters_terefinement(user_input):
  ter = TERefinement.query.filter_by(tripleval=user_input['selected_tripleval']).all()
  return {'terefinement_list': [
             {'name': it.name, 'value': it.id, 'is_none': it.is_none} for it in ter
            ]}


def read_grefinement(user_input):
  """
  if user_input['selected_grefinement'] == 1:
    return {'statements': []}
  if user_input['selected_grefinement'] == 2:
    return {'statements': [
            {
             's' : '<https://calvoritmo.com/tfm/entity/4d96d16c-655f-4d6a-8733-370a7986e958>',
             'p' : '<http://www.w3.org/2000/01/rdf-schema#label>',
             'o' : 'Core'
            }
            ]}
  return None
  """
  gr = GRefinement.query.filter_by(id=user_input['selected_grefinement']).first()
  return graph.GroundTruth(gr.filename).exportJSON()

def read_frefinement(user_input):
  fr = FRefinement.query.filter_by(id=user_input['selected_frefinement']).first()
  return fetch.Fetch(fr.filename).exportJSON()


def read_nrefinement(user_input):
  nr = NRefinement.query.filter_by(id=user_input['selected_nrefinement']).first()
  return nerd.Nerd(nr.filename).exportJSON()


def read_tgrefinement(user_input):
  tgr = TGRefinement.query.filter_by(id=user_input['selected_tgrefinement']).first()
  return triplegen.Triplegen(tgr.filename).exportJSON()


def read_terefinement(user_input):
  ter = TERefinement.query.filter_by(id=user_input['selected_terefinement']).first()
  return tripleval.Tripleval(ter.filename).exportJSON()


def create_grefinement(user_input):
  print(f'Attempting to create grefinement based on graph {user_input["selected_graph"]}')
  if user_input['selected_graph'] not in [1, 2]:
    return None
  filename = f'{DATA_PATH}/grefinement/{getuuid()}.ttl'
  graph.GroundTruth().importJSON(user_input['graph_refinement']).ttlg.save(filename)
  print('ee')
  gr = GRefinement(name=user_input['name'], graph=user_input["selected_graph"], filename=filename, is_none=False)
  db.session.add(gr)
  db.session.commit()
  return {}

def create_extraction_prefix(user_input):
  print(f'Attempting to create {user_input["extraction_number"]} random extractions with_prefix {user_input["extraction_prefix"]} over graph refinement {user_input["selected_grefinement"]}')
  if user_input['selected_grefinement'] not in [1,2]:
    return None
  if user_input['extraction_number'] < 1:
    return None
  return {}


def create_extraction_url(user_input):
  page = user_input["extraction_page"]
  selected_grefinement = user_input["selected_grefinement"]
  name = page.replace('https://en.wikipedia.org/wiki/','')
  extraction = Extraction(page=page, name=name, grefinement=selected_grefinement)
  db.session.add(extraction)
  db.session.commit()
  db.session.refresh(extraction)
  f = Fetch(extraction=extraction.id)
  db.session.add(f)
  db.session.commit()
  db.session.refresh(f)
  filename = f'{DATA_PATH}/fetch/{getuuid()}.ttl'
  article = fetch.FetchModel.fetchWP(name)
  fetch.WikipediaHTML.generate(article, None).asGraph().save(filename)
  fr = FRefinement(is_none=True, name='None', fetch=f.id, filename=filename)
  db.session.add(fr)
  db.session.commit()
  return {}


def create_frefinement(user_input):
  name = user_input['name']
  selected_fetch = user_input['selected_fetch']
  fetch_refinement = user_input['fetch_refinement']
  selected_frefinement = FRefinement.query.filter_by(is_none=True, fetch=selected_fetch).first().filename
  filename=f'{DATA_PATH}/fetch/{getuuid()}.ttl'
  fetch.Fetch(filename=selected_frefinement).importJSON(fetch_refinement).asGraph().save(filename)
  fr = FRefinement(fetch=selected_fetch, name=name, filename=filename, is_none=False)
  db.session.add(fr)
  db.session.commit()
  return {}

def create_nrefinement(user_input):
  name = user_input['name']
  selected_nerd = user_input['selected_nerd']
  nerd_refinement = user_input['nerd_refinement']
  selected_nrefinement = NRefinement.query.filter_by(is_none=True, nerd=selected_nerd).first().filename
  filename=f'{DATA_PATH}/nerd/{getuuid()}.ttl'
  nerd.Nerd(filename=selected_nrefinement).importJSON(nerd_refinement).asGraph().save(filename)
  nr = NRefinement(nerd=selected_nerd, name=name, filename=filename, is_none=False)
  db.session.add(nr)
  db.session.commit()
  return {}


def create_tgrefinement(user_input):
  name = user_input['name']
  selected_triplegen = user_input['selected_triplegen']
  triplegen_refinement = user_input['triplegen_refinement']
  selected_tgrefinement = TGRefinement.query.filter_by(is_none=True, triplegen=selected_triplegen).first().filename
  filename=f'{DATA_PATH}/triplegen/{getuuid()}.ttl'
  triplegen.Triplegen(filename=selected_tgrefinement).importJSON(triplegen_refinement).asGraph().save(filename)
  tgr = TGRefinement(triplegen=selected_triplegen, name=name, filename=filename, is_none=False)
  db.session.add(tgr)
  db.session.commit()
  return {}


def create_terefinement(user_input):
  name = user_input['name']
  selected_tripleval = user_input['selected_tripleval']
  tripleval_refinement = user_input['tripleval_refinement']
  selected_terefinement = TERefinement.query.filter_by(is_none=True, tripleval=selected_tripleval).first().filename
  filename=f'{DATA_PATH}/tripleval/{getuuid()}.ttl'
  tripleval.Tripleval(filename=selected_terefinement).importJSON(tripleval_refinement).asGraph().save(filename)
  ter = TERefinement(tripleval=selected_tripleval, name=name, filename=filename, is_none=False)
  db.session.add(ter)
  db.session.commit()
  return {}

def update_grefinement(user_input):
  print(f'Attempting to update grefinement {user_input["selected_grefinement"]}')
  if user_input['selected_grefinement'] not in [1, 2]:
    return None
  print(str(user_input['graph_refinement']))
  return {}


def update_frefinement(user_input):
  print(f'Attempting to update frefinement {user_input["selected_frefinement"]}')
  if user_input['selected_frefinement'] not in [1, 2]:
    return None
  if user_input['selected_frefinement'] == 1:
    return None
  print(str(user_input['fetch_refinement']))
  return {}


def update_nrefinement(user_input):
  print(f'Attempting to update nrefinement {user_input["selected_nrefinement"]}')
  if user_input['selected_nrefinement'] not in [1, 2]:
    return None
  if user_input['selected_nrefinement'] == 1:
    return None
  print(str(user_input['nerd_refinement']))
  return {}


def update_tgrefinement(user_input):
  print(f'Attempting to update tgrefinement {user_input["selected_tgrefinement"]}')
  if user_input['selected_tgrefinement'] not in [1, 2]:
    return None
  if user_input['selected_tgrefinement'] == 1:
    return None
  print(str(user_input['triplegen_refinement']))
  return {}


def update_terefinement(user_input):
  print(f'Attempting to update terefinement {user_input["selected_terefinement"]}')
  if user_input['selected_terefinement'] not in [1, 2]:
    return None
  if user_input['selected_terefinement'] == 1:
    return None
  print(str(user_input['tripleval_refinement']))
  return {}


def remove_grefinement(user_input):
  gr = GRefinement.query.filter_by(id=user_input['selected_grefinement']).first()
  db.session.delete(gr)
  db.session.commit()
  return {}

def remove_frefinement(user_input):
  fr = FRefinement.query.filter_by(id=user_input['selected_frefinement']).first()
  db.session.delete(fr)
  db.session.commit()
  return {}

def remove_nrefinement(user_input):
  nr = NRefinement.query.filter_by(id=user_input['selected_nrefinement']).first()
  db.session.delete(nr)
  db.session.commit()
  return {}

def remove_tgrefinement(user_input):
  tgr = TGRefinement.query.filter_by(id=user_input['selected_tgrefinement']).first()
  db.session.delete(tgr)
  db.session.commit()
  return {}

def remove_terefinement(user_input):
  ter = TERefinement.query.filter_by(id=user_input['selected_terefinement']).first()
  db.session.delete(ter)
  db.session.commit()
  return {}
