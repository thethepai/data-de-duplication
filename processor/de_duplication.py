import time
import logging
import jieba
import re
import hashlib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

THRESHOLD = 0.7
# tfidf or simhash
# METHOD = 'simhash'
METHOD = 'simhash_64'
# METHOD = 'tfidf'
stopwords = {'的', '了', '和', '是', '在', '就', '不', '有', '也', '都', '上', '你', '我'}
    
def chinese_tokenizer(tokens, caller=None):
    
    tokens = jieba.lcut(tokens)
    tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens]
    # tokens = [token for token in tokens if token not in stopwords]
    
    if caller == 'simhash':
        return tokens
    else:
        return ' '.join(tokens)

def simhash_128(text):
    words = chinese_tokenizer(text, caller='simhash')
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

import hashlib

def simhash_64(text):
    words = chinese_tokenizer(text, caller='simhash')
    hash_bits = 64
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

def hamming_distance_similarity(simhash1, simhash2):
    hamming_distance = bin(simhash1 ^ simhash2).count('1')
    similarity = 1 - hamming_distance / 128
    return similarity

def split_simhash(simhash_value, parts=4):
    """Split the simhash value into the specified number of parts."""
    part_length = len(simhash_value) // parts
    return [simhash_value[i * part_length:(i + 1) * part_length] for i in range(parts)]

def find_similar_pairs(articles, column_name, threshold, method='tfidf'):
    ids = [article['id'] for article in articles]
    
    similar_pairs = []
    
    if method == 'tfidf':
        texts = [chinese_tokenizer(article[column_name]) for article in articles]
        # calculate TF-IDF matrix
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        
        cosine_sim_matrix = cosine_similarity(tfidf_matrix) 
        
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                if cosine_sim_matrix[i, j] > threshold:
                    similar_pairs.append({
                        'id1': ids[i],
                        'id2': ids[j],
                        'text1': articles[i][column_name],
                        'text2': articles[j][column_name]
                    })
    elif method == 'simhash':
        simhash_values = [simhash_128(article[column_name]) for article in articles]
        
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                if hamming_distance_similarity(simhash_values[i], simhash_values[j]) > threshold:
                    similar_pairs.append({
                        'id1': ids[i],
                        'id2': ids[j],
                        'text1': articles[i][column_name],
                        'text2': articles[j][column_name]
                    })
    elif method == 'simhash_64':
        simhash_values = [simhash_64(article[column_name]) for article in articles]
        parts_dict = [{} for _ in range(4)]
        
        for i, simhash_value in enumerate(simhash_values):
            parts = split_simhash(simhash_value)
            for part_index, part in enumerate(parts):
                if part in parts_dict[part_index]:
                    for j in parts_dict[part_index][part]:
                        similar_pairs.append({
                            'id1': ids[i],
                            'id2': ids[j],
                            'text1': articles[i][column_name],
                            'text2': articles[j][column_name]
                        })
                    parts_dict[part_index][part].append(i)
                else:
                    parts_dict[part_index][part] = [i]
    
    return similar_pairs

def dd_similarity(connection, column_name):
    start_time = time.time()
    deletion_time = None
    deleted_count = 0
    
    logging.basicConfig(
        filename=f'Similarity_log_.txt',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )

    try:
        with connection.cursor() as cursor:
            # set cursor to return dictionary
            cursor = connection.cursor(dictionary=True)
            
            select_query = f"SELECT id, {column_name} FROM articles_info"
            cursor.execute(select_query)
            articles = cursor.fetchall()
        
            similar_pairs = find_similar_pairs(articles, column_name, THRESHOLD, method = METHOD)
            
            logging.info(f"Found {len(similar_pairs)} similar records.")
            
            record = 1
            for pair in similar_pairs:
                logging.info(f"pair NO.{record}")
                logging.info(f"Similarity: {pair['id1']} and {pair['id2']}")
                logging.info(f"Text 1: {pair['text1']}")
                logging.info(f"Text 2: {pair['text2']}")
                logging.info("------")
                record += 1
            
            # delete similar records
            for pair in similar_pairs:
                delete_query = f"DELETE FROM articles_info WHERE id = {pair['id2']}"
                cursor.execute(delete_query)
                deleted_count += cursor.rowcount
            
            deletion_time = time.time() - start_time
            
        connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"Deletion time: {deletion_time} seconds")
    print(f"Total records deleted: {deleted_count}")
    print(f"Total time taken: {total_time} seconds")