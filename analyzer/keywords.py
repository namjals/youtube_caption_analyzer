

import gensim

from lib.keywords import keywords
from lib.utils import CorpusGensim
from lib.utils import load_json, save_json
from lib.utils  import path

def make_doc2vec_src(analysis_path, doc2vec_src_path):
    with open(doc2vec_src_path, 'w', encoding='utf8') as f:
        for video_id, content in load_json(analysis_path).items():
            f.write('{}\n'.format(content['nouns']['all']))

def get_similarity(corpus, model,words, start, end):
    if start <= 1 and start >= 0:
        start = int(len(corpus) * start)
    if end <= 1 and end >= 0:
        end = int(len(corpus) * end)
    
    inferred_vector = model.infer_vector(words)
    sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))   
    result = []
    for rank in range(start, end):
        if corpus[sims[rank][0]].words != words:
            result += corpus[sims[rank][0]].words
    return result
#make_doc2vec_src(path['analysis'], path['doc2vec']['src'])
def train():
    analysis_path = path['analysis']
    doc2vec_src_path = path['doc2vec']['src']
    doc2vec_model_path = path['doc2vec']['model']

    make_doc2vec_src(analysis_path, doc2vec_src_path)   
    corpus = list(CorpusGensim(doc2vec_src_path))   

    model = gensim.models.doc2vec.Doc2Vec(vector_size=150, min_count=2, epochs=55)
    model.build_vocab(corpus)

    model.train(corpus, total_examples=model.corpus_count, epochs=model.epochs)
    model.save(doc2vec_model_path)


def update(forced = False):

    download_path = path['download']
    analysis_path = path['analysis']
    doc2vec_src_path = path['doc2vec']['src']
    doc2vec_model_path = path['doc2vec']['model']

    download = load_json(download_path)
    analysis = load_json(analysis_path)

    model = gensim.models.doc2vec.Doc2Vec
    model = model.load(doc2vec_model_path)
    corpus = list(CorpusGensim(doc2vec_src_path))
    
    for video_id, content in download.items():
        state = content.get('state', 'new')
        if state == 'new' or state == 'update' or forced:                
            words = analysis[video_id]['nouns']['all'].split()
            dt = get_similarity(corpus, model, words,0,0.1) + words
            dr = get_similarity(corpus, model, words,0.9,1)# + words
            keyword = keywords(words, dt, dr).get_keywords(10, 2)
            
            analysis[video_id]['keywords'] = ' '.join(keyword)
            
    save_json(analysis, analysis_path)


