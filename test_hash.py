import hashlib
import jieba

def simhash(text):
    words = jieba.lcut(text)
    print(words)
    
    hashes = [hashlib.md5(word.encode('utf-8')).hexdigest() for word in words]
    
    # 计算simhash值
    simhash_value = sum([(1 if h[i] == '1' else -1) for h in hashes for i in range(32)])
    
    return simhash_value

def similarity(text1, text2):
    simhash1 = simhash(text1)
    simhash2 = simhash(text2)
    
    # 计算汉明距离
    hamming_distance = bin(simhash1 ^ simhash2).count('1')
    
    # 计算相似度
    similarity = 1 - hamming_distance / 64
    
    return similarity

# 测试
text1 = "比特币失手5万美元大关"
text2 = "比特币失手51000美元/枚，日内跌幅12.42%。"
similarity_score = similarity(text1, text2)
print(f"两个句子的相似性: {similarity_score}")