import csv
import os
import torch
from transformers import pipeline

clean_path = os.path.realpath
current_folder = os.path.dirname(__file__)

INPUT_FILE  = clean_path(current_folder+'\\..\\wikipedia\\tripleval\\scoring_dataset.csv')
OUTPUT_FILE = clean_path(current_folder+'\\..\\wikipedia\\tripleval\\scored_dataset.csv')

device = "cuda:0" if torch.cuda.is_available() else "cpu"

if torch.cuda.is_available():
      classifier = pipeline("zero-shot-classification",
                             model="facebook/bart-large-mnli", device=0)#.to(device)    
else:
      classifier = pipeline("zero-shot-classification",
                            model="facebook/bart-large-mnli")#, device=0)#.to(device)

quality_labels = ['Bad', 'Mediocre', 'Good']
certainty_labels = ['NotSure', 'Sure']


with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
  writer = csv.writer(f)
  
  with open(INPUT_FILE, 'r', encoding='utf-8') as g:
    reader = csv.reader(g)
    
    for row in reader:
      
      certainty = classifier(f"From the text '{row[0]}' we can infer that '{row[1]}'", certainty_labels)['labels'][0]
      quality   = classifier(f"From the text '{row[0]}' we can infer that '{row[1]}'", quality_labels)['labels'][0]
      
      print(row[0] + '\n' + row[1] + '\n' + f'{certainty}, {quality} \n\n\n')
      writer.writerow([row[0], row[1], quality, certainty])
      