from SPARQLWrapper import SPARQLWrapper, JSON
import rdflib
import os
from app.utils import *

class TurtleGraph:
    def __init__(self, filename=None):
        self.g = rdflib.Graph()
        
        if filename != None:
            self.g.parse(source=filename)
            self.nsm = self.g.namespace_manager # .compute_qname(str)
        else:
            self.nsm = self.g.namespace_manager
      
    def save(self, filename):
        self.g.serialize(destination=filename, format='ttl')

    def __str__(self):
        return self.g.serialize(format="ttl")    

    # Returns a list that is either given as URI or specified
    #  by a subject and predicate URI
    # expects listUri as string (either "uri" or "<uri>") or URIRef
    # if relUri is specified, it can also be either string or URIRef
    # returns a "uri" string
    def getList(self, listUri, relUri=None):
      if type(listUri) != rdflib.term.URIRef:   # if listUri is a string
        if listUri[0] == '<' and listUri[-1] == '>':
          listUri = listUri[1:-1]
        listUri = rdflib.URIRef(listUri)
      # at this point listUri has to be an URIRef
      
      if relUri == None:
        pass
      else:
        if type(relUri) != rdflib.term.URIRef:   # if relUri is a string
          if relUri[0] == '<' and relUri[-1] == '>':
            relUri = relUri[1:-1]
          relUri = rdflib.URIRef(relUri)
          # at this point relUri has to be an URIRef
        if not (listUri, relUri, None) in self.g:
          return []
        listUri = next(self.g.triples((listUri, relUri, None)))[2] 
        # at this point listUri is either an URIRef or BNode (specified by subject and predicate)        
      
      res = []
      while listUri != rdflib.RDF+"nil":
        if (listUri, rdflib.RDF+"type", rdflib.RDF+"List") not in self.g:
          return res
      
        # listUri is a non-empty list, so we assume it has both rdf:first and rdf:rest
        res = res + [next(self.g.triples((listUri, rdflib.RDF+"first", None)))[2].n3()[1:-1]]
        listUri = next(self.g.triples((listUri, rdflib.RDF+"rest", None)))[2]
      return res

    # listUri and relUri can be either "<uri>", "uri" or URIRef
    # l is a list that may contain either "<uri>", "uri" or URIRef
    def updateList(self, listUri, relUri, l):
      if type(listUri) != rdflib.term.URIRef:   # if listUri is a string
        if listUri[0] == '<' and listUri[-1] == '>':
          listUri = listUri[1:-1]
        listUri = rdflib.URIRef(listUri)
      # at this point listUri has to be an URIRef
      
      if type(relUri) != rdflib.term.URIRef:   # if relUri is a string
        if relUri[0] == '<' and relUri[-1] == '>':
          relUri = relUri[1:-1]
        relUri = rdflib.URIRef(relUri)
        # at this point relUri has to be an URIRef
      
      if len(list(self.g.triples((listUri, relUri, None)))) > 0:      
        bnode = next(self.g.triples((listUri, relUri, None)))[2] # assumes there is exactly one bnode as List
      
        while bnode != rdflib.RDF+'nil':
          self.g.remove((None, None, bnode))        
          bnode_next = next(self.g.triples((bnode, rdflib.RDF+'rest', None)))[2] # assumes there is exactly one bnode as List
          self.g.remove((bnode, None, None))
          bnode = bnode_next
      
        self.g.remove((None, None, bnode))
      
      
      if l == []:
        self.g.add((listUri, relUri, rdflib.RDF+'nil'))
      else:
        it = l[0]
        if type(it) != rdflib.term.URIRef:
          if it[0] == '<' and it[-1] == '>':
            it = it[1:-1]
          it = rdflib.URIRef(it)
        bnode = rdflib.term.BNode()
        self.g.add((listUri, relUri, bnode))
        self.g.add((bnode, rdflib.RDF+'type', rdflib.RDF+'List'))
        self.g.add((bnode, rdflib.RDF+'first', it)) 
      
        for it in l[1:]:
          if type(it) != rdflib.term.URIRef:
            if it[0] == '<' and it[-1] == '>':
              it = it[1:-1]
            it = rdflib.URIRef(it)
        
          bnode_next = rdflib.term.BNode()
          self.g.add((bnode, rdflib.RDF+'rest', bnode_next))
          bnode = bnode_next
          self.g.add((bnode, rdflib.RDF+'type', rdflib.RDF+'List'))
          self.g.add((bnode, rdflib.RDF+'first', it))
        
        self.g.add((bnode, rdflib.RDF+'rest', rdflib.RDF+'nil'))


    # Accepts s, p and o as "<uri>", "uri" or URIRef
    # At least one must be provided
    # Returns [("uri", "uri", "uri")]
    def getTriples(self, s=None, p=None, o=None):
      assert s == None or p == None or o == None

      if s != None:
        if type(s) != rdflib.term.URIRef:
          if s[0] == '<':
            s = rdflib.term.URIRef(s[1:-1])
          else:
            s = rdflib.term.URIRef(s)
      if p != None:
        if type(p) != rdflib.term.URIRef:
          if p[0] == '<':
            p = rdflib.term.URIRef(p[1:-1])
          else:
            p = rdflib.term.URIRef(p)
      if o != None:
        if type(o) != rdflib.term.URIRef:
          if o[0] == '<':
            o = rdflib.term.URIRef(o[1:-1])
          else:
            o = rdflib.term.URIRef(o)
      
      res = []
      
      for triple in self.g.triples((s,p,o)):
        t = [None, None, None]
        if type(triple[2]) == rdflib.term.URIRef:
          t[2] = triple[2].n3()[1:-1]
        else:
          if len(str(triple[2])) > 0 and str(triple[2])[0] == '"':
            t[2] = str(triple[2])[1:-1]
          else:
            t[2] = str(triple[2])
        t[1] = triple[1].n3()[1:-1]
        t[0] = triple[0].n3()[1:-1]
        res = res + [tuple(t)]
      
      return res

    # Accepts s, p and o as "<uri>", "uri" or URIRef
    # At least one must be provided
    # Assumes only one result will match    
    # Returns ("uri", "uri", "uri")
    def getTriple(self, s=None, p=None, o=None):
      res = self.getTriples(s,p,o)
      assert len(res) == 1
      return res[0]
    
    # Accepts s, p and o as "<uri>", "uri" or URIRef
    # The object cannot be a literal (use setLiteral instead)
    def addTriple(self, s, p, o):
       if type(s) != rdflib.term.URIRef:
          if s[0] == '<':
            s = rdflib.term.URIRef(s[1:-1])
          else:
            s = rdflib.term.URIRef(s)
       if type(p) != rdflib.term.URIRef:
         if p[0] == '<':
           p = rdflib.term.URIRef(p[1:-1])
         else:
           p = rdflib.term.URIRef(p)
       if type(o) != rdflib.term.URIRef:
        if o[0] == '<':
          o = rdflib.term.URIRef(o[1:-1])
        else:
          o = rdflib.term.URIRef(o)
       self.g.add((s,p,o))
    
    # Accepts s and p as "<uri>", "uri" or URIRef
    # Accepts v as str, int or Literal
    def setLiteral(self, s, p, v):
      if type(s) != rdflib.term.URIRef:
          if s[0] == '<':
            s = rdflib.term.URIRef(s[1:-1])
          else:
            s = rdflib.term.URIRef(s)
      if type(p) != rdflib.term.URIRef:
          if p[0] == '<':
            p = rdflib.term.URIRef(p[1:-1])
          else:
            p = rdflib.term.URIRef(p)
      if type(v) != rdflib.term.Literal:
        v = rdflib.term.Literal(v)
        
      self.g.remove((s,p,None))
      self.g.add((s,p,v))
      

