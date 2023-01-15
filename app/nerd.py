import json
from bs4 import BeautifulSoup
import app.fetch as fetch
import app.graph as graph
import copy
import os
from app.utils import *

class Nerd:

  class Section:
    
    class Text:
    
      class Annotation:
        def __init__(self, surface, uri, start, end, source, uuid=None):
          self.surface = surface
          self.uri = uri
          self.start = int(start)
          self.end = int(end)
          self.source = source
          if uuid == None:
            self.uuid = getuuid()
          else:
            self.uuid = uuid
          
        def __hash__(self):
          return hash((self.surface, self.uri, self.start, self.end, self.source))
          
        def __eq__(self, other):
          return self.surface == other.surface and \
                 self.uri     == other.uri     and \
                 self.start   == other.start   and \
                 self.end     == other.end     and \
                 self.source  == other.source
          
          
      def __init__(self, parent, text, annotations=[], uuid=None):
        self.parent = parent
        self.text = text
        #------  TODO: if text have tags, fix them, ignore or raise exception?
        self._annotations = annotations
        if uuid == None:
          self.uuid = getuuid()
        else:
          self.uuid = uuid
       
      def _touch(self):
        self.uuid = getuuid()
        self.parent._touch()
        
      def appendAnnotation(self, annotation):
        self._annotations = self._annotations + [annotation]
        self._touch()
        return annotation
        
      def annotations(self):
        return self._annotations.__iter__()
      
    class UL:
      def __init__(self, parent, ul, uuid=None):
        self.parent = parent
        self.items = [Nerd.Section.Text(self, text) for text in ul]
        if uuid == None:
          self.uuid = getuuid()
        else:
          self.uuid = uuid
      
      def _touch(self):
        self.uuid = getuuid()
        self.parent._touch()
      
      # Accepts str
      # Assumes str is valid html text with only <a>, <b> and <i> labels      
      def appendText(self, text, annotations=[]):
        newText = Nerd.Section.Text(self, text, annotations)
        self.items = self.items + [newText]
        self._touch()
        return newText

      def texts(self):
        return self.items.__iter__()

    def __init__(self, parent, title="Untitled", uuid=None):
      self.parent = parent
      if type(self.parent) == Nerd:
        self.topLevelParent = self
      else:
        self.topLevelParent = self.parent.topLevelParent
      self.subsections = []
      self.title = title
      self.sectionItems = []
      self.depth = 0
      self.cursor = self
      if uuid == None:
        self.uuid = getuuid()
      else:
        self.uuid = uuid
    
    def _touch(self):
      self.uuid = getuuid()
      self.parent._touch()
    
    # Accepts [str]
    # Assumes str is valid html text with only <a>, <b> and <i> labels
    def appendUL(self, ul):
      self.resetCursor()
      s = self.cursor.sectionItems
      newUL = Nerd.Section.UL(self.cursor, ul)
      self.cursor.sectionItems = s + [newUL]
      self._touch()
      return newUL
       
    # Accepts str
    # Assumes str is valid html text with only <a>, <b> and <i> labels
    def appendText(self, text, annotations=[]):
      self.resetCursor()
      s = self.cursor.sectionItems
      newText = Nerd.Section.Text(self.cursor, text, annotations)
      self.cursor.sectionItems = s + [newText]
      self._touch()
      return newText
    
    def appendSection(self, title="Untitled"):
      newSection = Nerd.Section(self.cursor, title=title)
      self.cursor.subsections = self.cursor.subsections + [newSection]
      self.resetCursor()
      self._touch()
      return newSection
    
    def insertSection(self, title="Untitled"):
      self._touch()
      return self.resetCursor().appendSection(title=title)
    
    def drop(self):
      if type(self.parent) != Nerd.Section or self.parent == self:
        return
      idx = self.parent.subsections.index(self)
      if idx == -1:
        return
      self.parent.subsections = self.parent.subsections[:idx] + self.parent.subsections[idx+1:]      
      self.parent.resetCursor()
      self.parent._touch()
      self.parent = self
    
    def floatCursor(self):
      if self.cursor != self:
        self.cursor = self.cursor.parent
      return self
    
    def resetCursor(self):
      if self.subsections != []:
        self.subsections[-1].resetCursor()
        self.cursor = self.subsections[-1].cursor
      else:
        self.cursor = self
      return self
    
    def sections(self):
      rootSection = self
      class SectionIterator:
        def __iter__(self):
          self.index = 0
          self.pointer = [rootSection].__iter__()
          return self
          
        def __next__(self):
          try: 
            return next(self.pointer)
          except StopIteration:
            if self.index >= len(rootSection.subsections):
              raise StopIteration
            else:
              self.pointer = rootSection.subsections[self.index].sections().__iter__()
              self.index = self.index+1
          return next(self.pointer)
      return SectionIterator().__iter__()
    
    def lists(self):
      sections = self.sections()
      class ListIterator:
        def __iter__(self):
          self.index = 0
          self.pointer = sections.__iter__()
          self.section = None
          return self
          
        def __next__(self):
          while True:
            while self.section == None or len(self.section.sectionItems) <= self.index:
              self.section = next(self.pointer)
              self.index = 0
            if type(self.section.sectionItems[self.index]) == Nerd.Section.UL:
              self.index = self.index + 1
              return self.section.sectionItems[self.index-1]
            self.index = self.index + 1
      return ListIterator().__iter__()
      
    def texts(self):
      sections = self.sections()
      class TextIterator:
        def __iter__(self):
          self.section_index = 0
          self.pointer = sections.__iter__()
          self.section = None
          self.ul = None
          return self
          
        def __next__(self):
          if self.ul != None:
            try:
              return next(self.ul)
            except StopIteration:
              self.ul = None
          while self.section == None or len(self.section.sectionItems) <= self.section_index:
            self.section = next(self.pointer)
            self.section_index = 0
          item = self.section.sectionItems[self.section_index]
          self.section_index = self.section_index + 1
          if type(item) == Nerd.Section.Text:
            return item
          else: # Nerd.Section.UL
            self.ul = item.texts()
            return next(self.ul)
            
      return TextIterator().__iter__()
    
    def _touch(self):
      self.uuid = getuuid()
  
  def _buildAnnotations(self, ttlg, container, uri):
    annotations =  ttlg.getList(uri, 'https://calvoritmo.com/tfm/datamodel/nerd/hasAnnotations')
    for ann_uri in annotations:
        surface = ttlg.getTriple(s=ann_uri, p='https://calvoritmo.com/tfm/datamodel/nerd/hasSurface')[2]
        ent_uri = ttlg.getTriple(s=ann_uri, p='https://calvoritmo.com/tfm/datamodel/nerd/hasUri')[2]
        start = ttlg.getTriple(s=ann_uri, p='https://calvoritmo.com/tfm/datamodel/nerd/hasStart')[2]
        end = ttlg.getTriple(s=ann_uri, p='https://calvoritmo.com/tfm/datamodel/nerd/hasEnd')[2]
        source = ttlg.getTriple(s=ann_uri, p='https://calvoritmo.com/tfm/datamodel/nerd/hasSource')[2]
        
        container.appendAnnotation(Nerd.Section.Text.Annotation(surface, ent_uri, start, end, source, uuid=ann_uri.split('/')[-1]))
  
  def _buildText(self, ttlg, container, uri):
    plaintext =  ttlg.getTriple(s=uri, p='https://calvoritmo.com/tfm/datamodel/nerd/hasText')[2]
    text = container.appendText(plaintext)
    self._buildAnnotations(ttlg, text, uri)
    
  def _buildList(self, ttlg, section, uri):
    l = section.appendUL([])
    item_uris = ttlg.getList(uri, 'https://calvoritmo.com/tfm/datamodel/nerd/hasListItems')
    for item_uri in item_uris:
      self._buildText(ttlg, l, item_uri)
    
  def _buildSection(self, ttlg, section, uri):
    section.title = ttlg.getTriple(s=uri, p='https://calvoritmo.com/tfm/datamodel/nerd/hasTitle')[2]
    subsection_uris = ttlg.getList(uri, 'https://calvoritmo.com/tfm/datamodel/nerd/hasSubsections')
    item_uris = ttlg.getList(uri, 'https://calvoritmo.com/tfm/datamodel/nerd/hasSectionItems')
    
    for item_uri in item_uris:
      item_type = ttlg.getTriple(s=item_uri, p='http://www.w3.org/1999/02/22-rdf-syntax-ns#type')[2]
      if item_type == 'https://calvoritmo.com/tfm/datamodel/nerd/List':
        self._buildList(ttlg, section, item_uri)
      else: # item_type == 'https://calvoritmo.com/tfm/datamodel/nerd/Text'
        self._buildText(ttlg, section, item_uri)
        
    for section_uri in subsection_uris:
      new_section = section.appendSection()
      self._buildSection(ttlg, new_section, section_uri)
    
  def __init__(self, filename=None):
    self.uuid = getuuid()
    self.mainSection = Nerd.Section(self)
    self.friendlyName = "Nerd Stage"
    self.parentStage = 'https://calvoritmo.com/tfm/meta/bottom_stage'
    if filename != None:
      ttlg = graph.TurtleGraph(filename=filename)
      nerd_uri = ttlg.getTriple(p='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', o='https://calvoritmo.com/tfm/meta/Stage')[0]
      self.friendlyName = ttlg.getTriple(s=nerd_uri, p='https://calvoritmo.com/tfm/meta/stageFriendlyName')[2]
      mainSection_uri = ttlg.getTriple(s=nerd_uri, p='https://calvoritmo.com/tfm/datamodel/nerd/hasMainSection')[2]
      self._buildSection(ttlg, self.mainSection, mainSection_uri)
      self.uuid = nerd_uri.split('/')[-1]
  
  def _cloneText(fetch_text, parent):
    return Nerd.Section.Text(parent, BeautifulSoup(fetch_text.text, features="html.parser").text)
  
  def _cloneList(fetch_list, parent):
    ul = Nerd.Section.UL(parent, [])
    for text in fetch_list.texts():
      ul.appendText(BeautifulSoup(text.text, features="html.parser").text)
    return ul
  
  def _cloneSection(fetch_section, parent):
    section = Nerd.Section(parent)
    section.title = fetch_section.title
    
    for item in fetch_section.sectionItems:
      if type(item) == fetch.Fetch.Section.UL:
        section.sectionItems = section.sectionItems + [Nerd._cloneList(item, section)]      
      else: # type(item) == fetch.Fetch.Section.Text
        section.sectionItems = section.sectionItems + [Nerd._cloneText(item, section)]
    
    for f_subsection in fetch_section.subsections:
      section.subsections = section.subsections + [Nerd._cloneSection(f_subsection, section)]
    
    return section
    
  def cloneFetch(fetch):
    nerd = Nerd()
    nerd.friendlyName = fetch.friendlyName + ' - Nerd'
    nerd.parentStage = 'https://calvoritmo.com/tfm/data/fetch/'+fetch.uuid
    nerd.mainSection = Nerd._cloneSection(fetch.mainSection, nerd)    
    return nerd
    
  def _serializeSection(self, ttlg, section):
    ttlg.addTriple(  'https://calvoritmo.com/tfm/data/nerd/'+section.uuid, 
                     "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                     "https://calvoritmo.com/tfm/datamodel/nerd/Section")
    ttlg.setLiteral( 'https://calvoritmo.com/tfm/data/nerd/'+section.uuid,
                     'https://calvoritmo.com/tfm/datamodel/nerd/hasTitle',
                     section.title)
    sectionItems = []
    for item in section.sectionItems:
      if type(item) == Nerd.Section.UL:
        ttlg.addTriple( 'https://calvoritmo.com/tfm/data/nerd/'+item.uuid,
                        'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                        'https://calvoritmo.com/tfm/datamodel/nerd/List' )
        listItems = []
        for text in item.texts():
          listItems = listItems + ['https://calvoritmo.com/tfm/data/nerd/'+text.uuid]
          ttlg.addTriple( 'https://calvoritmo.com/tfm/data/nerd/'+text.uuid,
                          'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                          'https://calvoritmo.com/tfm/datamodel/nerd/ListItem' )
          ## Add annotations
          annotations = []
          for annotation in text.annotations():
            annotation_uri = 'https://calvoritmo.com/tfm/data/nerd/'+annotation.uuid
            annotations = annotations + [annotation_uri]
            ttlg.addTriple(annotation_uri,
                            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                            'https://calvoritmo.com/tfm/datamodel/nerd/Annotation')
                            
            ttlg.setLiteral(annotation_uri,
                            'https://calvoritmo.com/tfm/datamodel/nerd/hasUri',
                            annotation.uri)
            ttlg.setLiteral(annotation_uri,
                            'https://calvoritmo.com/tfm/datamodel/nerd/hasSurface',
                            annotation.surface)
            ttlg.setLiteral(annotation_uri,
                            'https://calvoritmo.com/tfm/datamodel/nerd/hasStart',
                            annotation.start)
            ttlg.setLiteral(annotation_uri,
                            'https://calvoritmo.com/tfm/datamodel/nerd/hasEnd',
                            annotation.end)
            ttlg.setLiteral(annotation_uri,
                            'https://calvoritmo.com/tfm/datamodel/nerd/hasSource',
                            annotation.source)
                            
          ttlg.updateList('https://calvoritmo.com/tfm/data/nerd/'+text.uuid,
                          'https://calvoritmo.com/tfm/datamodel/nerd/hasAnnotations',
                          annotations)
          ##
          ttlg.setLiteral( 'https://calvoritmo.com/tfm/data/nerd/'+text.uuid,
                           'https://calvoritmo.com/tfm/datamodel/nerd/hasText',
                            text.text  )
        ttlg.updateList( 'https://calvoritmo.com/tfm/data/nerd/'+item.uuid,
                         'https://calvoritmo.com/tfm/datamodel/nerd/hasListItems',
                         listItems)
      else:  # type(item) == Nerd.Section.Text
        ttlg.addTriple( 'https://calvoritmo.com/tfm/data/nerd/'+item.uuid,
                        'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                        'https://calvoritmo.com/tfm/datamodel/nerd/Text' )
        ## Add annotations
        annotations = []
        for annotation in item.annotations():
          annotation_uri = 'https://calvoritmo.com/tfm/data/nerd/'+annotation.uuid
          annotations = annotations + [annotation_uri]
          ttlg.addTriple(annotation_uri,
                          'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                          'https://calvoritmo.com/tfm/datamodel/nerd/Annotation')
                            
          ttlg.setLiteral(annotation_uri,
                          'https://calvoritmo.com/tfm/datamodel/nerd/hasUri',
                          annotation.uri)
          ttlg.setLiteral(annotation_uri,
                          'https://calvoritmo.com/tfm/datamodel/nerd/hasSurface',
                          annotation.surface)
          ttlg.setLiteral(annotation_uri,
                          'https://calvoritmo.com/tfm/datamodel/nerd/hasStart',
                          annotation.start)
          ttlg.setLiteral(annotation_uri,
                          'https://calvoritmo.com/tfm/datamodel/nerd/hasEnd',
                          annotation.end)
          ttlg.setLiteral(annotation_uri,
                          'https://calvoritmo.com/tfm/datamodel/nerd/hasSource',
                          annotation.source)
                            
        ttlg.updateList('https://calvoritmo.com/tfm/data/nerd/'+item.uuid,
                        'https://calvoritmo.com/tfm/datamodel/nerd/hasAnnotations',
                        annotations)
        ##                       
        ttlg.setLiteral('https://calvoritmo.com/tfm/data/nerd/'+item.uuid,
                        'https://calvoritmo.com/tfm/datamodel/nerd/hasText',
                        item.text  )
      sectionItems = sectionItems + ['https://calvoritmo.com/tfm/data/nerd/'+item.uuid]
    ttlg.updateList( 'https://calvoritmo.com/tfm/data/nerd/'+section.uuid,
                     'https://calvoritmo.com/tfm/datamodel/nerd/hasSectionItems',
                      sectionItems)
    subsections = []
    for subsection in section.subsections:
      subsections = subsections + ['https://calvoritmo.com/tfm/data/nerd/'+subsection.uuid]
      self._serializeSection(ttlg, subsection)
    ttlg.updateList( 'https://calvoritmo.com/tfm/data/nerd/'+section.uuid,
                     'https://calvoritmo.com/tfm/datamodel/nerd/hasSubsections',
                     subsections  )
  
  def asGraph(self):
    ttlg = graph.TurtleGraph()
    # 'https://calvoritmo.com/tfm/meta/hasGroundTruth'
    # 'https://calvoritmo.com/tfm/meta/hasParentStage'
    # 'https://calvoritmo.com/tfm/meta/hasBaseStage'
    # 'https://calvoritmo.com/tfm/meta/hasModel'
    ttlg.addTriple('https://calvoritmo.com/tfm/data/nerd/'+self.uuid,
                   'https://calvoritmo.com/tfm/meta/hasParentStage',
                   self.parentStage)

    ttlg.addTriple( 'https://calvoritmo.com/tfm/data/nerd/'+self.uuid,
                    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 
                    'https://calvoritmo.com/tfm/meta/Stage' )
    ttlg.setLiteral( 'https://calvoritmo.com/tfm/data/nerd/'+self.uuid, 
                     'https://calvoritmo.com/tfm/meta/stageFriendlyName', 
                     self.friendlyName )   
    ttlg.addTriple( 'https://calvoritmo.com/tfm/data/nerd/'+self.uuid, 
                     'https://calvoritmo.com/tfm/datamodel/nerd/hasMainSection', 
                     'https://calvoritmo.com/tfm/data/nerd/'+self.mainSection.uuid )
    self._serializeSection(ttlg, self.mainSection)
    return ttlg

  def _exportAnnotations(self, item):
    res = []
    for ann in item._annotations:
      res = res + [{
                    'surface' : ann.surface,
                    'start' : ann.start,
                    'end'   : ann.end,
                    'uri'   : ann.uri,
                    'source' : ann.source
                    }]
    return res

  def _exportSection(self, section):
    res = {}
    res['title'] = section.title
    sectionItems = []
    for item in section.sectionItems:
      if type(item) == Nerd.Section.Text:
       sectionItems = sectionItems + [{
                                      'text' : item.text,
                                      'annotations' : self._exportAnnotations(item)}]
      else:  # type(item) == Nerd.Section.UL
       listItems = []
       for li in item.texts():
         listItems = listItems + [{
                                      'text' : li.text,
                                      'annotations' : self._exportAnnotations(li)}]
       sectionItems = sectionItems + [listItems]
    res['sectionItems'] = sectionItems
    subsections = []
    for subsection in section.subsections:
       subsections = subsections + [self._exportSection(subsection)]
    res['subsections'] = subsections
    return res

  def exportJSON(self):
    res = {}
    res['friendlyName'] = self.friendlyName
    res['mainSection'] = self._exportSection(self.mainSection)
    return res
  
  def _importAnnotations(self, json_dict):
    res = []
    for ann in json_dict:
      res = res + [Nerd.Section.Text.Annotation(
                    ann['surface'],
                    ann['uri'],
                    ann['start'],
                    ann['end'],
                    ann['source']
                   )]
    return res
  
  def _importSection(self, section, json_dict):
    if len(section.sectionItems) != len(json_dict['sectionItems']):
      return
    if len(section.subsections) != len(json_dict['subsections']):
      return
    for i in range(len(section.sectionItems)):
      if type(section.sectionItems[i]) == Nerd.Section.Text:
        section.sectionItems[i]._annotations = self._importAnnotations(json_dict['sectionItems'][i]['annotations'])
      else: # type(section.sectionItems[i]) == Nerd.Section.UL
        if len(section.sectionItems[i].items) != len(json_dict['sectionItems'][i]):
          return
        for j in range(len(section.sectionItems[i].items)):
          section.sectionItems[i].items[j]._annotations = self._importAnnotations(json_dict['sectionItems'][i][j]['annotations'])
    for i in range(len(section.subsections)):
      self._importSection(section.subsections[i], json_dict['subsections'][i])
    
  def importJSON(self, json_dict):
    self._importSection(self.mainSection, json_dict['mainSection'])
    return self

# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
class WP:
  def generate(fetchStage, groundTruth):
    nerdStage = Nerd.cloneFetch(fetchStage)
    # Iterate over texts and annotate
    for fetch_text, nerd_text in zip(fetchStage.mainSection.texts(), nerdStage.mainSection.texts()):
      offset = 0
      b = BeautifulSoup(fetch_text.text, features="html.parser")
      for tag in b.contents:
        new_offset = offset + len(tag.text)
        if tag.name == 'a' and 'href' in tag.attrs:
          surface = tag.text
          start = offset
          end = new_offset
          source = 'a'
          uri = tag['href']
          ann = Nerd.Section.Text.Annotation(surface, uri, start, end, source)
          nerd_text.appendAnnotation(ann)
        if tag.name == 'b' or tag.name == 'i':
          surface = tag.text
          start = offset
          end = new_offset
          source = tag.name
          uri = 'https://calvoritmo.com/tfm/entity/'+getuuid()
          ann = Nerd.Section.Text.Annotation(surface, uri, start, end, source)
          nerd_text.appendAnnotation(ann)
          
        offset = new_offset
        
    return nerdStage


# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
class Spotlight:
  def generate(fetchStage, groundTruth):
    # https://pypi.org/project/spacy-dbpedia-spotlight/
    import spacy_dbpedia_spotlight
    nerdStage = Nerd.cloneFetch(fetchStage)
    nlp = spacy_dbpedia_spotlight.create('en')

    for nerd_text in nerdStage.mainSection.texts():
      if nerd_text.text.replace(' ', '').replace('\n', '').replace('\r', '') == '':
        continue
      for ent in nlp(nerd_text.text).ents:
        surface = ent.text
        start = ent.start_char
        end = ent.end_char
        source = 'dbpedia_spotlight'
        uri = ent.kb_id_
        ann = Nerd.Section.Text.Annotation(surface, uri, start, end, source)
        nerd_text.appendAnnotation(ann)

    return nerdStage

    
# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
class SpacyNER:
  def generate(fetchStage, groundTruth):
    import spacy
    nerdStage = Nerd.cloneFetch(fetchStage)
    
    nlp = spacy.load("en_core_web_sm")
    
    # Iterate over texts and annotate
    for nerd_text in nerdStage.mainSection.texts():
      for ent in nlp(nerd_text.text).ents:
        surface = ent.text
        start = ent.start_char
        end = ent.end_char
        source = 'spacy'
        uri = 'https://calvoritmo.com/tfm/entity/'+getuuid()
        ann = Nerd.Section.Text.Annotation(surface, uri, start, end, source)
        nerd_text.appendAnnotation(ann)

    return nerdStage

    
# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
class FullNerd:
  def generate(fetchStage, groundTruth):
    import spacy
    import spacy_dbpedia_spotlight
    nerdStage = Nerd.cloneFetch(fetchStage)

    import time
    
    a = time.time()
    for fetch_text, nerd_text in zip(fetchStage.mainSection.texts(), nerdStage.mainSection.texts()):
      offset = 0
      b = BeautifulSoup(fetch_text.text, features="html.parser")
      for tag in b.contents:
        new_offset = offset + len(tag.text)
        if tag.name == 'a' and 'href' in tag.attrs:
          surface = tag.text
          start = offset
          end = new_offset
          source = 'a'
          uri = tag['href']
          ann = Nerd.Section.Text.Annotation(surface, uri, start, end, source)
          nerd_text.appendAnnotation(ann)
        if tag.name == 'b' or tag.name == 'i':
          surface = tag.text
          start = offset
          end = new_offset
          source = tag.name
          uri = 'https://calvoritmo.com/tfm/entity/'+getuuid()
          ann = Nerd.Section.Text.Annotation(surface, uri, start, end, source)
          nerd_text.appendAnnotation(ann)
          
        offset = new_offset
    b = time.time()
    print(f'WP: {b-a}')
    
    a = time.time()
    nlp = spacy_dbpedia_spotlight.create('en')

    for nerd_text in nerdStage.mainSection.texts():
      if nerd_text.text.replace(' ', '').replace('\n', '').replace('\r', '') == '':
        continue
      for ent in nlp(nerd_text.text).ents:
        surface = ent.text
        start = ent.start_char
        end = ent.end_char
        source = 'dbpedia_spotlight'
        uri = ent.kb_id_
        ann = Nerd.Section.Text.Annotation(surface, uri, start, end, source)
        nerd_text.appendAnnotation(ann)
    b = time.time()
    print(f'Spacy NER: {b-a}')
    
    a = time.time()
    nlp = spacy.load("en_core_web_sm")
    
    # Iterate over texts and annotate
    for nerd_text in nerdStage.mainSection.texts():
      for ent in nlp(nerd_text.text).ents:
        surface = ent.text
        start = ent.start_char
        end = ent.end_char
        source = 'spacy'
        uri = 'https://calvoritmo.com/tfm/entity/'+getuuid()
        ann = Nerd.Section.Text.Annotation(surface, uri, start, end, source)
        nerd_text.appendAnnotation(ann)
    b = time.time()
    print(f'DBpedia Spotlight: {b-a}')

    return nerdStage


def find_intersecting_overlaps(overlaps, element):
    return [it for it in overlaps
            if element['start'] >= it['start'] and element['start'] <  it['end']
              or element['end']-1 >= it['start'] and element['end']-1 < it['end']]

class NerdFactory:
  def delete(uuid):
    if os.path.isfile(f'data/nerd/{uuid}.txt'):
      os.remove(f'data/nerd/{uuid}.txt')
  def build_from_str(s):
    b, ul_spans, masks = fetch.WPLists().generate(s)
    return NerdStage(b, ul_spans, masks)
  
class NerdStage(fetch.FetchDataModel):
  def __init__(self, b, ul_spans, masks, nerdModel=None, uuid=None):
    if nerdModel == None:
      nerdModel = WP()
    self.b = b
    self.ul_spans = ul_spans
    self.masks = masks
    if uuid == None:
      self.uuid = getuuid()
    else:
      self.uuid = uuid

  def get_spans(self, bs=None): # [None, {}, None, [{},{},{}], {}, None, {}]
    res = []
    if bs == None:
      bs = self.b.contents
    for it in bs:
      if it.name == 'ul':
        res = res + [self.get_spans(bs=it)]
      else:
        meta = it.find('meta')
        if meta == None or not 'value' in meta.attrs:
          res = res + [None]
        else:
          res = res + [json.loads(meta.attrs['value'].replace("%%", '"'))]
    return res

  def load(uuid, nerdModel=None):
    with open(f'data/nerd/{uuid}.txt', 'r', encoding='utf-8') as f:
      content = f.read()
    tmp = NerdFactory.build_from_str(content)
    return NerdStage(tmp.b, tmp.ul_spans, tmp.masks, uuid=uuid, nerdModel=nerdModel)
    
  def save(self, uuid=None):
    if uuid == None:
      uuid = self.uuid
    with open(f'data/nerd/{uuid}.txt', 'w', encoding='utf-8') as f:
      f.write(str(self))
    return self
  
  def delete(self):
    NerdFactory.delete(self.uuid)
  
  def edit(self, content, inplace=False):
    tmp = NerdFactory.build_from_str(content)
    self.b = tmp.b
    self.ul_spans = tmp.ul_spans
    self.masks = tmp.masks
    if not inplace:
      self.uuid = getuuid()
    return self
  
class NerdModel:
  pass


class WP_blue:

  def generate(self, fetchStage):
    b, ul_spans, masks = fetchStage.copy()
    self.annotate_span(b)
    b = self.validate(b)
    return NerdStage(b, ul_spans, masks, nerdModel=self)

  def validate(self, b): # assert html with meta is compliant
    for tag in b.find_all():
        if not tag.name in ['p', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'meta']:
          tag.replaceWithChildren()
    return b

  def annotate_span(self,b):
    for it in b.contents:
      self.annotate(it)
    
  def annotate(self, b):
    if b.name in ['p', 'li']:
      spans = self.find_overlaps(b)
      b.replaceWith(BeautifulSoup('<'+b.name+'>'+
                                      b.text+
                                      '<meta name="spans" value="'+
                                      json.dumps(spans).replace('"',"%%")+
                                      '"></'+b.name+'>',
                                      'html.parser'))
    if b.name == 'ul':
      for it in b.contents:
        self.annotate(it)

  def find_overlaps(self, b, offset=0):
    cursor = offset
    overlaps = []
    for it in b.contents:
      if it.name == None or it.name == 'meta':
        cursor = cursor + len(it.text)
      else: # it.name in ['a', 'i', 'b']
        overlaps = overlaps + self.find_overlaps(it, offset=cursor)
        overlaps = overlaps + [{'start': cursor,
                              'end'  : cursor + len(it.text),
                              'kind' : it.name,
                              'uri'  : it['href'] if 'href' in it.attrs else get_uri()}]
        cursor = cursor + len(it.text)
    return overlaps