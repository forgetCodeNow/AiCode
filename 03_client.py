from langserve import RemoteRunnable

if __name__ == '__main__':
    client = RemoteRunnable(url='http://localhost:8000/chainDemo')
    print(client.invoke({'language': 'english', 'text': '你好！'}))