class GroundTruth:
  def __init__(self, filename=None, parent=None):
    self.ttlg = TurtleGraph(filename=filename)
  
  def getTriple(self, s=None, p=None, o=None):
    return self.getTriples(s=s, p=p, o=o)[0]
    
  def getTriples(self, s=None, p=None, o=None):
    res = self.ttlg.getTriples(s=s, p=p, o=o)
    if parent != None:
      res = res + parent.getTriples(s=s, p=p, o=o)
    return res
  
  def importJSON(self, json_dict):
    self.ttlg=TurtleGraph()
    for stm in json_dict['statements']:
      s = stm['s'][1:-1] if stm['s'][0] == '"' and stm['s'][-1] == '"' else stm['s']
      p = stm['p'][1:-1] if stm['p'][0] == '"' and stm['p'][-1] == '"' else stm['p']
      o = stm['o'][1:-1] if stm['o'][0] == '"' and stm['o'][-1] == '"' else stm['o']
      s = rdflib.term.URIRef(s[1:-1]) if s[0] == '<' and s[-1] == '>' else rdflib.term.Literal(s)
      p = rdflib.term.URIRef(p[1:-1]) if p[0] == '<' and p[-1] == '>' else rdflib.term.Literal(p)
      o = rdflib.term.URIRef(o[1:-1]) if o[0] == '<' and o[-1] == '>' else rdflib.term.Literal(o)
      self.ttlg.g.add((s,p,o))
    return self
    
  def exportJSON(self):
    statements = []
    for triple in self.ttlg.g.triples((None, None, None)):
      statement = {}
      statement['s'] = triple[0].n3()
      statement['p'] = triple[1].n3()
      statement['o'] = triple[2].n3()
      statements = statements + [statement]
    return {'statements' : statements}
  
  def dbpedia_kb():
    class DBpedia_kb:
      def __init__(self):
        pass
    
      def getTriple(self, s=None, p=None, o=None):
        self.getTriples(s=s, p=p, o=o)[0]
        
      def getTriples(self, s=None, p=None, o=None):
          assert s == None or p == None or o == None

          if s != None and s[0] != '<':
            s = '<' + s + '>'
          if p != None and p[0] != '<':
            p = '<' + p + '>'
          if o != None and o[0] != '<':
            o = '<' + o + '>'

          select_x = " ?x" if s == None else ""
          select_y = " ?y" if p == None else ""
          select_z = " ?z" if o == None else ""

          where_x = "?x" if s == None else s
          where_y = "?y" if p == None else p
          where_z = "?z" if o == None else o
          
          query = (
             "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n"
            f"SELECT{select_x}{select_y}{select_z} ""\n"
             "WHERE { "f"{where_x} {where_y} {where_z}"" }\n"
            )

          sparql = SPARQLWrapper("http://dbpedia.org/sparql")

          sparql.setQuery(query)
          sparql.setReturnFormat(JSON)
          results = sparql.query().convert()["results"]["bindings"]

          if s == None:
            res_x = [f"{it['x']['value']}" if it['x']['type'] == 'uri' 
                     else it['x']['value'] for it in results]
          else:
            res_x = [s[1:-1]] * len(results)
              
          if p == None:
            res_y = [f"{it['y']['value']}" if it['y']['type'] == 'uri' 
                     else it['y']['value'] for it in results]
          else:
            res_y = [p[1:-1]] * len(results)
                
          if o == None:
            res_z = [f"{it['z']['value']}" if it['z']['type'] == 'uri' 
                     else it['z']['value'] for it in results]
          else:
            res_z = [o[1:-1]] * len(results)

          return list(zip(res_x, res_y, res_z))
    
    return DBpedia_kb()


