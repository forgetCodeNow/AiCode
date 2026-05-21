import tiktoken


# 获取大模型对应的分词器
tokenizer = tiktoken.encoding_for_model('gpt-3.5-turbo')
print(tokenizer.name)

# 直接使用分词器名闯将
# tokenizer2 = tiktoken.get_encoding('cl100k_base')

# 使用分词器得到向量
res1 = tokenizer.encode('i am a boy')
res2 = tokenizer.encode('Tom cannot to complete this task')
res3 = tokenizer.encode('你是什么人?')


# 根据向量还原本文
print(tokenizer.decode(res1))

# 把每个向量元素还原成单个文本
words =  [tokenizer.decode_single_token_bytes(token) for token in res3]
print(words)