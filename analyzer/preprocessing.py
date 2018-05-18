

import json
import pickle
import sys

from soynlp.utils import DoublespaceLineCorpus
from soynlp.hangle import normalize

from lib.utils import Corpus
from lib.utils import load_json, save_json
from lib.utils import path


def normalizing(forced = False):

    download_path = path['download']
    analysis_path = path['analysis']
    normed_path = path['norm']
    
    download = load_json(download_path)
    analysis = load_json(analysis_path)

    with open(normed_path, 'w', encoding='utf8') as f:   
        for video_id, content in download.items():
            state = content.get('state', 'new')
            if state == 'new' or state == 'update' or forced:              
                
                norm_title = normalize(content.get('title','').lower(), english = True, number=True, punctuation=False, remains = {'+','#'})
                norm_description = normalize(content.get('description','').lower(), english = True, number=True, punctuation=False, remains = {'+','#'})
                norm_caption = normalize(content.get('caption','').lower(), english = True, number=True, punctuation=False, remains = {'+','#'})
                f.write('{}\n'.format(norm_title + norm_description + norm_caption))
                
                analysis[video_id] = {}
                
                norm = {}
                    
                norm['title'] = norm_title
                norm['description'] = norm_description
                norm['caption'] = norm_caption
                norm['trackKind'] = content.get('trackKind', '')
                analysis[video_id]['norm'] = norm
        save_json(analysis, analysis_path)


