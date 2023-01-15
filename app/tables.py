from datetime import datetime
# pip install dataclasses
from dataclasses import dataclass

import app.app as app

@dataclass
class NExecution(app.db.Model):
  id: int
  frefinement: int
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  frefinement = app.db.Column(app.db.Integer())
   
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
@dataclass
class TGExecution(app.db.Model):
  id: int
  nrefinement: int
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  nrefinement = app.db.Column(app.db.Integer())
   
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
@dataclass
class TEExecution(app.db.Model):
  id: int
  tgrefinement: int
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  tgrefinement = app.db.Column(app.db.Integer())
   
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs) 
    
@dataclass
class GRefinement(app.db.Model):
  id: int
  name: str
  graph: int
  filename: str
  is_none: bool
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  name = app.db.Column(app.db.String(70))
  graph = app.db.Column(app.db.Integer())
  filename = app.db.Column(app.db.String(25))
  is_none = app.db.Column(app.db.Boolean(), default=False)
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    
@dataclass
class Extraction(app.db.Model):
  id: int
  page: str
  name: str
  grefinement: int
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  page = app.db.Column(app.db.String(300))
  name = app.db.Column(app.db.String(70))
  grefinement = app.db.Column(app.db.Integer())
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
@dataclass
class Fetch(app.db.Model):
  id: int
  extraction: int
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  extraction = app.db.Column(app.db.Integer())
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
@dataclass
class Nerd(app.db.Model):
  id: int
  frefinement: int
  model: int
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  frefinement = app.db.Column(app.db.Integer())
  model = app.db.Column(app.db.Integer())
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
@dataclass
class Triplegen(app.db.Model):
  id: int
  nrefinement: int
  model: int
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  nrefinement = app.db.Column(app.db.Integer())
  model = app.db.Column(app.db.Integer())
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
@dataclass
class Tripleval(app.db.Model):
  id: int
  tgrefinement: int
  model: int
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  tgrefinement = app.db.Column(app.db.Integer())
  model = app.db.Column(app.db.Integer())
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
@dataclass
class FRefinement(app.db.Model):
  id: int
  fetch: int
  name: str
  filename: str
  is_none: bool
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  fetch = app.db.Column(app.db.Integer())
  name = app.db.Column(app.db.String(70))
  filename = app.db.Column(app.db.String(300))
  is_none = app.db.Column(app.db.Boolean(), default=False)
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
@dataclass
class NRefinement(app.db.Model):
  id: int
  nerd: int
  name: str
  filename: str
  is_none: bool
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  nerd = app.db.Column(app.db.Integer())
  name = app.db.Column(app.db.String(70))
  filename = app.db.Column(app.db.String(300))
  is_none = app.db.Column(app.db.Boolean(), default=False)
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
@dataclass
class TGRefinement(app.db.Model):
  id: int
  triplegen: int
  name: str
  filename: str
  is_none: bool
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  triplegen = app.db.Column(app.db.Integer())
  name = app.db.Column(app.db.String(70))
  filename = app.db.Column(app.db.String(300))
  is_none = app.db.Column(app.db.Boolean(), default=False)
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
@dataclass
class TERefinement(app.db.Model):
  id: int
  tripleval: int
  name: str
  filename: str
  is_none: bool
  
  id = app.db.Column(app.db.Integer(), primary_key=True)
  tripleval = app.db.Column(app.db.Integer())
  name = app.db.Column(app.db.String(70))
  filename = app.db.Column(app.db.String(300))
  is_none = app.db.Column(app.db.Boolean(), default=False)
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    
