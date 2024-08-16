import jieba
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def chinese_tokenizer(text):
    return jieba.lcut(text)

text1 = "比特币失手5万美元大关"
text2 = "比特币失手51000美元/枚，日内跌幅12.42%。"

tokens1 = chinese_tokenizer(text1)
tokens2 = chinese_tokenizer(text2)
print("分词结果：")
print(tokens1)
print(tokens2)

processed_text1 = ' '.join(tokens1)
processed_text2 = ' '.join(tokens2)

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform([processed_text1, processed_text2])

print("TF-IDF 矩阵：")
print(tfidf_matrix.toarray())

# 计算余弦相似度
cosine_sim = cosine_similarity(tfidf_matrix)
print("余弦相似度矩阵：")
print(cosine_sim)
for i in range(len(cosine_sim)):
    for j in range(len(cosine_sim[i])):
        print(f"文本{i+1}和文本{j+1}的余弦相似度: {cosine_sim[i][j]}")