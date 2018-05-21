

import abc
from collections import Counter
import math
import os

from lib.utils import get_depth_dict
from lib.utils import load_binary, save_binary
from lib.utils import load_json, save_json
from lib.utils import path
from lib.utils import runtime

class Indexer(metaclass=abc.ABCMeta):
    
    download_path = path['download']
    analysis_path = path['analysis']
    index_path = path['index']['pkl']
    index_readable_path = path['index']['readable']    
    
    _indexer = None
    _download = None
    _analysis = None
    
    @staticmethod
    def loader():        
        if not Indexer._indexer:
            Indexer._indexer = load_binary(Indexer.index_path)
        if not Indexer._download:
            Indexer._download = load_json(Indexer.download_path)
        if not Indexer._analysis:
            Indexer._analysis = load_json(Indexer.analysis_path)   
    
    @abc.abstractmethod
    def _add_item(self, indexer, video_id, contents):
        pass
    
    @abc.abstractmethod
    def _delete_item(self, indexer, video_id):
        pass
    
    #@runtime    
    def update(self, t_weight = 6, d_weight = 3, c_weight = 1, forced = False):
        indexer = load_binary(self.index_path)
        indexer_readable = load_json(self.index_readable_path)
        download = load_json(self.download_path)
        analysis = load_json(self.analysis_path)

        total_count = Counter()
        id_noun_count = {}   

        for video_id, content in download.items():
            title = analysis[video_id]['nouns']['title'].split() * t_weight
            description = analysis[video_id]['nouns']['description'].split() * d_weight
            caption = analysis[video_id]['nouns']['caption'].split() * c_weight

            state = content.get('state')    

            if state == 'update' or forced:            
                self._delete_item(indexer, video_id)
                self._add_item(indexer, video_id, title + description + caption)
                download[video_id]['state'] = 'complete'
            elif state == 'new':                
                self._add_item(indexer, video_id, title + description + caption)
                download[video_id]['state'] = 'complete'

        save_binary(indexer, self.index_path)
        save_json(indexer, self.index_readable_path)
        save_json(download, self.download_path)
        self._indexer = load_binary(self.index_path)
    
    @abc.abstractmethod
    def _search_index(self, words):
        pass
    
    #@runtime    
    def search(self, words):
        Indexer.loader()
        result = []    
        download = self._download
        analysis = self._analysis
        for video_id in self._search_index(words):
            item = {}
            item['title'] = download[video_id]['title']
            item['description'] = download[video_id]['description']
            item['trackKind'] = download[video_id].get('trackKind', 'None')
            item['keywords'] = analysis[video_id]['keywords']
            item['link'] = 'https://www.youtube.com/watch?v='+video_id
            result.append(item)
        return result

class IndexerDict(Indexer):  

    #indexer = {word_1 : {video_1 : count, video_2 : count... }, word_2: {}... }
    def _add_item(self, indexer, video_id, contents):
        for word, count in Counter(contents).items():   
            if word in indexer:
                if video_id in indexer[word]:
                     indexer[word][video_id] += count
                else:
                     indexer[word][video_id] = count
            else:
                indexer[word] = {}
                indexer[word][video_id] = count

    def _delete_item(self, indexer, video_id):
        for word, v_id_count in indexer.items():
            if video_id in v_id_count:
                del v_id_count[video_id]

    def update(self, t_weight = 6, d_weight = 3, c_weight = 1, forced = False):
        super().update(t_weight, d_weight, c_weight, forced)

    def _search_index(self, words):    
        indexer = self._indexer   
        result = Counter()
        for word in words.split():
            word = word.lower() #lowercase search
            
            for key,val in indexer.items():#O(n), startswith search
                if key.startswith(word): 
                    result += Counter(indexer.get(key, {}))
                    
#             result += Counter(indexer.get(word, {})) # O(1), search == index
        return [video_id for video_id, _ in result.most_common()]    
    
    def search(self, words):
        return super().search(words)
        

class IndexerTrie(Indexer):
    
    #indexer = {char_1 : {"*" : {video_1 : count, video_2 : count...}, char_2 : {"*" : {video_1 : count, ...}} } }
    def _add_item(self, indexer, video_id, contents):
        for word, count in Counter(contents).items():  
            
            cur = indexer
            
            for ch in word:
                if ch not in cur:
                    cur[ch] = {}
                cur = cur[ch]
                
                #'*' : A separation point between char and videoID.
                if '*' not in cur:
                    cur['*'] = {}

                if video_id not in cur['*']:
                    cur['*'][video_id] = count
                else:
                    cur['*'][video_id] += count            
            
    
    def _delete_item(self, indexer, video_id):
        for k, v in indexer.items():
            if isinstance(v, dict) :
                if get_depth_dict(v, ('*', video_id), False):
                    del v['*'][video_id]
                self._delete_item(v, video_id)
        
    
    def update(self, t_weight = 6, d_weight = 3, c_weight = 1, forced = False):
        super().update(t_weight, d_weight, c_weight, forced)
    
    def _search_index(self, words):
        indexer = self._indexer   
        result = Counter()
        for word in words.split():
            word = word.lower() #lowercase search

            cur = indexer
            for ch in word: #O(m)
                if ch not in cur:
                    continue
                cur = cur[ch]   
            
            result += Counter(cur.get('*', {}))
        return [video_id for video_id, _ in result.most_common()]
    
    def search(self, words):
        return super().search(words)    
    


if __name__=='__main__':
    words = ['프로', 'c++', 'c#', 'c', '프로그래밍', '야근', '하드웨어', '저수준', '포프']
    
    def make_indexer(indexer):
        if os.path.isfile(path['index']['pkl']):
            os.remove(path['index']['pkl'])
        if os.path.isfile(path['index']['readable']):
            os.remove(path['index']['readable'])
        index = indexer()
        
        index.update(forced = True)   
        index.loader()
    
    def check_indexer(indexer, words):      
        for word in words:
            #print("word : {}".format(word))
            indexer().search(word)    
    get_ipython().magic('timeit make_indexer(IndexerDict)')
    len(IndexerDict().search('c++'))
    get_ipython().magic('timeit check_indexer(IndexerDict, words) #O(1)')
    get_ipython().magic('timeit check_indexer(IndexerDict, words) #O(n)')
    get_ipython().magic('timeit make_indexer(IndexerTrie)')
    get_ipython().magic('timeit check_indexer(IndexerTrie, words) #O(m)')
    len(IndexerTrie().search('c++'))


