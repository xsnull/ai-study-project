from openai import OpenAI
import json

client = OpenAI(base_url='http://127.0.0.1:8000', api_key="123")
# 指定模型
MODEL = "qwen2.5:7b"


# 实现一个多轮问答的类
class MultiConversation:
    # 初始化对象时传入第一句指令
    def __init__(self, init_prompt):
        self.messages = []
        self.messages.append({"role": "system", "content": init_prompt})

    # 每调用一次这个方法，都会将问题和回答记录在self.messages列表属性中，用于记录上下文
    def qa(self, question):
        self.messages.append({"role": "user", "content": question})
        answer = client.chat.completions.create(
            model=MODEL,
            messages=self.messages,
            stream=True
        )
        for chunk in answer:
            print(chunk.choices[0].delta.content, end='')
        self.messages.append({"role": "assistant", "content": answer.choices[0].message.content})
        return answer.choices[0].message.content


if __name__ == "__main__":
    mc = MultiConversation('你是一个数学专家机器人，需要回答数学相关的问题，你的回答需要满足以下要求：'
                           '1.你的回答必须是中文'
                           '2.只回答数学相关的问题，对于非数学问题，一律只回答：对不起，无法回答不相关问题')
    print('您好，我是您的专属数学机器人，您可以向我提问任何数学问题，输入【exit】退出问答。')
    while True:
        user_input = input('Q：')
        if user_input.lower() == 'exit':
            print('bye~')
            break
        response = mc.qa(user_input)
        print('A:' + response)
