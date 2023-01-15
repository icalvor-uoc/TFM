import csv
import app.triplegen as triplegen
import os

clean_path = os.path.realpath

DATASET_FOLDER = 'C:\\Users\\calvo\\TFM\\wikipedia\\'

MODELS = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Zeta']

DEST_FILE = clean_path(DATASET_FOLDER+'tripleval\\template.csv')

with open(DEST_FILE, 'w', newline='', encoding='utf-8') as f:
  writer = csv.writer(f)
  
  for model in MODELS:
    FOLDER = DATASET_FOLDER+'triplegen\\'+model+'\\'
    FILE   = clean_path(DATASET_FOLDER+'triplegen\\'+model+'.csv')
    
    with open(FILE, 'r', encoding='utf-8') as g:
      reader = csv.reader(g)
    
      for row in reader:
        
        try:
          TRIPLEGEN_FILE = clean_path(FOLDER+row[2]+'.ttl')
          units = triplegen.Triplegen(filename=TRIPLEGEN_FILE).units
          print(TRIPLEGEN_FILE)
          for unit in units:
           writer.writerow( [unit.evidence, unit.description] )
           
        except Exception as e:
          print(e)