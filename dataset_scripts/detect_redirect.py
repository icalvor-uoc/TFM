import os

SOURCE_PATH = 'C:\\users\\calvo\\desktop\\wikipedia'
LOG_PATH = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\raw_files.txt'

BASE_DIR = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\raw_flat\\'

with open(BASE_DIR+'AAAHH!!!_Real_Monsters!_2790.html', 'r', encoding='utf-8') as f:
  print(f.read().find('http-equiv="Refresh"'))