

import collections
from collections import Counter
import math
import os

from lib.utils import load_binary, save_binary
from lib.utils import load_json, save_json

from lib.utils  import path

def add_item(indexer, video_id, contents):
    for word, count in Counter(contents).items():   
        word = word.lower() #lowercase indexing
        if word in indexer:
            if video_id in indexer[word]:
                 indexer[word][video_id] += count
            else:
                 indexer[word][video_id] = count
        else:
            indexer[word] = {}
            indexer[word][video_id] = count
            
def delete_item(indexer, video_id):
    for word, v_id_count in indexer.items():
        if video_id in v_id_count:
            del v_id_count[video_id]

def update(t_weight = 6, d_weight = 3, c_weight = 1, forced = False):

    download_path = path['download']
    analysis_path = path['analysis']
    index_path = path['index']['pkl']
    index_readable_path = path['index']['readable']


    indexer = load_binary(index_path)
    indexer_readable = load_json(index_readable_path)
    download = load_json(download_path)
    analysis = load_json(analysis_path)

    total_count = Counter()
    id_noun_count = {}   
        

    for video_id, content in download.items():
        title = analysis[video_id]['nouns']['title'].split() * t_weight
        description = analysis[video_id]['nouns']['description'].split() * d_weight
        caption = analysis[video_id]['nouns']['caption'].split() * c_weight
        
        state = content.get('state')    
                    
        if state == 'update' or forced:            
            delete_item(indexer, video_id)
            add_item(indexer, video_id, title + description + caption)
            download[video_id]['state'] = 'complete'
        elif state == 'new':                
            add_item(indexer, video_id, title + description + caption)
            download[video_id]['state'] = 'complete'
        

    save_binary(indexer, index_path)
    save_json(indexer, index_readable_path)
    save_json(download, download_path)


