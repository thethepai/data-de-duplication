import hashlib
import jieba
import re

def chinese_tokenizer(tokens):
    tokens = jieba.lcut(tokens)
    tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens]
    
    return tokens
    

def simhash(text):
    # 分词并去除标点符号
    words = chinese_tokenizer(text)
    # 初始化向量
    v = [0] * 256
    for word in words:
        # 计算每个词的hash值
        hash_value = int(hashlib.sha256(word.encode('utf-8')).hexdigest(), 16)
        for i in range(256):
            bitmask = 1 << i
            if hash_value & bitmask:
                v[i] += 1
            else:
                v[i] -= 1
    # 生成SimHash指纹
    fingerprint = 0
    for i in range(256):
        if v[i] > 0:
            fingerprint |= 1 << i
    return fingerprint

def hamming_distance(hash1, hash2):
    x = hash1 ^ hash2
    tot = 0
    while x:
        tot += 1
        x &= x - 1
    return tot

# 示例文本
text1 = "工银投资成立绿能股权投资合伙企业 出资额75亿"
text2 = "工银于近日投资成立了绿能股权投资合伙企业 出资额75亿"

# 计算SimHash指纹
hash1 = simhash(text1)
hash2 = simhash(text2)

# 计算海明距离
distance = hamming_distance(hash1, hash2)

print(f"SimHash of text1: {hash1}")
print(f"SimHash of text2: {hash2}")
print(f"Hamming Distance: {distance}")