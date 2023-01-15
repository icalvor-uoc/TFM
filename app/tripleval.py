import os
import csv
import app.triplegen as triplegen
import app.graph as graph

from app.utils import *

class Tripleval:
  class Unit:
    def __init__(self, evidence, description, quality, certainty, uuid=None):
      self.evidence = evidence
      self.description = description
      self.quality = quality
      self.certainty = certainty
      if uuid == None:
        self.uuid = getuuid()
      else:
        self.uuid = uuid
        
    def __hash__(self):
      return hash((self.evidence, self.description, self.quality, self.certainty))
    def __equals__(self, other):
      return self.quality == other.quality and \
             self.certainty == other.certainty and \
             self.description == other.description and \
             self.evidence == other.evidence

  def __init__(self, filename=None):
    self.parentStage = 'https://calvoritmo.com/tfm/meta/bottom_stage'
    if filename == None:
      self.units = []
      self.uuid = getuuid()
      self.friendlyName = 'Tripleval Stage'
    else:
      ttlg = graph.TurtleGraph(filename=filename)
      tripleval_uri = ttlg.getTriple(p='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', o='https://calvoritmo.com/tfm/meta/Stage')[0]
      self.friendlyName = ttlg.getTriple(s=tripleval_uri, p='https://calvoritmo.com/tfm/meta/stageFriendlyName')[2]
      units = ttlg.getList(tripleval_uri, 'https://calvoritmo.com/tfm/datamodel/tripleval/hasUnits')
      self.units = []
      for unit in units:
        evidence = ttlg.getTriple(s=unit, p='https://calvoritmo.com/tfm/datamodel/tripleval/hasEvidence')[2]
        description = ttlg.getTriple(s=unit, p='https://calvoritmo.com/tfm/datamodel/tripleval/hasDescription')[2]
        quality = ttlg.getTriple(s=unit, p='https://calvoritmo.com/tfm/datamodel/tripleval/hasQuality')[2]
        certainty = ttlg.getTriple(s=unit, p='https://calvoritmo.com/tfm/datamodel/tripleval/hasCertainty')[2]
        self.units = self.units + [Tripleval.Unit(evidence, description, quality, certainty)]
      self.uuid = tripleval_uri.split('/')[-1]
  
  def asGraph(self):
    ttlg = graph.TurtleGraph()
    tripleval_uri = 'https://calvoritmo.com/tfm/data/tripleval/' + self.uuid
    ttlg.addTriple('https://calvoritmo.com/tfm/data/tripleval/'+self.uuid,               'https://calvoritmo.com/tfm/meta/hasParentStage',self.parentStage)
    ttlg.addTriple(tripleval_uri, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'https://calvoritmo.com/tfm/meta/Stage')
    ttlg.setLiteral(tripleval_uri, 'https://calvoritmo.com/tfm/meta/stageFriendlyName', self.friendlyName)
    ttlg.updateList(tripleval_uri, 'https://calvoritmo.com/tfm/datamodel/tripleval/hasUnits', 
                ['https://calvoritmo.com/tfm/data/tripleval/' + unit.uuid for unit in self.units])
    for unit in self.units:
      unit_uri = 'https://calvoritmo.com/tfm/data/tripleval/' + unit.uuid
      statement_uris = []
      ttlg.addTriple(unit_uri, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'https://calvoritmo.com/tfm/datamodel/tripleval/Unit')
      ttlg.setLiteral(unit_uri, 'https://calvoritmo.com/tfm/datamodel/tripleval/hasEvidence', unit.evidence)
      ttlg.setLiteral(unit_uri, 'https://calvoritmo.com/tfm/datamodel/tripleval/hasDescription', unit.description)
      ttlg.setLiteral(unit_uri, 'https://calvoritmo.com/tfm/datamodel/tripleval/hasQuality', unit.quality)
      ttlg.setLiteral(unit_uri, 'https://calvoritmo.com/tfm/datamodel/tripleval/hasCertainty', unit.certainty)
    return ttlg

  def exportJSON(self):
    units = []
    for unit in self.units:
      units = units + [{
                        'evidence' : unit.evidence,
                        'description' : unit.description,
                        'certainty' : unit.certainty,
                        'quality' : unit.quality,
                      }]
    return {'friendlyName' : self.friendlyName,
            'units'        : units}
    
  def importJSON(self, json_dict):
    if len(json_dict['units']) == len(self.units):
      for i in range(len(json_dict['units'])):
        self.units[i].evidence = json_dict['units'][i]['evidence']
        self.units[i].description = json_dict['units'][i]['description']
        self.units[i].certainty = json_dict['units'][i]['certainty']
        self.units[i].quality = json_dict['units'][i]['quality']
    return self

