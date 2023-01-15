import glob
import os
import shutil

SOURCE_PATH = 'C:\\users\\calvo\\desktop\\wikipedia'
DEST_PATH = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\raw_flat\\'
LOG_PATH = os.path.dirname(os.path.realpath(__file__))+'\\..\\wikipedia\\raw_files.txt'

ABC = 'abcdefghijklmnopqrstuvwxyz'

START_1 = 'a'
START_2 = 'g'
START_3 = 's' # ado, agr failed


with open(LOG_PATH, 'a', encoding='utf-8') as f:
    for i in range(ABC.index(START_1), len(ABC)):
      for j in range(ABC.index(START_2), len(ABC)):
        for k in range(ABC.index(START_3), len(ABC)):
          print(f'{ABC[i]}{ABC[j]}{ABC[k]}')
          files = glob.glob(SOURCE_PATH+f'\\{ABC[i]}\\{ABC[j]}\\{ABC[k]}\\*')
          for file in files:
            filename = file.replace('\\', '/').split('/')[-1]
            if len(filename) > 80:
              continue
            f.write(f'{ABC[i]}{ABC[j]}{ABC[k]} - {filename}\n')
            # print(f'{ABC[i]}{ABC[j]}{ABC[k]} - {filename}')
            shutil.copy(file, DEST_PATH+filename)