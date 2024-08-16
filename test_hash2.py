import hashlib
import jieba
import re

HASHNUM = 64

def chinese_tokenizer(tokens, caller=None):
    tokens = jieba.lcut(tokens)
    tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens]
    if caller == 'find_similar_pairs':
        return ' '.join(tokens)
    elif caller == 'simhash':
        return tokens
    else:
        return ' '.join(tokens)

def simhash_128(text):
    words = jieba.lcut(text)
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
    print(f"Hamming distance: {hamming_distance}")
    similarity = 1 - hamming_distance / HASHNUM
    return similarity

def find_similar_pairs(articles, column_name, threshold):
    ids = [article['id'] for article in articles]
    similar_pairs = []
    simhash_values = []
    for article in articles:
        value = simhash_64(article[column_name])
        print(f"Simhash fingerprint for article: {value}")
        simhash_values.append(value)
    
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            dis = hamming_distance_similarity(simhash_values[i], simhash_values[j])
            print(dis)
            if dis > threshold:
                similar_pairs.append({
                    'id1': ids[i],
                    'id2': ids[j],
                    'text1': articles[i][column_name],
                    'text2': articles[j][column_name]
                })
    
    return similar_pairs

def main():
    articles = [
        {'id': 1, 'content': '工银投资成立绿能股权投资合伙企业 出资额75亿'},
        {'id': 2, 'content': '工银于近日投资成立了绿能股权投资合伙企业 出资额75亿'},
    ]
    threshold = 0.8
    similar_pairs = find_similar_pairs(articles, 'content', threshold)
    for pair in similar_pairs:
        print(f"ID1: {pair['id1']}, ID2: {pair['id2']}")
        print(f"Text1: {pair['text1']}")
        print(f"Text2: {pair['text2']}")
        print('---')

if __name__ == "__main__":
    main()