class GraphFactory:
  def delete(uuid):
    if os.path.isfile(f'data/grefinement/{uuid}.ttl'):
      os.remove(f'data/grefinement/{uuid}.ttl')

class GraphRefinement:
    def __init__(self, ttl=None, dbpedia=True, uuid=None):
        if uuid == None:
          self.uuid = getuuid()
        else:
          self.uuid = uuid
        self.dbpedia = dbpedia
        self.g = rdflib.Graph()
        if ttl == None:
          self.g.parse(data='@base <http://app.internal/> . ')
        else:
          self.g.parse(data='@base <http://app.internal/> . '+ttl, format='ttl')
      
    def load(uuid, dbpedia=True):
        with open(f'data/grefinement/{uuid}.ttl', 'r', encoding='utf-8') as f:
          content = f.read()
        return GraphRefinement(content, uuid=uuid, dbpedia=dbpedia)

    def save(self, uuid=None):
        if uuid == None:
          uuid = self.uuid
        with open(f'data/grefinement/{uuid}.ttl', 'w', encoding='utf-8') as f:
          f.write(str(self))
        return self

    def delete(self):
        GraphFactory.delete(self.uuid)

    def edit(self, content, inplace=False):
        if not inplace:      
          self.uuid = getuuid()
        self.g = rdflib.Graph()
        self.g.parse(data='@base <http://app.internal/> . '+content, format='ttl')
        return self

    def __str__(self): # --> ttl
        return self.g.serialize(format="ttl")

    # Returns a list that is either given as URI or specified
    #  by a subject and predicate URI
    # expects listUri as string (either "uri" or "<uri>") or URIRef
    # if relUri is specified, it can also be either string or URIRef
    # returns a "uri" string
    def getList(self, listUri, relUri=None):
      if type(listUri) != rdflib.term.URIRef:   # if listUri is a string
        if listUri[0] == '<' and listUri[-1] == '>':
          listUri = listUri[1:-1]
        listUri = rdflib.URIRef(listUri)
      # at this point listUri has to be an URIRef
      
      if relUri == None:
        pass
      elif type(relUri) != rdflib.term.URIRef:   # if relUri is a string
        if relUri[0] == '<' and relUri[-1] == '>':
          relUri = relUri[1:-1]
        relUri = rdflib.URIRef(relUri)
        # at this point relUri has to be an URIRef
        if not (listUri, relUri, None) in self.g:
          return []
        listUri = next(self.g.triples((listUri, relUri, None)))[2] 
        # at this point listUri is either an URIRef or BNode (specified by subject and predicate)        
      
      res = []
      while listUri != rdflib.RDF+"nil":
        if not (listUri, rdflib.RDF+"type", rdflib.RDF+"List") in self.g:
          return res
      
        # listUri is a non-empty list, so we assume it has both rdf:first and rdf:rest
        res = res + [next(self.g.triples((listUri, rdflib.RDF+"first", None)))[2].n3()[1:-1]]
        listUri = next(self.g.triples((listUri, rdflib.RDF+"rest", None)))[2]
      return res      
    
    def getTriples(self, s=None, p=None, o=None):
      assert s == None or p == None or o == None

      if s != None and s[0] != '<':
        s = '<' + s + '>'
      if p != None and p[0] != '<':
        p = '<' + p + '>'
      if o != None and o[0] != '<':
        o = '<' + o + '>'

      select_x = " ?x" if s == None else ""
      select_y = " ?y" if p == None else ""
      select_z = " ?z" if o == None else ""

      where_x = "?x" if s == None else s
      where_y = "?y" if p == None else p
      where_z = "?z" if o == None else o
      
      query = (
         "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \n"
        f"SELECT{select_x}{select_y}{select_z} ""\n"
         "WHERE { "f"{where_x} {where_y} {where_z}"" }\n"
        )

      res = []

      if self.dbpedia:

          sparql = SPARQLWrapper("http://dbpedia.org/sparql")

          sparql.setQuery(query)
          sparql.setReturnFormat(JSON)
          results = sparql.query().convert()["results"]["bindings"]

          if s == None:
            res_x = [f"{it['x']['value']}" if it['x']['type'] == 'uri' 
                     else it['x']['value'] for it in results]
          else:
            res_x = [s[1:-1]] * len(results)
            
          if p == None:
            res_y = [f"{it['y']['value']}" if it['y']['type'] == 'uri' 
                     else it['y']['value'] for it in results]
          else:
            res_y = [p[1:-1]] * len(results)
            
          if o == None:
            res_z = [f"{it['z']['value']}" if it['z']['type'] == 'uri' 
                     else it['z']['value'] for it in results]
          else:
            res_z = [o[1:-1]] * len(results)
            
          res = res + list(zip(res_x, res_y, res_z))
      
      for it in self.g.query(query):
        i = 0
        
        if s == None:
          it_x = it[i].n3()[1:-1]
          i = i + 1
        else:
          it_x = s[1:-1]
          
        if p == None:
          it_y = it[i].n3()[1:-1]          
          i = i + 1
        else:
          it_y = p[1:-1]          
          
        if o == None:
          it_z = it[i].n3()[1:-1]          
          i = i + 1
        else:
          it_z = o[1:-1]          
        
        res = res + [(it_x, it_y, it_z)]
      
      return res

    