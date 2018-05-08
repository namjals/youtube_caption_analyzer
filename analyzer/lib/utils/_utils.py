import gensim
import json
import pickle
import smart_open
import os

directory = '/'.join(os.path.abspath(__file__).replace('\\', '/').split('/')[:-3])
path = {
    'download' : 'data/Download.json',
    'norm' : 'data/Normalization',
    'word' : {
        'train' : {
            'pkl' : 'data/WordTrained.pkl',
            'readable' : 'data/WordTrained.json',
            },
        'result' : 'data/Word.json'
        },
    'noun' :  {
        'train' : {
            'pkl':'data/NounTrained.pkl',
            'readable' : 'data/WordTrained.json'
            },
        'src' : 'data/NounSrc.src',
        'lrgraph' : 'data/NounLRGraph.json',
        'result' : 'data/Noun.json'
        
        },
    'user_dictionary' : 'data/UserDictionary.txt', #파일
    'analysis' : 'data/Analysis.json',
    'doc2vec' : {
        'src' : 'data/Doc2Vec.src',
        'model' : 'data/Doc2Vec.model'        
        },
    'index' : {
        'pkl' : 'data/Index.pkl',
        'readable' : 'data/Index.json'
        }
    
    }

class Corpus:
    def __init__(self, fname, gensim_tagging = False):
        self.fname = fname
        self.gensim_tagging = gensim_tagging
        self.length = 0
        
    def __iter__(self):
        with open(self.fname, encoding='utf-8') as f:
            for doc in f:
                #if 'C++' in f:
                    #print('C++ is exist!')
                yield doc.strip()
    def __len__(self):
        if self.length == 0:
            with open(self.fname, encoding='utf-8') as f:
                for n_doc, _ in enumerate(f):
                    continue
                self.length = (n_doc + 1)
        return self.length

class CorpusGensim(Corpus):
    def __init__(self, fname, tokens_only = False):
        self.fname = fname
        self.tokens_only = tokens_only
        self.length = 0
        
    def __iter__(self):
        with smart_open.smart_open(self.fname, encoding='utf8') as f:        
            for i, line in enumerate(f):
                if self.tokens_only:
                    yield gensim.utils.simple_preprocess(line)
                else:
                    # For training data, add tags                    
                    #yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])
                    yield gensim.models.doc2vec.TaggedDocument(line.split(), [i])
                
                
def load_json(path):    
    directory, _ = os.path.split(path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)        
    if not os.path.isfile(path):
        with open(path, 'w', encoding = 'utf8') as f:
            json.dump({},f,indent = 4, ensure_ascii=False)
    with open(path, 'r', encoding = 'utf8') as f:
        json_file = json.load(f)
    return json_file

def save_json(obj, path):
    with open(path, 'w', encoding = 'utf8') as f:
        json.dump(obj,f,indent = 4, ensure_ascii=False)


def load_binary(path):
    directory, _ = os.path.split(path)
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)        
    if not os.path.isfile(path):
        with open(path, 'wb') as f:            
            pickle.dump({},f)
    with open(path, 'rb') as f:
        binary_file = pickle.load(f)
    return binary_file

def save_binary(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj,f)
        
def get_depth_dict(dict_val, keys, default= None):    
    for key in keys:
        if key in dict_val:
            dict_val = dict_val.get(key)
        else:
            return default
    return dict_val

def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        try:
            initializer = next(it)
        except StopIteration:
            raise TypeError('reduce() of empty sequence with no initial value')
    accum_value = initializer
    for x in it:
        accum_value = function(accum_value, x)
    return accum_value
