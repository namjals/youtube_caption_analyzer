import json
import pickle
import sys

from soynlp.utils import DoublespaceLineCorpus
from soynlp.hangle import normalize

from lib.utils import path
from lib.utils import Corpus

def normalizing():

    download_path = path['download']
    normed_path = path['norm']
    
    with open(download_path,'r',encoding='utf8') as f:
        download = json.load(f)    

    with open(normed_path, 'w', encoding='utf8') as f:    
        for index, info in enumerate(download.values()):
            contents = info.get('title','') + info.get('description','') + info.get('caption','')
            norm_contents = normalize(contents, english = True, number=True, punctuation=False, remains = {'+','#'})
            f.write('{}\n'.format(norm_contents))

