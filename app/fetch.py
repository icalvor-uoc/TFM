from bs4 import BeautifulSoup, Comment, NavigableString
import requests
import json
import copy
import os
import app.graph as graph

from app.utils import *

class Fetch:

  class Section:
    
    class Text:
      def __init__(self, parent, text, uuid=None):
        self.parent = parent
        self.text = text
        if uuid == None:
          self.uuid = getuuid()
        else:
          self.uuid = uuid
          
      def _touch(self):
        self.uuid = getuuid()
        self.parent._touch()
        
      def edit(self, text):
        if text != self.text:
          self.text = text
          self._touch()
      
    class UL:
      def __init__(self, parent, ul, uuid=None):
        self.parent = parent
        self.items = [Fetch.Section.Text(self, text) for text in ul]
        if uuid == None:
          self.uuid = getuuid()
        else:
          self.uuid = uuid

      def _touch(self):
        self.uuid = getuuid()
        self.parent._touch()
      
      # Accepts str
      # Assumes str is valid html text with only <a>, <b> and <i> labels      
      def appendText(self, text):
        newText = Fetch.Section.Text(self, text)
        self.items = self.items + [newText]
        self._touch()
        return newText

      def texts(self):
        return self.items.__iter__()

    def __init__(self, parent, title="Untitled", uuid=None):
      self.parent = parent
      if type(self.parent) == Fetch:
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
      newUL = Fetch.Section.UL(self.cursor, ul)
      self.cursor.sectionItems = s + [newUL]
      self._touch()
      return newUL
       
    # Accepts str
    # Assumes str is valid html text with only <a>, <b> and <i> labels
    def appendText(self, text):
      self.resetCursor()
      s = self.cursor.sectionItems
      newText = Fetch.Section.Text(self.cursor, text)
      self.cursor.sectionItems = s + [newText]   
      self._touch()      
      return newText
    
    def appendSection(self, title="Untitled"):
      newSection = Fetch.Section(self.cursor, title=title)
      self.cursor.subsections = self.cursor.subsections + [newSection]
      self.resetCursor()
      self._touch()
      return newSection
    
    def insertSection(self, title="Untitled"):
      self._touch()
      return self.resetCursor().appendSection(title=title)
    
    def drop(self):
      if type(self.parent) != Fetch.Section or self.parent == self:
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
            if type(self.section.sectionItems[self.index]) == Fetch.Section.UL:
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
          if type(item) == Fetch.Section.Text:
            return item
          else: # Fetch.Section.UL
            self.ul = item.texts()
            return next(self.ul)
            
      return TextIterator().__iter__()
  
  def _touch(self):
    self.uuid = getuuid()

  def _buildText(self, ttlg, container, uri):
    text =  ttlg.getTriple(s=uri, p='https://calvoritmo.com/tfm/datamodel/fetch/hasText')[2]
    text = container.appendText(text)
    text.uuid = uri.split('/')[-1]
    
  def _buildList(self, ttlg, section, uri):
    l = section.appendUL([])
    item_uris = ttlg.getList(uri, 'https://calvoritmo.com/tfm/datamodel/fetch/hasListItems')
    for item_uri in item_uris:
      self._buildText(ttlg, l, item_uri)
    l.uuid = uri.split('/')[-1]
    
  def _buildSection(self, ttlg, section, uri):
    section.title = ttlg.getTriple(s=uri, p='https://calvoritmo.com/tfm/datamodel/fetch/hasTitle')[2]
    subsection_uris = ttlg.getList(uri, 'https://calvoritmo.com/tfm/datamodel/fetch/hasSubsections')
    item_uris = ttlg.getList(uri, 'https://calvoritmo.com/tfm/datamodel/fetch/hasSectionItems')
    
    for item_uri in item_uris:
      item_type = ttlg.getTriple(s=item_uri, p='http://www.w3.org/1999/02/22-rdf-syntax-ns#type')[2]
      if item_type == 'https://calvoritmo.com/tfm/datamodel/fetch/List':
        self._buildList(ttlg, section, item_uri)
      else: # item_type == 'https://calvoritmo.com/tfm/datamodel/fetch/Text'
        self._buildText(ttlg, section, item_uri)
        
    for section_uri in subsection_uris:
      new_section = section.appendSection()
      self._buildSection(ttlg, new_section, section_uri)
      
    section.uuid = uri.split('/')[-1]
    
  def __init__(self, filename=None):
    self.uuid = getuuid()
    self.mainSection = Fetch.Section(self)
    self.friendlyName = 'Fetch Stage'
    self.parentStage = 'https://calvoritmo.com/tfm/meta/bottom_stage'
    if filename != None:
      ttlg = graph.TurtleGraph(filename=filename)
      fetch_uri = ttlg.getTriple(p='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', o='https://calvoritmo.com/tfm/meta/Stage')[0]
      self.friendlyName = ttlg.getTriple(s=fetch_uri, p='https://calvoritmo.com/tfm/meta/stageFriendlyName')[2]
      mainSection_uri = ttlg.getTriple(s=fetch_uri, p='https://calvoritmo.com/tfm/datamodel/fetch/hasMainSection')[2]
      self._buildSection(ttlg, self.mainSection, mainSection_uri)
      self.uuid = fetch_uri.split('/')[-1]
  
  def _serializeSection(self, ttlg, section):
    ttlg.addTriple(  'https://calvoritmo.com/tfm/data/fetch/'+section.uuid, 
                     "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
                     "https://calvoritmo.com/tfm/datamodel/fetch/Section")
    ttlg.setLiteral( 'https://calvoritmo.com/tfm/data/fetch/'+section.uuid,
                     'https://calvoritmo.com/tfm/datamodel/fetch/hasTitle',
                     section.title)
    sectionItems = []
    for item in section.sectionItems:
      if type(item) == Fetch.Section.UL:
        ttlg.addTriple( 'https://calvoritmo.com/tfm/data/fetch/'+item.uuid,
                        'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                        'https://calvoritmo.com/tfm/datamodel/fetch/List' )
        listItems = []
        for text in item.texts():
          listItems = listItems + ['https://calvoritmo.com/tfm/data/fetch/'+text.uuid]
          ttlg.addTriple( 'https://calvoritmo.com/tfm/data/fetch/'+text.uuid,
                          'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                          'https://calvoritmo.com/tfm/datamodel/fetch/ListItem' )
          ttlg.setLiteral( 'https://calvoritmo.com/tfm/data/fetch/'+text.uuid,
                           'https://calvoritmo.com/tfm/datamodel/fetch/hasText',
                            text.text  )
        ttlg.updateList( 'https://calvoritmo.com/tfm/data/fetch/'+item.uuid,
                         'https://calvoritmo.com/tfm/datamodel/fetch/hasListItems',
                         listItems)
      else:  # type(item) == Fetch.Section.Text
        ttlg.addTriple( 'https://calvoritmo.com/tfm/data/fetch/'+item.uuid,
                        'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                        'https://calvoritmo.com/tfm/datamodel/fetch/Text' )
        ttlg.setLiteral('https://calvoritmo.com/tfm/data/fetch/'+item.uuid,
                        'https://calvoritmo.com/tfm/datamodel/fetch/hasText',
                        item.text  )
      sectionItems = sectionItems + ['https://calvoritmo.com/tfm/data/fetch/'+item.uuid]
    ttlg.updateList( 'https://calvoritmo.com/tfm/data/fetch/'+section.uuid,
                     'https://calvoritmo.com/tfm/datamodel/fetch/hasSectionItems',
                      sectionItems)
    subsections = []
    for subsection in section.subsections:
      subsections = subsections + ['https://calvoritmo.com/tfm/data/fetch/'+subsection.uuid]
      self._serializeSection(ttlg, subsection)
    ttlg.updateList( 'https://calvoritmo.com/tfm/data/fetch/'+section.uuid,
                     'https://calvoritmo.com/tfm/datamodel/fetch/hasSubsections',
                     subsections  )
  
  def asGraph(self):
    ttlg = graph.TurtleGraph()
    # 'https://calvoritmo.com/tfm/meta/hasGroundTruth'
    # 'https://calvoritmo.com/tfm/meta/hasBaseStage'
    # 'https://calvoritmo.com/tfm/meta/hasModel'
    ttlg.addTriple('https://calvoritmo.com/tfm/data/fetch/'+self.uuid,
                   'https://calvoritmo.com/tfm/meta/hasParentStage',
                   self.parentStage)
    ttlg.addTriple( 'https://calvoritmo.com/tfm/data/fetch/'+self.uuid,
                    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type', 
                    'https://calvoritmo.com/tfm/meta/Stage' )
    ttlg.setLiteral( 'https://calvoritmo.com/tfm/data/fetch/'+self.uuid, 
                     'https://calvoritmo.com/tfm/meta/stageFriendlyName', 
                     self.friendlyName )   
    ttlg.addTriple( 'https://calvoritmo.com/tfm/data/fetch/'+self.uuid, 
                     'https://calvoritmo.com/tfm/datamodel/fetch/hasMainSection', 
                     'https://calvoritmo.com/tfm/data/fetch/'+self.mainSection.uuid )
    self._serializeSection(ttlg, self.mainSection)
    return ttlg
  
  def _exportSection(self, section):
    res = {}
    res['title'] = section.title
    sectionItems = []
    for item in section.sectionItems:
      if type(item) == Fetch.Section.Text:
       sectionItems = sectionItems + [item.text]
      else:  # type(item) == Fetch.Section.UL
       listItems = []
       for li in item.texts():
         listItems = listItems + [li.text]
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

  def _editSection(self, section, json_dict):
    if len(section.sectionItems) != len(json_dict['sectionItems']):
      return
    if len(section.subsections) != len(json_dict['subsections']):
      return
    section.title = json_dict['title']
    for i in range(len(section.sectionItems)):
      if type(section.sectionItems[i]) == Fetch.Section.Text:
        section.sectionItems[i].edit(json_dict['sectionItems'][i])
      else: # type(section.sectionItems[i]) == Fetch.Section.UL
        if len(section.sectionItems[i].items) != len(json_dict['sectionItems'][i]):
          return
        for j in range(len(section.sectionItems[i].items)):
          section.sectionItems[i].items[j].edit(json_dict['sectionItems'][i][j])
    for i in range(len(section.subsections)):
      self._editSection(section.subsections[i], json_dict['subsections'][i])
    
  def importJSON(self, json_dict):
    self._editSection(self.mainSection, json_dict['mainSection'])
    return self


class FetchFactory:
  def build_from_title(title):
    s = FetchModel.fetchWP(title)
    return FetchFactory.build_from_str(s)

  def build_from_str(s):
    return FetchStage(s)
    
  def delete(uuid):
    if os.path.isfile(f'data/fetch/{uuid}.txt'):
      os.remove(f'data/fetch/{uuid}.txt')

# register in catalog
# implement decent groundTruth
# graph <- turtlegraph, sparqlgraph, groundTruth
class WikipediaHTML:
  def generate(rawHTML, groundTruth):  # rawHTML instead of Stage?
      if BeautifulSoup(rawHTML, features="html.parser").find('title') == None:
        title = None
      else:
        title = BeautifulSoup(rawHTML, features="html.parser").find('title').text
        title = BeautifulSoup(f'<h1>{title}</h1>', 'html.parser')
      b = BeautifulSoup(rawHTML, features="html.parser").find('body')
      if b == None:
        b = BeautifulSoup(rawHTML, features="html.parser")
      else:
        b = BeautifulSoup(str(b), features="html.parser")
      for tag in b.find_all('style'):
          tag.extract()
      for tag in b.find_all('meta'):
          if 'name' not in tag.attrs or tag.attrs['name'] != 'spans':
            tag.extract()
      for tag in b.find_all('h5'):
          tag.extract()
      for tag in b.find_all('h1'):
          tag.extract()
      for tag in b.find_all('h6'):
          tag.extract()
      for tag in b.find_all('link'):
          tag.extract()
      for tag in b.find_all('figure'):
          tag.extract()
      for tag in b.find_all('dd'):
          tag.replaceWithChildren()
      for tag in b.find_all('dl'):
          tag.replaceWithChildren()
      for tag in b.find_all('math'):
          tag.extract()
      for tag in b.find_all('img'):
          tag.extract()
      for tag in b.find_all('small'):
          tag.extract()
      for tag in b.find_all('span', class_='editsection'):
          tag.extract()
      for tag in b.find_all('span'):
          tag.replaceWithChildren()
      for tag in b.find_all(class_='mw-reflink-text'):
          tag.extract()
      for tag in b.find_all(class_='mw-ref'):
          tag.extract()
      for tag in b.find_all(class_='hatnote'):
          tag.extract()
      for tag in b.find_all(class_='infobox'):
          tag.extract()
      for tag in b.find_all(class_='shortdescription'):
          tag.extract()
      for tag in b.find_all(class_='thumb'):
          tag.extract()
      for tag in b.find_all(class_='wikitable'):
          tag.extract()
      for tag in b.find_all(class_='gallery'):
          tag.extract()
      
      for tag in b.find_all('table'):
          tag.extract()
      
      for tag in b.find_all('blockquote'):
          tag.replaceWithChildren()
          
      for tag in b.find_all('tbody'):
          tag.replaceWithChildren()
          
      for tag in b.find_all('th'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('tr'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('td'):
          tag.replaceWithChildren()
          
      aux = b.find(id='Footnotes')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='See_also')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='External_links')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='Further_reading')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='Notes')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='References')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='Gallery')
      if aux:
          aux.findParent().extract()

      b.attrs = {}
      for tag in b.find_all('i'):
          tag.attrs = {}
      for tag in b.find_all('b'):
          tag.attrs = {}
      for tag in b.find_all('ul'):
          tag.attrs = {}
      for tag in b.find_all('ol'):
          tag.attrs = {}
      for tag in b.find_all('li'):
          tag.attrs = {}
          
      for tag in b.find_all('li'):
          for it in tag.find_all('p'):
            it.replaceWithChildren()

      for tag in b.find_all('section'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('a'):
          if not 'href' in tag.attrs:
           # print(tag)
            tag.replaceWithChildren()
            continue
          href = tag['href']
          href = href.split('#')[0]
          if href[:len('http://dbpedia.org/resource/')] == 'http://dbpedia.org/resource/':
            continue
          # print('------' + href)
          if href[:len('../../../../articles')] == '../../../../articles':
            # print('------' + href)
            href = './' + href[len('../../../../articles/a/a/d/'):]
            if len(href) > 5 and href[-5:] == '.html':
              href = href[:-5]
            if len(href) > 5 and href[-5] == '_' and  \
               'abcdef0123456789'.find(href[-4]) != -1 and \
               'abcdef0123456789'.find(href[-3]) != -1 and \
               'abcdef0123456789'.find(href[-2]) != -1 and \
               'abcdef0123456789'.find(href[-1]) != -1:
              href = href[:-5]
          if href[:2] == './' and not ':' in href:
            href = 'http://dbpedia.org/resource/' + href[2:]
            tag.attrs = {'href': href}
          else:
            tag.replaceWithChildren()
      
      for c in b(text=lambda t: isinstance(t, Comment)):
          c.extract()
      
      for tag in b.find_all('var'):
          tag.replaceWithChildren()
      for tag in b.find_all('sub'):
          tag.replaceWithChildren()
      for tag in b.find_all('sup'):
          tag.replaceWithChildren()
      for tag in b.find_all('div'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('ol'):
        newtag = BeautifulSoup('<ul></ul>', 'html.parser')
        for c in list(tag.contents):
          newtag.contents[0].append(c)
        tag.replaceWith(newtag)
 
      for tag in b.find_all():
          if not tag.name in ['p', 'a', 'b', 'i', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'meta']:
            tag.replaceWithChildren()
      
      for it in b.find_all(text=True):
        if it == '\n':
          it.extract()
          continue
        begin = "" if it.parent != b else "<p>"
        end = "" if it.parent != b else "</p>"
        it.replaceWith(BeautifulSoup(begin+it.text.replace("\"", "'")+end, 'html.parser'))
        
      if title != None:        
        b.insert(0,title)
      
      for tag in b.contents:
        if tag.name in ['h1', 'h2', 'h3', 'h4']:
          last_header = tag.name        
        if tag.name != 'ul':
          continue
        if last_header == 'h1':
          if tag.find('ul') != None:
            tag.replaceWith(WikipediaHTML._flattenUl(tag, last_header='h1'))
        if last_header == 'h2':
          if tag.find('ul') != None:
            tag.replaceWith(WikipediaHTML._flattenUl(tag, last_header='h2'))
        if last_header == 'h3':
          if tag.find('ul') != None:
            tag.replaceWith(WikipediaHTML._flattenUl(tag, last_header='h3'))
        if last_header == 'h4':
          for i in tag.find_all('li'):
            i.replaceWithChildren()
          for i in tag.find_all('ul'):
            i.replaceWithChildren()
      
      f = Fetch()
      f.mainSection.title = WikipediaHTML._cleanTitle(b.contents[0].text)
      s = f.mainSection
      last_header = 'h1'
      previous_list = None
      for tag in b.contents[1:]:
        if tag.name == 'ul':
          if previous_list == None:
            previous_list = s.appendUL([li.text if type(li) == NavigableString else li.encode_contents().decode() for li in tag.contents])
          else:
            for li in tag.contents:
              previous_list.appendText(li.encode_contents().decode())
         
        if tag.name == 'p':
          previous_list = None
          s.appendText(tag.encode_contents().decode())
          
        if tag.name == 'h2':
          previous_list = None
          if last_header == 'h1':
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h2':
            s.floatCursor()
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h3':
            s.floatCursor()
            s.floatCursor()
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h4':
            s.floatCursor()
            s.floatCursor()
            s.floatCursor()
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          last_header = 'h2'
        
        if tag.name == 'h3':
          previous_list = None
          if last_header == 'h1':
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
            last_header = 'h2'
            continue
          if last_header == 'h2':
            s.insertSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h3':
            s.floatCursor()
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h4':
            s.floatCursor()
            s.floatCursor()
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          last_header = 'h3'
        
        if tag.name == 'h4':
          previous_list = None
          if last_header == 'h1':
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
            last_header = 'h2'
            continue
          if last_header == 'h2':
            s.insertSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
            last_header = 'h3'
            continue
          if last_header == 'h3':
            s.insertSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h4':
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          last_header = 'h4'
        
      for i in range(5):  # 5 is a magic number
        for section in list(s.sections()):
          if section.subsections == []:
            containsUL = False
            for item in section.sectionItems:
              if type(item) == Fetch.Section.UL:
                containsUL = True
            if not containsUL:
              section.drop()        
      return f

  def _cleanTitle(t):
    return t
    if t[0] == ' ':
      t = t[1:]
    if len(t) > len(' - Wikipedia, the free encyclopedia') and t[-len(' - Wikipedia, the free encyclopedia'):] == ' - Wikipedia, the free encyclopedia':
      t = t[:-len(' - Wikipedia, the free encyclopedia')]
    return t

  def _flattenUl(tag, last_header='h1'):
          if tag.find('ul') == None:
            return tag
          if last_header == 'h4':
            for i in tag.find_all('li'):
              i.replaceWithChildren()
            for i in tag.find_all('ul'):
              i.replaceWithChildren()
            return tag
          headers = ['h1', 'h2', 'h3', 'h4']
          next_header = headers[headers.index(last_header)+1]

          newtag = BeautifulSoup('', 'html.parser')
          for li in list(tag.contents):
            header_text = ''
            for it in list(li.contents):
              if it.name == None:
                header_text = header_text + it.text
            newtag.append(BeautifulSoup(f'<{next_header}>{header_text}</{next_header}>',
                                         'html.parser'))
            for it in list(li.contents):
              if it.name == 'ul':
                newtag.append(WikipediaHTML._flattenUl(it, last_header=next_header))
          
          return newtag
      



class DumpHTML:
  def generate(rawHTML, groundTruth):  # rawHTML instead of Stage?
#      if BeautifulSoup(rawHTML, features="html.parser").find('title') == None:
#        title = None
#      else:
      title = BeautifulSoup(rawHTML, features="html.parser").find('h1').text
      title = BeautifulSoup(f'<h1>{title}</h1>', 'html.parser')
      b = BeautifulSoup(rawHTML, features="html.parser").find('div', {'id' : 'bodyContent'})
      if b == None:
        b = BeautifulSoup(rawHTML, features="html.parser")
      else:
        b = BeautifulSoup(str(b), features="html.parser")
      for tag in b.find_all('style'):
          tag.extract()
      for tag in b.find_all('meta'):
          if 'name' not in tag.attrs or tag.attrs['name'] != 'spans':
            tag.extract()
      for tag in b.find_all('h5'):
          tag.extract()
      for tag in b.find_all('h1'):
          tag.extract()
      for tag in b.find_all('h6'):
          tag.extract()
      for tag in b.find_all('link'):
          tag.extract()
      for tag in b.find_all('figure'):
          tag.extract()
      for tag in b.find_all('dd'):
          tag.replaceWithChildren()
      for tag in b.find_all('dl'):
          tag.replaceWithChildren()
      for tag in b.find_all('math'):
          tag.extract()
      for tag in b.find_all('img'):
          tag.extract()
      for tag in b.find_all('small'):
          tag.extract()
      for tag in b.find_all('span', class_='editsection'):
          tag.extract()
      for tag in b.find_all('span'):
          tag.replaceWithChildren()
      for tag in b.find_all(class_='mw-reflink-text'):
          tag.extract()
      for tag in b.find_all(class_='mw-ref'):
          tag.extract()
      for tag in b.find_all(class_='hatnote'):
          tag.extract()
      for tag in b.find_all(class_='infobox'):
          tag.extract()
      for tag in b.find_all(class_='shortdescription'):
          tag.extract()
      for tag in b.find_all(class_='thumb'):
          tag.extract()
      for tag in b.find_all(class_='wikitable'):
          tag.extract()
      for tag in b.find_all(class_='gallery'):
          tag.extract()

      for tag in b.find_all(id='siteSub'):
          tag.extract()
      
      for tag in b.find_all('table'):
          tag.extract()
      
      for tag in b.find_all('blockquote'):
          tag.replaceWithChildren()
          
      for tag in b.find_all('tbody'):
          tag.replaceWithChildren()
          
      for tag in b.find_all('th'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('tr'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('td'):
          tag.replaceWithChildren()
          
#      aux = b.find(id='Footnotes')
#      if aux:
#          aux.findParent().extract()
#      aux = b.find(id='See_also')
#      if aux:
#          aux.findParent().extract()
#      aux = b.find(id='External_links')
#      if aux:
#          aux.findParent().extract()
#      aux = b.find(id='Further_reading')
#      if aux:
#          aux.findParent().extract()
#      aux = b.find(id='Notes')
#      if aux:
#          aux.findParent().extract()
#      aux = b.find(id='References')
#      if aux:
#          aux.findParent().extract()
#      aux = b.find(id='Gallery')
#      if aux:
#          aux.findParent().extract()

      b.attrs = {}
      for tag in b.find_all('i'):
          tag.attrs = {}
      for tag in b.find_all('b'):
          tag.attrs = {}
      for tag in b.find_all('ul'):
          tag.attrs = {}
      for tag in b.find_all('ol'):
          tag.attrs = {}
      for tag in b.find_all('li'):
          tag.attrs = {}
          
      for tag in b.find_all('li'):
          for it in tag.find_all('p'):
            it.replaceWithChildren()

      for tag in b.find_all('section'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('a'):
          if not 'href' in tag.attrs:
           # print(tag)
            tag.replaceWithChildren()
            continue
          href = tag['href']
          href = href.split('#')[0]
          if href[:len('http://dbpedia.org/resource/')] == 'http://dbpedia.org/resource/':
            continue
          # print('------' + href)
          if href[:len('../../../../articles')] == '../../../../articles':
            # print('------' + href)
            href = './' + href[len('../../../../articles/a/a/d/'):]
            if len(href) > 5 and href[-5:] == '.html':
              href = href[:-5]
            if len(href) > 5 and href[-5] == '_' and  \
               'abcdef0123456789'.find(href[-4]) != -1 and \
               'abcdef0123456789'.find(href[-3]) != -1 and \
               'abcdef0123456789'.find(href[-2]) != -1 and \
               'abcdef0123456789'.find(href[-1]) != -1:
              href = href[:-5]
          if href[:2] == './' and not ':' in href:
            href = 'http://dbpedia.org/resource/' + href[2:]
            tag.attrs = {'href': href}
          else:
            tag.replaceWithChildren()
      
      for c in b(text=lambda t: isinstance(t, Comment)):
          c.extract()
      
      for tag in b.find_all('var'):
          tag.replaceWithChildren()
      for tag in b.find_all('sub'):
          tag.replaceWithChildren()
      for tag in b.find_all('sup'):
          tag.replaceWithChildren()
      for tag in b.find_all('div'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('ol'):
        newtag = BeautifulSoup('<ul></ul>', 'html.parser')
        for c in list(tag.contents):
          newtag.contents[0].append(c)
        tag.replaceWith(newtag)
 
      for tag in b.find_all():
          if not tag.name in ['p', 'a', 'b', 'i', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'meta']:
            tag.replaceWithChildren()
      
      for it in b.find_all(text=True):
        if it == '\n':
          it.extract()
          continue
        begin = "" if it.parent != b else "<p>"
        end = "" if it.parent != b else "</p>"
        it.replaceWith(BeautifulSoup(begin+it.text.replace("\"", "'")+end, 'html.parser'))
        
      if title != None:        
        b.insert(0,title)
      
      for tag in b.contents:
        if tag.name in ['h1', 'h2', 'h3', 'h4']:
          last_header = tag.name        
        if tag.name != 'ul':
          continue
        if last_header == 'h1':
          if tag.find('ul') != None:
            tag.replaceWith(WikipediaHTML._flattenUl(tag, last_header='h1'))
        if last_header == 'h2':
          if tag.find('ul') != None:
            tag.replaceWith(WikipediaHTML._flattenUl(tag, last_header='h2'))
        if last_header == 'h3':
          if tag.find('ul') != None:
            tag.replaceWith(WikipediaHTML._flattenUl(tag, last_header='h3'))
        if last_header == 'h4':
          for i in tag.find_all('li'):
            i.replaceWithChildren()
          for i in tag.find_all('ul'):
            i.replaceWithChildren()
      
      f = Fetch()
      f.mainSection.title = WikipediaHTML._cleanTitle(b.contents[0].text)
      s = f.mainSection
      last_header = 'h1'
      previous_list = None
      ignore_until_h = False
      for tag in b.contents[1:]:
        if tag.text.lower().strip(' :') in ['footnotes', 'see also', 'external links', 'further reading', 'notes', 'references', 'gallery']:
          ignore_until_h = True
          continue
      
        if tag.name == 'ul':
          if ignore_until_h:
            continue
          if previous_list == None:
            previous_list = s.appendUL([li.text if type(li) == NavigableString else li.encode_contents().decode() for li in tag.contents])
          else:
            for li in tag.contents:
              if li.encode_contents().decode().strip() == '':
                continue
              previous_list.appendText(li.encode_contents().decode())
         
        if tag.name == 'p':
          if ignore_until_h:
            continue
          if tag.encode_contents().decode().strip() == '':
            continue
          previous_list = None
          s.appendText(tag.encode_contents().decode())
          
        if tag.name == 'h2':
          ignore_until_h = False
          previous_list = None
          if last_header == 'h1':
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h2':
            s.floatCursor()
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h3':
            s.floatCursor()
            s.floatCursor()
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h4':
            s.floatCursor()
            s.floatCursor()
            s.floatCursor()
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          last_header = 'h2'
        
        if tag.name == 'h3':
          ignore_until_h = False
          previous_list = None
          if last_header == 'h1':
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
            last_header = 'h2'
            continue
          if last_header == 'h2':
            s.insertSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h3':
            s.floatCursor()
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h4':
            s.floatCursor()
            s.floatCursor()
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          last_header = 'h3'
        
        if tag.name == 'h4':
          ignore_until_h = False
          previous_list = None
          if last_header == 'h1':
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
            last_header = 'h2'
            continue
          if last_header == 'h2':
            s.insertSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
            last_header = 'h3'
            continue
          if last_header == 'h3':
            s.insertSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          if last_header == 'h4':
            s.appendSection(WikipediaHTML._cleanTitle(tag.text))
            s.resetCursor()
          last_header = 'h4'
        
      for i in range(5):  # 5 is a magic number
        for section in list(s.sections()):
          if section.subsections == []:
            containsUL = False
            for item in section.sectionItems:
              if type(item) == Fetch.Section.UL:
                containsUL = True
            if not containsUL:
              section.drop()        
      return f



class FetchDataModel:
  def copy(self):
    return copy.copy(self.b), copy.copy(self.ul_spans), copy.copy(self.masks)
  
  def span_number(self):
    return len(self.ul_spans)

  def render_span(self, i):
    return self.render_text(mask=self.masks[i])
  
  def render_text(self, mask=None):
    if mask == None:
      return ''.join([str(it) for it in self.b])
    text = ''
    for i, it in enumerate(self.b.contents):
      if mask[i]:
        if it.name == 'ul':
          for li in it.contents:
            text = text + '\n' + li.text
        else:
          text = text + '\n' + it.text
    return text
   
  def render_summary(self):
    return [str(it)[:min(10,len(str(it)))] for it in self.b.contents]

  def __str__(self):
    return str(self.b)


class FetchStage(FetchDataModel):
  def __init__(self, content, fetchModel=None, uuid=None):
    if fetchModel == None:
      self.fetchModel = WPLists()
    else:
      self.fetchModel = fetchModel
    self.b, self.ul_spans, self.masks = self.fetchModel.generate(content)
    if uuid == None:
      self.uuid = getuuid()
    else:
      self.uuid = uuid
    
  def load(uuid, fetchModel=None):
    with open(f'data/fetch/{uuid}.txt', 'r', encoding='utf-8') as f:
      content = f.read()
    return FetchStage(content, fetchModel=fetchModel, uuid=uuid)
    
  def save(self, uuid=None):
    if uuid == None:
      uuid = self.uuid
    with open(f'data/fetch/{uuid}.txt', 'w', encoding='utf-8') as f:
      f.write(str(self))
    return self
  
  def delete(self):
    FetchFactory.delete(self.uuid)
  
  def edit(self, content, inplace=False):
    self.b, self.ul_spans, self.masks = self.fetchModel.generate(content)
    if not inplace:
      self.uuid = getuuid()
    return self


class FetchModel:
  def fetchWP(title):
    url = f"https://en.wikipedia.org/w/rest.php/v1/page/{title}/html"
    r = requests.get(url)
    return r.text
    
  def random_articles(n):
    result = []
    for i in range(n):
      text = requests.get("https://en.wikipedia.org/api/rest_v1/page/random/title")
      result = result + [json.loads(text.text)['items'][0]['title']]
    return result

class WPLists:
    def generate(self, s):
      if BeautifulSoup(s, features="html.parser").find('title') == None:
        title = None
      else:
        title = BeautifulSoup(s, features="html.parser").find('title').text
        title = BeautifulSoup(f'<h1>{title}</h1>', 'html.parser')
      b = BeautifulSoup(s, features="html.parser").find('body')
      if b == None:
        b = BeautifulSoup(s, features="html.parser")
      else:
        b = BeautifulSoup(str(b), features="html.parser")
      for tag in b.find_all('style'):
          tag.extract()
      for tag in b.find_all('meta'):
          if 'name' not in tag.attrs or tag.attrs['name'] != 'spans':
            tag.extract()
      for tag in b.find_all('h5'):
          tag.extract()
      for tag in b.find_all('h1'):
          tag.extract()
      for tag in b.find_all('h6'):
          tag.extract()
      for tag in b.find_all('link'):
          tag.extract()
      for tag in b.find_all('figure'):
          tag.extract()
      for tag in b.find_all('dd'):
          tag.replaceWithChildren()
      for tag in b.find_all('dl'):
          tag.replaceWithChildren()
      for tag in b.find_all('math'):
          tag.extract()
      for tag in b.find_all('img'):
          tag.extract()
      for tag in b.find_all('small'):
          tag.extract()
      for tag in b.find_all('span'):
          tag.replaceWithChildren()
      for tag in b.find_all(class_='mw-reflink-text'):
          tag.extract()
      for tag in b.find_all(class_='mw-ref'):
          tag.extract()
      for tag in b.find_all(class_='hatnote'):
          tag.extract()
      for tag in b.find_all(class_='infobox'):
          tag.extract()
      for tag in b.find_all(class_='shortdescription'):
          tag.extract()
      for tag in b.find_all(class_='thumb'):
          tag.extract()
      for tag in b.find_all(class_='wikitable'):
          tag.extract()
      for tag in b.find_all(class_='gallery'):
          tag.extract()
      
      for tag in b.find_all('table'):
          tag.extract()
      
      for tag in b.find_all('blockquote'):
          tag.replaceWithChildren()
          
      for tag in b.find_all('tbody'):
          tag.replaceWithChildren()
          
      for tag in b.find_all('th'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('tr'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('td'):
          tag.replaceWithChildren()
          
      aux = b.find(id='Footnotes')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='See_also')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='External_links')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='Further_reading')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='Notes')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='References')
      if aux:
          aux.findParent().extract()
      aux = b.find(id='Gallery')
      if aux:
          aux.findParent().extract()

      b.attrs = {}
      for tag in b.find_all('i'):
          tag.attrs = {}
      for tag in b.find_all('b'):
          tag.attrs = {}
      for tag in b.find_all('ul'):
          tag.attrs = {}
      for tag in b.find_all('ol'):
          tag.attrs = {}
      for tag in b.find_all('li'):
          tag.attrs = {}
          
      for tag in b.find_all('li'):
          for it in tag.find_all('p'):
            it.replaceWithChildren()

      for tag in b.find_all('section'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('a'):
          href = tag['href']
          href = href.split('#')[0]
          if href[:len('http://dbpedia.org/resource/')] == 'http://dbpedia.org/resource/':
            continue
          if href[:2] == './' and not ':' in href:
            href = 'http://dbpedia.org/resource/' + href[2:]
            tag.attrs = {'href': href}
          else:
            tag.replaceWithChildren()
      
      for c in b(text=lambda t: isinstance(t, Comment)):
          c.extract()
      
      for tag in b.find_all('var'):
          tag.replaceWithChildren()
      for tag in b.find_all('sub'):
          tag.replaceWithChildren()
      for tag in b.find_all('sup'):
          tag.replaceWithChildren()
      for tag in b.find_all('div'):
          tag.replaceWithChildren()
      
      for tag in b.find_all('ol'):
        newtag = BeautifulSoup('<ul></ul>', 'html.parser')
        for c in list(tag.contents):
          newtag.contents[0].append(c)
        tag.replaceWith(newtag)
 
      for tag in b.find_all():
          if not tag.name in ['p', 'a', 'b', 'i', 'ul', 'li', 'h1', 'h2', 'h3', 'h4', 'meta']:
            tag.replaceWithChildren()
      
      for it in b.find_all(text=True):
        if it == '\n':
          it.extract()
          continue
        begin = "" if it.parent != b else "<p>"
        end = "" if it.parent != b else "</p>"
        it.replaceWith(BeautifulSoup(begin+it.text.replace("\"", "'")+end, 'html.parser'))
        
      if title != None:        
        b.insert(0,title)
      
      for tag in b.contents:
        if tag.name in ['h1', 'h2', 'h3', 'h4']:
          last_header = tag.name        
        if tag.name != 'ul':
          continue
        if last_header == 'h1':
          if tag.find('ul') != None:
            tag.replaceWith(self.flattenUl(tag, last_header='h1'))
        if last_header == 'h2':
          if tag.find('ul') != None:
            tag.replaceWith(self.flattenUl(tag, last_header='h2'))
        if last_header == 'h3':
          if tag.find('ul') != None:
            tag.replaceWith(self.flattenUl(tag, last_header='h3'))
        if last_header == 'h4':
          for i in tag.find_all('li'):
            i.replaceWithChildren()
          for i in tag.find_all('ul'):
            i.replaceWithChildren()
      
      ul_spans = self.find_ULs(b)
      masks = self.find_masks(b)
      
      return b, ul_spans, masks

    def find_ULs(self, b):
        ul_spans = []
        last_span = None
        for i, it in enumerate(b.contents):
          if last_span == None:
            if it.name == 'ul':
              last_span = i
          else:
            if it.name != 'ul':
              ul_spans = ul_spans + [(last_span, i)]
              last_span = None
        if last_span != None:
          ul_spans = ul_spans + [(last_span, len(b.contents))]
        return ul_spans

    def find_masks(self, b):
        ul_spans = self.find_ULs(b)
        masks = []

        for ul in ul_spans:
          mask = [False] * len(b.contents)
          mask[0] = True
          base = ul[0]
          h4 = False
          h3 = False
          h2 = False
          
          for i in range(ul[0]-1, 0, -1):
            if b.contents[i].name == 'h4' and not h4 and not h3 and not h2:
              mask[i] = True
              h4 = True
            if b.contents[i].name == 'h3' and not h3 and not h2:
              mask[i] = True
              h3 = True
            if b.contents[i].name == 'h2'and not h2:        
              mask[i] = True
              h2 = True

          for i in range(ul[0], ul[1]):
            mask[i] = True
          
          masks = masks + [mask]
        return masks

    # >>> flattenUl(BeautifulSoup('<ul><li>ee<ul><li>oo</li><li>o33</li></ul></li></ul>', 'html.parser').contents[0])
    # <h1>ee</h1><ul><li>oo</li><li>o33</li></ul>
    def flattenUl(self, tag, last_header='h1'):
      if tag.find('ul') == None:
        return tag
      if last_header == 'h4':
        for i in tag.find_all('li'):
          i.replaceWithChildren()
        for i in tag.find_all('ul'):
          i.replaceWithChildren()
        return tag
      headers = ['h1', 'h2', 'h3', 'h4']
      next_header = headers[headers.index(last_header)+1]

      newtag = BeautifulSoup('', 'html.parser')
      for li in list(tag.contents):
        header_text = ''
        for it in list(li.contents):
          if it.name == None:
            header_text = header_text + it.text
        newtag.append(BeautifulSoup(f'<{next_header}>{header_text}</{next_header}>',
                                     'html.parser'))
        for it in list(li.contents):
          if it.name == 'ul':
            newtag.append(self.flattenUl(it, last_header=next_header))
      
      return newtag

