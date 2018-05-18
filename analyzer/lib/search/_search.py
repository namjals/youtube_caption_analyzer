import os
from collections import Counter
from lib.utils import load_binary
from lib.utils import load_json
from lib.utils import path

download_path = path['download']
analysis_path = path['analysis']
indexer_path =path['index']['pkl']

def search_index(words):    
    indexer = load_binary(indexer_path)    
    result = Counter()
    for word in words.split():
        word = word.lower() #lowercase search
        if word in indexer:
            result += Counter(indexer.get(word))    
    return [video_id for video_id, _ in result.most_common()]    

def search(words):
    result = []    
    download = load_json(download_path)
    analysis = load_json(analysis_path)
    for video_id in search_index(words):
        item = {}
        item['title'] = download[video_id]['title']
        item['description'] = download[video_id]['description']
        item['trackKind'] = download[video_id].get('trackKind', 'None')
        item['keywords'] = analysis[video_id]['keywords']
        item['link'] = 'https://www.youtube.com/watch?v='+video_id
        result.append(item)
    return result
    

    
