from bs4 import BeautifulSoup
import app.graph as graph
import rdflib
import app.nerd as nerd
import app.fetch as fetch
import os
from app.utils import *

import urllib

def uft8(s):
  if not type(s) == str:
    print('Eeueueue')
  return s if type(s) == str else s.decode('utf-8')

class Triplegen:
  class Unit:
    def __init__(self, evidence, statements, description, uuid=None):
      self.evidence = evidence
      self.statements = [tuple(s) for s in statements]
      self.description = description
      if uuid == None:
        self.uuid = getuuid()
      else:
        self.uuid = uuid
        
    def __hash__(self):
      return hash((set(self.statements), self.evidence, self.description))
    def __eq__(self, other):
      return set(self.statements) == set(other.statements) and \
             len(self.evidence) == len(other.evidence)     and \
             sum([self.evidence[i] == other.evidence[i] for i in range(len(other.evidence))])/len(other.evidence) > 0.95 and \
             self.description == other.description
      
  def __init__(self, filename=None):
    self.parentStage = 'https://calvoritmo.com/tfm/meta/bottom_stage'
    if filename == None:
      self.units = []
      self.uuid = getuuid()
      self.friendlyName = 'Triplegen Stage'
    else:
      ttlg = graph.TurtleGraph(filename=filename)
      triplegen_uri = ttlg.getTriple(p='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', o='https://calvoritmo.com/tfm/meta/Stage')[0]
      self.friendlyName = ttlg.getTriple(s=triplegen_uri, p='https://calvoritmo.com/tfm/meta/stageFriendlyName')[2]
      units = ttlg.getList(triplegen_uri, 'https://calvoritmo.com/tfm/datamodel/triplegen/hasUnits')
      self.units = []
      for unit in units:
        statements = []
        for statement in ttlg.getList(unit, 'https://calvoritmo.com/tfm/datamodel/triplegen/hasStatements'):
          subject = ttlg.getTriple(s=statement, p='http://www.w3.org/1999/02/22-rdf-syntax-ns#subject')[2]
          if subject[:7] == 'http://' or subject[:7] == 'https:/':
            subject = '<' + subject + '>'
          predicate = ttlg.getTriple(s=statement, p='http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate')[2]
          if predicate[:7] == 'http://' or predicate[:7] == 'https:/':
            predicate = '<' + predicate + '>'
          obj = ttlg.getTriple(s=statement, p='http://www.w3.org/1999/02/22-rdf-syntax-ns#object')[2]
          if obj[:7] == 'http://' or obj[:7] == 'https:/':
            obj = '<' + obj + '>'
          statements = statements + [(subject, predicate, obj)]
        evidence = ttlg.getTriple(s=unit, p='https://calvoritmo.com/tfm/datamodel/triplegen/hasEvidence')[2]
        description = ttlg.getTriple(s=unit, p='https://calvoritmo.com/tfm/datamodel/triplegen/hasDescription')[2]
        self.units = self.units + [Triplegen.Unit(evidence, statements, description)]
      self.uuid = triplegen_uri.split('/')[-1]
  
  def asGraph(self):
    ttlg = graph.TurtleGraph()
    triplegen_uri = 'https://calvoritmo.com/tfm/data/triplegen/' + self.uuid
    ttlg.addTriple('https://calvoritmo.com/tfm/data/triplegen/'+self.uuid,
                   'https://calvoritmo.com/tfm/meta/hasParentStage',
                   self.parentStage)
    ttlg.addTriple(triplegen_uri, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'https://calvoritmo.com/tfm/meta/Stage')
    ttlg.setLiteral(triplegen_uri, 'https://calvoritmo.com/tfm/meta/stageFriendlyName', self.friendlyName)
    ttlg.updateList(triplegen_uri, 'https://calvoritmo.com/tfm/datamodel/triplegen/hasUnits', 
                ['https://calvoritmo.com/tfm/data/triplegen/' + unit.uuid for unit in self.units])
    for unit in self.units:
      unit_uri = 'https://calvoritmo.com/tfm/data/triplegen/' + unit.uuid
      statement_uris = []
      ttlg.addTriple(unit_uri, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'https://calvoritmo.com/tfm/datamodel/triplegen/Unit')
      ttlg.setLiteral(unit_uri, 'https://calvoritmo.com/tfm/datamodel/triplegen/hasEvidence', unit.evidence)
      ttlg.setLiteral(unit_uri, 'https://calvoritmo.com/tfm/datamodel/triplegen/hasDescription', unit.description)
      for statement in unit.statements:
        statement_uri = 'https://calvoritmo.com/tfm/data/triplegen/' + getuuid()
        ttlg.addTriple(statement_uri, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement')
        ttlg.addTriple(statement_uri, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#subject', statement[0])
        ttlg.addTriple(statement_uri, 'http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate', statement[1])
        if statement[2][0] == '<':
          ttlg.addTriple(statement_uri,'http://www.w3.org/1999/02/22-rdf-syntax-ns#object', statement[2])
        else:
          ttlg.setLiteral(statement_uri,'http://www.w3.org/1999/02/22-rdf-syntax-ns#object', statement[2]) 
        statement_uris = statement_uris + [statement_uri]
      ttlg.updateList(unit_uri, 'https://calvoritmo.com/tfm/datamodel/triplegen/hasStatements', statement_uris)
    return ttlg
    
  def exportJSON(self):
    units = []
    for unit in self.units:
      units = units + [{
                        'evidence' : unit.evidence,
                        'description' : unit.description,
                        'statements'  : [list(s) for s in unit.statements]
                      }]
    return {'friendlyName' : self.friendlyName,
            'units'        : units}
    
  def importJSON(self, json_dict):
    if len(json_dict['units']) == len(self.units):
      for i in range(len(json_dict['units'])):
        self.units[i].evidence = json_dict['units'][i]['evidence']
        self.units[i].description = json_dict['units'][i]['description']
    return self

class TriplegenFactory:
  def delete(uuid):
    if os.path.isfile(f'data/triplegen/{uuid}.ttl'):
      os.remove(f'data/triplegen/{uuid}.ttl')
  def register():
    pass

# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
"""
Its scope is a full UL item, preceded by 'T types:'
It generates a bag of RDF statements.

If UL H parent contains any of ["type", "types", "category", "categories"]:
  For each entity, generate T -skos:narrower-> entity (through skos bag)

Given ent_i, T generate "{{ent_i.label@en}},{{}}and{{}} are kinds of {{T.label@en}}"
"""
class Alpha:
  def generate(nerdStage, groundTruth, openie_client = None):
    units = []
    for ul in nerdStage.mainSection.lists():

      subject = ul.parent.topLevelParent.title
      heading = ul.parent.title

      if set(["type", "types", "category", "categories"]).intersection(set(heading.lower().split(' '))) == set():
        continue
      
      individuals = []    
      for text in ul.texts():
        if text._annotations == []:
          continue
        else:
          individuals = individuals + [next(text.annotations())]
      if individuals == []:
        continue
        
      target_uri = f'<https://calvoritmo.com/tfm/entity/{getuuid()}>'
      statements = []
      for individual in individuals:
        statements = statements + [('<http://dbpedia.org/resource/'+urllib.parse.quote(subject)+'>', '<http://www.w3.org/2004/02/skos/core#narrower>', '<'+individual.uri+'>')]
        statements = statements + [('<'+individual.uri+'>', '<http://www.w3.org/2000/01/rdf-schema#label>', individual.surface)]
      evidence = subject + ': ' + heading + '\n'
      for text in ul.texts():
        evidence = evidence + text.text + '\n'
      description = f"{', '.join([ann.surface for ann in individuals])} are kinds of {subject}."
      evidence = evidence if type(evidence) == str else evidence.decode('utf-8')
      description = description if type(description) == str else description.decode('utf-8')
      units = units + [Triplegen.Unit(evidence, statements, description)]
    triplegenStage = Triplegen()
    triplegenStage.parentStage = 'https://calvoritmo.com/tfm/data/nerd/'+nerdStage.uuid
    triplegenStage.units = units
    return triplegenStage
    

# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
"""
Its scope is a LI element
It generates a single statement

Relation extraction (ent1, r, ent2): if ['is'] in r:
  ent1 a ent2.
  
Given ent1, ent2 generate "{{ent1.label}} is a {{ent2.label}}"
"""
class Beta:
  def generate(nerdStage, groundTruth, openie_client = None):
    units = []
    client = openie_client
    for ul in nerdStage.mainSection.lists():
      for li in ul.texts():
        if len(li._annotations) < 2:
          continue
        # print('Lets annotate')
        # print(li.text)
        triples = client.annotate(li.text)
        # print(triples)
        for i in range(len(li._annotations)-1):
          for triple in triples:
            # print(li._annotations[i].surface + '-------' + triple['subject'])
            if li._annotations[i].surface != triple['subject']:
              continue
            for j in range(i+1, len(li._annotations)):
              # print(li._annotations[j].surface + '-------' + triple['object'])
              if li._annotations[j].surface == triple['object']:
                # yield!!
                if triple['relation'].lower() not in ['is', 'are']:
                  continue
                evidence = li.text
                statements = [(li._annotations[i].uri, '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>', li._annotations[j].uri),
                (li._annotations[i].uri, '<http://www.w3.org/2000/01/rdf-schema#label>', li._annotations[i].surface),
                (li._annotations[j].uri, '<http://www.w3.org/2000/01/rdf-schema#label>', li._annotations[j].surface)]
                description = f'{triple["subject"]} is a {triple["object"]}'
                evidence = evidence if type(evidence) == str else evidence.decode('utf-8')
                description = description if type(description) == str else description.decode('utf-8')
                units = units + [Triplegen.Unit(evidence, statements, description)]
    triplegenStage = Triplegen()
    triplegenStage.parentStage = 'https://calvoritmo.com/tfm/data/nerd/'+nerdStage.uuid
    triplegenStage.units = units
    return triplegenStage


# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
"""
Its scope is a full UL with its parent Header and Title. 'Title: Heading\nSents'
Generates a statement bag

If a prefix from parent heading is article or redirect:
  T skos:related N
  H skos:narrower N
  N rdfs:label H.label
  N skos:narrower Bag skos:member ent_i

Given T, H, ent_i generate "{{T.label}} is related to the following {{H.label}}: {{ent_i.label}}"
"""
class Gamma:
  def generate(nerdStage, groundTruth, openie_client = None):
    units = []
    
    for ul in nerdStage.mainSection.lists():

      subject = ul.parent.topLevelParent.title
      target_concept = ul.parent.title.split(' ')[0]
      results = groundTruth.getTriples(s='http://dbpedia.org/resource/'+target_concept, p='http://www.w3.org/2000/01/rdf-schema#label')
      if results != []:
        concept = results[0][0]
      else:
        results = groundTruth.getTriples(s='http://dbpedia.org/resource/'+target_concept, p='http://dbpedia.org/ontology/wikiPageRedirects')
        if results != []:
          concept = results[0][2] 
        else:
          continue
      individuals = []    
      for text in ul.texts():
        if text._annotations == []:
          continue
        else:
          individuals = individuals + [next(text.annotations())]
      if individuals == []:
        continue

      target_uri = f'<https://calvoritmo.com/tfm/entity/{getuuid()}>'
      statements = [('<http://dbpedia.org/resource/'+urllib.parse.quote(subject)+'>', '<http://www.w3.org/2004/02/skos/core#related>', target_uri ),
                     ('<http://dbpedia.org/resource/'+target_concept+'>', '<http://www.w3.org/2004/02/skos/core#narrower>', target_uri ),
                     (target_uri, '<http://www.w3.org/2000/01/rdf-schema#label>', f'{target_concept} of {subject}')]
      for individual in individuals:
          statements = statements + [(target_uri, '<http://www.w3.org/2004/02/skos/core#narrower>', individual.uri)]
          statements = statements + [(individual.uri, '<http://www.w3.org/2000/01/rdf-schema#label>', individual.surface)]
          pass
      evidence = subject + ': ' + ul.parent.title + '\n'
      for text in ul.texts():
        evidence = evidence + text.text + '\n'
      description = f"{subject} is related to the following {target_concept}: {', '.join([ann.surface for ann in individuals])}."
      evidence = evidence if type(evidence) == str else evidence.decode('utf-8')
      description = description if type(description) == str else description.decode('utf-8')
      units = units + [Triplegen.Unit(evidence, statements, description)]
    triplegenStage = Triplegen()
    triplegenStage.parentStage = 'https://calvoritmo.com/tfm/data/nerd/'+nerdStage.uuid
    triplegenStage.units = units
    return triplegenStage
    
# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
"""
properties = {
    'openie.affinity_probability_cap': 2 / 3,
}
with StanfordOpenIE(properties=properties) as client:
    text = 'temperature and pressure are sufficient for nuclear fusion to occur.'
    print('Text: %s.' % text)
    for triple in client.annotate(text):
        print('|-', triple)
>> triple == {'subject': '', 'relation': '', 'object': ''}


Its scope is a single LI
It generates a single statement

Relation extraction (ent1, text, ent2):
   ent1 skos:related ent2.
   
Given ent1, ent2: generate "{{ent1.label}} is related to {{ent2.label}}"
"""
class Delta:
  def generate(nerdStage, groundTruth, openie_client = None):
    units = []
    client = openie_client
    for ul in nerdStage.mainSection.lists():
      for li in ul.texts():
        if len(li._annotations) < 2:
          continue
        # print('Lets annotate')
        # print(li.text)
        triples = client.annotate(li.text)
        # print(triples)
        for i in range(len(li._annotations)-1):
          for triple in triples:
            # print(li._annotations[i].surface + '-------' + triple['subject'])
            if li._annotations[i].surface != triple['subject']:
              continue
            for j in range(i+1, len(li._annotations)):
              # print(li._annotations[j].surface + '-------' + triple['object'])
              if li._annotations[j].surface == triple['object']:
                # yield!!
                evidence = li.text
                statements = [(li._annotations[i].uri, '<http://www.w3.org/2004/02/skos/core#related>', li._annotations[j].uri),
                (li._annotations[i].uri, '<http://www.w3.org/2000/01/rdf-schema#label>', li._annotations[i].surface),
                (li._annotations[j].uri, '<http://www.w3.org/2000/01/rdf-schema#label>', li._annotations[j].surface)]
                description = f'{triple["subject"]} is related to {triple["object"]}'
                evidence = evidence if type(evidence) == str else evidence.decode('utf-8')
                description = description if type(description) == str else description.decode('utf-8')
                units = units + [Triplegen.Unit(evidence, statements, description)]
    triplegenStage = Triplegen()
    triplegenStage.parentStage = 'https://calvoritmo.com/tfm/data/nerd/'+nerdStage.uuid
    triplegenStage.units = units
    return triplegenStage
    
# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
"""
Its scope is a full UL item preceded by a title.
It generates a single RDF statement.

For each entity add all r to the relation collection, where (title -r-> entity).
  For each entity and r, generate title -r-> entity
  
Given Title,UL, (Title -r-> Entity), generate:
"{{Title.rdfs:label@en}} has {{Entity.rdfs:label@en}} as {{r.rdfs:label@en}}"
"""
class Epsilon:
  def generate(nerdStage, groundTruth, openie_client = None):
    article = 'http://dbpedia.org/resource/' + urllib.parse.quote(nerdStage.mainSection.title)
    units = []
    for ul in nerdStage.mainSection.lists():

      subject = ul.parent.topLevelParent.title
 
      individuals = []    
      for text in ul.texts():
        if text._annotations == []:
          continue
        else:
          individuals = individuals + [next(text.annotations())]
      if individuals == []:
        continue
      
      rels = []
      for individual in individuals:
        rels = rels + [f'<{it[1]}>' for it in groundTruth.getTriples(s=article, o=individual.uri)]
        
      labels = []
      for rel in rels:
        l = groundTruth.getTriple(s=rel,p='<http://www.w3.org/2000/01/rdf-schema#label>')
        if l != None and len(l) > 0:
          l = l[1]
        labels = labels + [l]
      #labels = [groundTruth.getTriple(s=rel,p='<http://www.w3.org/2000/01/rdf-schema#label>')[1] for rel in rels]


      evidence = subject + '\n'
      for text in ul.texts():
        evidence = evidence + text.text + '\n'
      
      for rel, label in zip(rels, labels):
        if label == None:
          continue
        for individual in individuals:
          description = f"{subject} has {individual.surface} as {label}."

          statements = [('<http://dbpedia.org/resource/'+urllib.parse.quote(subject)+'>', f'{rel}', f'<{individual.uri}>' ),
                     (f'<{individual.uri}>', '<http://www.w3.org/2000/01/rdf-schema#label>', individual.surface)]      

          evidence = utf8(evidence)
          description = utf8(description)
          units = units + [Triplegen.Unit(evidence, statements, description)]
    triplegenStage = Triplegen()
    triplegenStage.parentStage = 'https://calvoritmo.com/tfm/data/nerd/'+nerdStage.uuid
    triplegenStage.units = units
    return triplegenStage
    
# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
"""
Its scope is a single LI
It generates a single statement

Relation extraction (ent1, text, ent2):
    S a rdf:Statement.
S zeta:kindOfRelation text.
S = ent1 skos:related ent2.

Given ent1, ent2, text: generate "{{text}} is a relation between {{ent1.label}} and {{ent2.label}}"
"""
class Zeta:
  def generate(nerdStage, groundTruth, openie_client = None):
    units = []
    client = openie_client
    for ul in nerdStage.mainSection.lists():
      for li in ul.texts():
        if len(li._annotations) < 2:
          continue
        # print('Lets annotate')
        # print(li.text)
        triples = client.annotate(li.text)
        # print(triples)
        for i in range(len(li._annotations)-1):
          for triple in triples:
            # print(li._annotations[i].surface + '-------' + triple['subject'])
            if li._annotations[i].surface != triple['subject']:
              continue
            for j in range(i+1, len(li._annotations)):
              # print(li._annotations[j].surface + '-------' + triple['object'])
              if li._annotations[j].surface == triple['object']:
                # yield!!
                evidence = li.text
                new_statement = f'<https://calvoritmo.com/tfm/entity/{getuuid()}>'
                statements = [(new_statement, '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>', '<http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement>'),
                (new_statement, '<http://www.w3.org/1999/02/22-rdf-syntax-ns#subject>', li._annotations[i].uri),
                (new_statement, '<http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate>', '<http://www.w3.org/2004/02/skos/core#related>'),
                (new_statement, '<http://www.w3.org/1999/02/22-rdf-syntax-ns#object>', li._annotations[j].uri),
                (new_statement, '<https://calvoritmo.com/tfm/ontogen/zeta/kindOfRelation>', triple['relation']),
                (li._annotations[i].uri, '<http://www.w3.org/2000/01/rdf-schema#label>', li._annotations[i].surface),
                (li._annotations[j].uri, '<http://www.w3.org/2000/01/rdf-schema#label>', li._annotations[j].surface)]
                description = f'The relation "{triple["relation"]}" holds between {triple["subject"]} and {triple["object"]}'
                evidence = evidence if type(evidence) == str else evidence.decode('utf-8')
                description = description if type(description) == str else description.decode('utf-8')
                units = units + [Triplegen.Unit(evidence, statements, description)]
    triplegenStage = Triplegen()
    triplegenStage.parentStage = 'https://calvoritmo.com/tfm/data/nerd/'+nerdStage.uuid
    triplegenStage.units = units
    return triplegenStage

class TriplegenStage:

  def __init__(self, ttl=None, uuid=None):
    self.g = rdflib.Graph()
    if ttl == None:
      self.g.parse(data='@base <http://app.internal/> . ')
    else:
      self.g.parse(data=ttl, format='ttl')
    if uuid == None:
      self.uuid = getuuid()
    else:
       self.uuid = uuid
  
  def load(uuid):
    with open(f'data/triplegen/{uuid}.ttl', 'r', encoding='utf-8') as f:
      content = f.read()
    return TriplegenStage(ttl=content, uuid=uuid)
    
  def save(self, uuid=None):
    if uuid == None:
      uuid = self.uuid
    with open(f'data/triplegen/{uuid}.ttl', 'w', encoding='utf-8') as f:
      f.write(str(self))
    return self
  
  def delete(self):
    TriplegenFactory.delete(self.uuid)
  
  def edit(self, content, inplace=False):
    if not inplace:      
      self.uuid = getuuid()

    self.g = rdflib.Graph()
    self.g.parse(data=content, format='ttl')
    return self
  
  
  def __str__(self): # --> ttl
    return self.g.serialize(format="ttl")
    
  def flatten(self, bag=None):
    if bag == None:
        statements = list(self.g.query(
        "SELECT ?x ?y ?z WHERE { "
        "    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> ?x .   "
        "    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> ?y . "
        "    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> ?z . }  "    
        ))
    else:
        statements = list(self.g.query(
        "SELECT ?x ?y ?z WHERE { "
        "    <"+bag+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#li> ?s . "
        "    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> ?x .   "
        "    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> ?y . "
        "    ?s <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> ?z . }  "    
        ))
    triplegenStage = TriplegenStage()
    for it in statements:
      triplegenStage.insert_triple(it)
    return triplegenStage

  def include_statement(self, s, p, o, bag):
    #text = text.encode("ascii", "ignore").decode().replace('\n', ' ')
    query =  u"INSERT DATA { <"+bag+"> <http://www.w3.org/1999/02/22-rdf-syntax-ns#li> [" + \
             u" <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement> ;" + \
             u"   <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> " + s + u"; " + \
             u"   <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> " + p + u"; " + \
             u"   <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> " + o + u" " + \
             u" ] . }"
    self.g.update(query)

  def get_bags(self):
    return [ it[0].n3()[1:-1] for it in self.g.query(
    "SELECT ?x WHERE { "
    "    ?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag> . }  "    
    )]
  
  def get_bag_evidence(self, bag):
    return list(self.g.query(
    "SELECT ?x WHERE { "
    f" <{bag}> <http://app.internal/m/evidence> ?x . ""}  "    
    ))[0][0].n3()[1:-1]
    
  def get_bag_description(self, bag):
    return list(self.g.query(
    "SELECT ?x WHERE { "
    f" <{bag}>    <http://app.internal/m/description> ?x. "" }  "    
    ))[0][0].n3()[1:-1]
  
  def insert_bag(self,bag_uri, bag_evidence, bag_description):
    query =  "INSERT DATA { <"+ bag_uri +">" + \
             " <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Bag> ;" + \
             "   <http://app.internal/m/evidence> \"\"\"" +  bag_evidence + "\"\"\" ; " + \
             "  <http://app.internal/m/description> \"\"\"" +  bag_description + "\"\"\"  . }"
    self.g.update(query)
    
  def intersect_create(self, ttl):
    statements = TriplegenStage(ttl)
    for triple in statements.g:
      if not self.check_triple(triple):
        self.insert_statement(triple)
    for triple in self.flatten():
      if not statements.check_triple(triple):
        self.remove_statement(triple)
    return self

  def check_triple(self, triple):
    return list(self.g.query("  ASK WHERE { "
       f" {triple[0].n3()} {triple[1].n3()} {triple[2].n3()} . "+"}"))[0]      

  def insert_triple(self, triple):
    query =  u"INSERT DATA { " + triple[0].n3() + u" " + triple[1].n3() + u" " + triple[2].n3() + u"  . }"
    self.g.update(query)
    
  def remove_statement(self, triple):
    self.g.update("DELETE WHERE {  "
        f"?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> {triple[0].n3()} ."
        f"?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> {triple[1].n3()} ."
        f"?x <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> {triple[2].n3()} ."
        "?x ?y ?z . }")
        
  def insert_statement(self, triple): 
  #  query =  u"INSERT DATA { [" + \
  #           u" <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement> ;" + \
  #           u"   <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> " + triple[0].n3() + u"; " + \
  #           u"   <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> " + triple[1].n3() + u"; " + \
  #           u"   <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> " + triple[2].n3() + u" " + \
  #           u" ] <http://app.internal/m/text> \"\"\"" +  "Manually added" + u"\"\"\"  }"
  #  g.update(query)
    self.add_statement(triple[0].n3(), triple[1].n3(), triple[2].n3(), 'Manually added', 'Manually added')
    
  def add_statement(self, s, p, o, evidence, description):
    #text = text.encode("ascii", "ignore").decode().replace('\n', ' ')
    query =  u"INSERT DATA { [" + \
             u" <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/02/22-rdf-syntax-ns#Statement> ;" + \
             u"   <http://www.w3.org/1999/02/22-rdf-syntax-ns#subject> " + s + u"; " + \
             u"   <http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate> " + p + u"; " + \
             u"   <http://www.w3.org/1999/02/22-rdf-syntax-ns#object> " + o + u" " + \
             u" ] <http://app.internal/m/evidence> \"\"\"" +  evidence + u"\"\"\"  ; " + \
             u"   <http://app.internal/m/description> \"\"\"" +  description + u"\"\"\" . }"
    self.g.update(query)

"""
class Epsilon:
  def __init__(self, graphRefinement=None):
    if graphRefinement == None:
      self.graph = graph.GraphRefinement()
    else:
      self.graph = graphRefinement
      
  def generate(self, nerdStage):
    res = TriplegenStage()
    article = 'http://dbpedia.org/resource/' + nerdStage.b.contents[0].text
    spans = nerdStage.get_spans(nerdStage.b)
    
    k = 0
    rels = []
    objects = []
    for i, tag in enumerate(nerdStage.b.contents):
        if tag.name != 'ul':
          text = nerdStage.render_span(k)
          for rel in rels:
            for obj in objects:
              bag_uri = get_uri(subgraph='b')
              res.insert_bag(bag_uri, text, text)
              res.include_statement(f'<{article}>', f'<{rel}>', f'<{obj}>', bag_uri)
          if rels != [] and objects != []:
            k = k+1    
          rels = []
          objects = []
          
          continue
          
        for j, t in enumerate(tag.find_all('li')):
          sp = spans[i][j]
          if sp == []:
            continue
          first_sp = sorted(sp, key=lambda it: it['start'])[0]
          rels = rels + [b for a,b,c in self.graph.getTriples(s=f'<{article}>', o=f'<{first_sp["uri"]}>')]
          objects = objects + [first_sp["uri"]]
          
    text = nerdStage.render_span(k)    
    for rel in rels:
        for obj in objects:
              bag_uri = get_uri(subgraph='b')
              res.insert_bag(bag_uri, text, text)
              res.include_statement(f'<{article}>', f'<{rel}>', f'<{obj}>', bag_uri)
    return res
"""


