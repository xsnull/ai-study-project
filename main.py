import json
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests

app = FastAPI()


class ChatRequest(BaseModel):
    model: str
    messages: list
    stream: bool


# openai 接口适配器
@app.post("/chat/completions")
async def root(request: ChatRequest, background_tasks: BackgroundTasks):
    print(f"接受请求：{request.stream}")

    url = "http://localhost:11434/api/chat"
    data = {
        "model": 'qwen2.5:7b',
        "messages": request.messages,
        "stream": request.stream
    }
    headers = {'Content-Type': 'application/json'}
    # 发送请求
    response = requests.post(url, json=data, headers=headers, stream=request.stream)
    # 整处理数据
    if request.stream:
        print("stream export")

        # 流式处理数据返回
        async def generate_response():
            # 遍历每个响应片段
            for line in response.iter_lines():
                if line:
                    # 解码并解析 JSON 数据
                    chunk = line.decode('utf-8')
                    parsed_data = json.loads(chunk)
                    # 处理内容
                    if not parsed_data['done']:
                        # 将返回数据转换为openai格式返回
                        base_response = {
                            "id": "chatcmpl-123",
                            "object": 'chat.completion.chunk',
                            "created": parsed_data['created_at'],
                            "model": request.model,
                            "model_dump": "",
                            "system_fingerprint": "fp_44709d6fcb",
                            "choices": [
                                {
                                    "index": 0, "delta": parsed_data['message'], "logprobs": None, "finish_reason": None
                                }
                            ]
                        }
                        yield f"data: {json.dumps(base_response)}\n\n"
                    else:
                        base_response = {
                            "id": "chatcmpl-123",
                            "object": 'chat.completion.chunk',
                            "created": parsed_data['created_at'],
                            "model": request.model,
                            "model_dump": "",
                            "system_fingerprint": "fp_44709d6fcb",
                            "choices": [
                                {
                                    "index": 0,
                                    "delta":
                                        parsed_data['message'],
                                    "logprobs": None,
                                    "finish_reason": 'stop'
                                }
                            ]
                        }
                        yield f"data: {json.dumps(base_response)}\n\n"
                        break

        return StreamingResponse(generate_response(), media_type="text/event-stream")
    else:
        print("not stream")
        # 正常响应结果
        return {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": response.json()['created_at'],
            "model": "gpt-4o-mini",
            "system_fingerprint": "fp_44709d6fcb",
            "choices": [{
                "index": 0,
                "message": response.json()['message'],
                "logprobs": None,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 9,
                "completion_tokens": 12,
                "total_tokens": 21,
                "completion_tokens_details": {
                    "reasoning_tokens": 0
                }
            }
        }
