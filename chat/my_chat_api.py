# 将本地接口在转为openApi接口
import requests
import ollama
import json


def api_generate(data):

    url = "http://localhost:11434/api/chat"
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=data, headers=headers, stream=True)

    for line in response.iter_lines():
        if line:
            chunk = line.decode('utf-8')
            chunk = json.loads(chunk)
            if not chunk['done']:
                print(chunk['message']['content'], end='', flush=True)
            else:
                print('\n')
                print('-----------------------------------------')
                print(f"总耗时：{chunk['total_duration']}")
                print('-----------------------------------------')


if __name__ == '__main__':
    # open api 请求参数
    base_data = {
        "stream": True,
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": '天空为什么是蓝色的？'
            }
        ]
    }

    # 流式输出
    api_generate(base_data)


    # open api 响应参数
    base_response = {
        "id": "chatcmpl-123",
        "object": "chat.completion.chunk",
        "created": 1694268190,
        "model": "gpt-4o-mini",
        "system_fingerprint": "fp_44709d6fcb",
        "choices": [{"index": 0, "delta": {}, "logprobs": None, "finish_reason": None}]
    }