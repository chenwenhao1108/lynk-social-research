from utils import *

openai_service = OpenAIService()

res = openai_service.infer(
    "你好",
    system_prompt="你是一个聊天机器人。请用以下格式返回内容：\n```json\n{\"message\": \"你的回复内容\"}\n```",
)

print(res)