from collections import Counter
class keywords:
    def __init__(self, words, dt, dr):
        self.words = words
        self.dt = dt
        self.dr = dr

    def _get_freq(self, words):
        return Counter(words)

    def get_keywords(self, num_word = 8, min_count = 2):
        
        words_freq = self._get_freq(self.words)
        
        dt_freq = self._get_freq(self.dt)
        dr_freq = self._get_freq(self.dr)
        
        dt_sum = sum(dt_freq.values())
        dr_sum = sum(dr_freq.values())
        
        keywords = []
        for word in set(self.words):
            if words_freq.get(word) < min_count:
                continue
            dt_score = dt_freq.get(word) / dt_sum
            dr_score = dr_freq.get(word, 0) /dr_sum
            score = dt_score / (dt_score + dr_score)
            keywords.append((word, score))
        keywords = sorted(keywords, key = lambda x:-x[1])
        keywords = [word for word, _ in keywords]
        return keywords[:num_word]
            
