import hashlib
import jieba
import re

def chinese_tokenizer(tokens, caller=None):
    tokens = jieba.lcut(tokens)
    tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens]
    if caller == 'find_similar_pairs':
        return ' '.join(tokens)
    elif caller == 'simhash':
        return tokens
    else:
        return ' '.join(tokens)

def simhash(text):
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

def hamming_distance_similarity(simhash1, simhash2):
    hamming_distance = bin(simhash1 ^ simhash2).count('1')
    similarity = 1 - hamming_distance / 128
    return similarity

def find_similar_pairs(articles, column_name, threshold):
    ids = [article['id'] for article in articles]
    similar_pairs = []
    simhash_values = [simhash(article[column_name]) for article in articles]
    
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
        {'id': 3, 'content': '预告：国家卫生健康委就“时令节气与健康”举行发布会'},
        {'id': 4, 'content': '财联社8月5日电，市场预计欧洲央行今年将进一步降息逾90个基点，高于上周五尾盘的约70个基点和上周初的50个基点。'}
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