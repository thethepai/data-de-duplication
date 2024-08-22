import jieba
import re
import hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datasketch import MinHash, MinHashLSH

from .dd_strategy import SimilarityStrategy

stopwords = {'的', '了', '和', '是', '在', '就', '不', '有', '也', '都', '上', '你', '我'}

class TokenizeTools:
    @staticmethod
    def chinese_tokenizer(tokens, caller=None):
        tokens = jieba.lcut(tokens)
        tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens]
        # tokens = [token for token in tokens if token not in self.stopwords]
        
        if caller == 'simhash':
            return tokens
        else:
            return ' '.join(tokens)

class Simhash:
    @staticmethod
    def simhash_128(text):
        words = TokenizeTools.chinese_tokenizer(text, caller='simhash')
        hash_bits = 128
        v = [0] * hash_bits
        
        for word in words:
            hash_value = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            for i in range(hash_bits):
                bitmask = 1 << i
                if hash_value & bitmask:
                    v[i] += 1
                else:
                    v[i] -= 1
        
        fingerprint = 0
        for i in range(hash_bits):
            if v[i] >= 0:
                fingerprint |= 1 << i
        
        return fingerprint

    @staticmethod
    def hamming_distance_similarity(simhash1, simhash2):
        hamming_distance = bin(simhash1 ^ simhash2).count('1')
        similarity = 1 - hamming_distance / 128
        return similarity

class TfidfSimilarity(SimilarityStrategy):
    def find_similar_pairs(self, articles, column_name, threshold, sub_string = True):
        ids = [article['id'] for article in articles]
        
        similar_pairs = []
        
        # TODO: repeate
        if sub_string:
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    if articles[i][column_name] in articles[j][column_name]:
                        similar_pairs.append({
                            'id1': ids[i],
                            'id2': ids[j],
                            'text1': articles[i][column_name],
                            'text2': articles[j][column_name]
                        })
            print(f"Found {len(similar_pairs)} similar records by substring.")
            
        texts = [TokenizeTools.chinese_tokenizer(article[column_name]) for article in articles]
        # calculate TF-IDF matrix
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        cosine_sim_matrix = cosine_similarity(tfidf_matrix) 
        
        print("your threshold is: ", threshold)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                sim_val = cosine_sim_matrix[i, j]
                # print(f"similarity between {ids[i]} and {ids[j]} is {sim_val}")
                if sim_val > threshold:
                    similar_pairs.append({
                        'id1': ids[i],
                        'id2': ids[j],
                        'text1': articles[i][column_name],
                        'text2': articles[j][column_name]
                    })
        
        return similar_pairs

class SimhashSimilarity(SimilarityStrategy):
    def find_similar_pairs(self, articles, column_name, threshold, sub_string = True):
        ids = [article['id'] for article in articles]
        
        similar_pairs = []
        
        # TODO: repeate
        if sub_string:
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    if articles[i][column_name] in articles[j][column_name]:
                        similar_pairs.append({
                            'id1': ids[i],
                            'id2': ids[j],
                            'text1': articles[i][column_name],
                            'text2': articles[j][column_name]
                        })
            print(f"Found {len(similar_pairs)} similar records by substring.")
        
        simhash_values = [Simhash.simhash_128(article[column_name]) for article in articles]
        
        print("your threshold is: ", threshold)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                sim_val = Simhash.hamming_distance_similarity(simhash_values[i], simhash_values[j])
                if sim_val > threshold:
                    # print(f"similarity between {ids[i]} and {ids[j]} is {sim_val}")
                    similar_pairs.append({
                        'id1': ids[i],
                        'id2': ids[j],
                        # 'text1': articles[i][column_name],
                        # 'text2': articles[j][column_name]
                    })
        
        return similar_pairs
    
class MinHashSimilarity(SimilarityStrategy):
    def find_similar_pairs(self, articles, column_name, threshold, sub_string = True):
        ids = [article['id'] for article in articles]
        
        similar_pairs = []
        
        # TODO: repeate
        if sub_string:
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    if articles[i][column_name] in articles[j][column_name]:
                        similar_pairs.append({
                            'id1': ids[i],
                            'id2': ids[j],
                            # 'text1': articles[i][column_name],
                            # 'text2': articles[j][column_name]
                        })
            print(f"Found {len(similar_pairs)} similar records by substring.")
            
        # minhash
        texts = [TokenizeTools.chinese_tokenizer(article[column_name]) for article in articles]
        
        lsh = MinHashLSH(num_perm=128, threshold = threshold)
        minhashes = {}
        
        # TODO: O(n)
        for i, tokens in enumerate(texts):
            minhash = MinHash(num_perm=128)
            for token in tokens:
                minhash.update(token.encode('utf8'))
            lsh.insert(ids[i], minhash)
            minhashes[ids[i]] = minhash

        for i in range(len(ids)):
            result = lsh.query(minhashes[ids[i]])
            for j in result:
                if ids[i] != j:
                    similar_pairs.append({
                        'id1': ids[i],
                        'id2': j,
                        # 'text1': articles[i][column_name],
                        # 'text2': next(article[column_name] for article in articles if article['id'] == j)
                    })
            
        return similar_pairs