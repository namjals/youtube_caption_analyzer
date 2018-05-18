

import json
import pickle
import re
import os

from soynlp.utils import DoublespaceLineCorpus
from soynlp.noun import LRNounExtractor    

from lib.komoran import Komoran
from lib.utils import load_json, save_json
from lib.utils import path


def update_user_dict():
    user_dict_path = path['user_dictionary']
    soynlp_noun_path = path['noun']['result']    
    
    user_dict = set()
    if not os.path.isfile(user_dict_path):    
        open(user_dict_path, 'a').close()
    with open(user_dict_path, 'r', encoding='utf8') as nouns:
        for noun in nouns:
            user_dict.add(noun.split()[0].strip())

    with open(soynlp_noun_path,'r',encoding='utf8') as f:
        nouns = json.load(f)
        
    for noun in nouns:
        if re.search('[a-zA-Z]', noun):
            user_dict.add(noun)
            
    with open(user_dict_path, 'w', encoding='utf8') as f:
        for noun in user_dict:
            f.write('{}\t{}\n'.format(noun,'NNP'))

def train():

    normed_path = path['norm']

    noun_src_path = path['noun']['src']
    noun_lrgraph_path = path['noun']['lrgraph']
    noun_trained_path = path['noun']['train']['pkl']
    noun_readable_path = path['noun']['train']['readable']
    noun_result_path = path['noun']['result']


    corpus = DoublespaceLineCorpus(normed_path, iter_sent=True)

    noun_extractor = LRNounExtractor(verbose = False, min_num_of_features = 1)
    nouns = noun_extractor.train_extract(corpus, minimum_noun_score=0.5)

    word_freq = noun_extractor._wordset_l_counter
    lrgraph = noun_extractor.lrgraph
    words = noun_extractor.words

    trained_data = {}
    trained_data['lrgraph'] = lrgraph
    trained_data['words'] = words
    trained_data['word_freq'] = word_freq


    with open(noun_src_path, 'wb') as f:
        pickle.dump(trained_data, f)   

    with open(noun_lrgraph_path, 'w', encoding = 'utf8') as f:
        json.dump(lrgraph, f, ensure_ascii = False, indent = 4)
        
    params = {}
    for noun, noun_score in nouns.items():  
        params[noun] = {'frequency' : noun_score.frequency, 'score' : noun_score.score, 'known_r_ratio' : noun_score.known_r_ratio} 

    with open(noun_trained_path, 'wb') as f:
        pickle.dump(params, f)
        
    with open(noun_readable_path, 'w', encoding = 'utf8') as f:
        json.dump(sorted(params.items()), f, ensure_ascii = False, indent = 4)   

    with open(noun_result_path, 'w', encoding = 'utf8') as f:
        json.dump(sorted(params), f, ensure_ascii = False, indent = 4)

    update_user_dict()
    update(forced = True)


def update(forced = False):
    def get_nouns(text):
        nouns = komoran3.nouns(text)
        return [noun for noun in nouns if len(noun) > 1 and not noun.isnumeric()]
    
    
    user_dict_path = path['user_dictionary']
    
    komoran3 = Komoran('./lib/komoran/komoran/models', './lib/komoran/komoran/libs')
    komoran3.set_user_dictionary(user_dict_path)
    
    download_path = path['download']
    analysis_path = path['analysis']
    
    download = load_json(download_path)
    analysis = load_json(analysis_path)
    
    for video_id, content in download.items():
        state = content.get('state', 'new')
        if state == 'new' or state == 'update' or forced:
            
            norm = analysis[video_id]['norm']
            
            nouns = {}                
            nouns['title'] = ' '.join(get_nouns(norm.get('title', '')))
            nouns['description'] = ' '.join(get_nouns(norm.get('description', '')))
            nouns['caption'] = ' '.join(get_nouns(norm.get('caption', '')))
            nouns['all'] = nouns['title'] + ' ' + nouns['description'] + ' ' + nouns['caption'] 
            
            analysis[video_id]['nouns'] = nouns

    save_json(analysis, analysis_path)


            