class TriplevalFactory:
  def delete(uuid):
    if os.path.isfile(f'data/tripleval/{uuid}.csv'):
      os.remove(f'data/tripleval/{uuid}.csv')
      
class TriplevalStage:
  def __init__(self, dataframe, uuid=None):
    if uuid == None:
      self.uuid = getuuid()
    else:
      self.uuid = uuid
    self.dataframe = dataframe  
      
  def load(uuid):
    with open(f'data/tripleval/{uuid}.csv', 'r', encoding='utf-8') as f:
      reader = csv.DictReader(f)
      dataframe = list(reader)
    return TriplegenStage(dataframe, uuid=uuid)
      
  def edit(self, dataframe, inplace=False):
    if not inplace:
      self.uuid = getuuid()
    self.dataframe = dataframe
    return self

  def get(self):
    return self.dataframe

  def save(self, uuid=None):
    if uuid == None:
      uuid = self.uuid    
    with open(f'data/tripleval/{uuid}.csv', 'w', encoding='utf-8') as f:
      writer = csv.DictWriter(f, fieldnames=['triple', 'quality', 'certainty'])
      writer.writeheader()
      for it in content:
        writer.writerow(it)
    return self

class Baseline:
  def generate(self, triplegenStage):
    dataframe = []
    for bag in triplegenStage.get_bags():
      triples = str(triplegenStage.flatten(bag=bag))
      dataframe = dataframe + [{'triple':triples, 'quality':1, 'certainty':0}]
    return TriplevalStage(dataframe)
    #  turtle_content = ''
    #  with open(f'data/triplegen/{tgr.filename}.ttl', 'r', encoding='utf-8') as f:
    #    turtle_content = f.read()
    #  turtle_content = re.sub('@base[^\\.]<[^>]*>[^\\.]*\\.', '', turtle_content)
    #  turtle_content = '@base <http://localhost:5000/> . ' + turtle_content
    #  g = rdflib.Graph()
    #  triples = []
    #  try:
    #    g = g.parse(data=turtle_content)
    #    g = triplegen.DBP.flatten(g)
    #    triples = [ f'{a.n3()} {b.n3()} {c.n3()}.' 
    #                for a,b,c in g ]
    #  except Exception:
    #    print('PARSE ERROR ON TURTLE FILE')
    #    print(turtle_content)
    #    return
    #  content = [{'triple':it, 'quality':1, 'certainty':0}
    #              for it in triples]
    

# https://stackoverflow.com/questions/57814535/assertionerror-torch-not-compiled-with-cuda-enabled-in-spite-upgrading-to-cud
# https://stackoverflow.com/questions/63629075/error-in-training-opennmt-caffe2-detectron-ops-dll-not-found

class BartLargeMNLI:
  def generate(triplegenStage, groundTruth):
    if triplegenStage.units == []:
      return Tripleval()
    from transformers import pipeline
    import torch
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    if torch.cuda.is_available():
      classifier = pipeline("zero-shot-classification",
                         model="facebook/bart-large-mnli", device=0)#.to(device)    
    else:
      classifier = pipeline("zero-shot-classification",
                         model="facebook/bart-large-mnli")#, device=0)#.to(device)
    quality_labels = ['Bad', 'Mediocre', 'Good']
    certainty_labels = ['NotSure', 'Sure']
    dataframe = []
    triplevalStage = Tripleval()
    for unit in triplegenStage.units:
      certainty = classifier(f"From the text '{unit.evidence}' we can infer that '{unit.description}'", certainty_labels)['labels'][0]
      quality = classifier(f"From the text '{unit.evidence}' we can infer that '{unit.description}'", quality_labels)['labels'][0]
      triplevalStage.units = triplevalStage.units + [Tripleval.Unit(unit.evidence, unit.description, quality, certainty)]
    return triplevalStage