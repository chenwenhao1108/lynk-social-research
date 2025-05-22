"""
    这个脚本用来对theme_count.json中每个theme的content进行总结，并得出一些结构性的总结。
"""

import asyncio
from utils import *
from prompt import *


questions_map = {
    "A": "用户**决定**下定、购买**领克900**的原因、理由；",
    "B": "用户**纠结**下定、购买**领克900**的原因、理由；",
    "C": "用户**决定放弃**购买**领克900**的原因、理由；",
    "D": "用户在网上浏览领克900后，**预留联系方式后，是否及时获得反馈**，包括但不限于询问**车辆信息、价格、政策、邀约到店**等；",
    "E": "用户**在领克门店**，看领克900的整体体验**，是否低于、符合、超越预期；",
    "F": "用户在**领克门店**看领克900时，对于**销售的接待、服务体验**，是否低于、符合、超越预期；",
    "G": "用户在**领克门店**看领克900时，对于**销售介绍车辆的专业度**，是否低于、符合、超越预期；",
    "H": "用户在**领克门店**看领克900时，对于**试驾的整体体验**，是否低于、符合、超越预期；",
    "I": "用户在**领克门店**试驾领克900时，对于**1.5T车型**的**智驾辅助系统**，是否低于、符合、超越预期；",
    "J": "用户在**领克门店**试驾领克900时，对于**1.5T车型**的**整体驾驶感受**，是否低于、符合、超越预期；",
    "K": "用户在**领克门店**试驾领克900时，对于**2.0T车型**的**智驾辅助系统**，是否低于、符合、超越预期；",
    "L": "用户在**领克门店**试驾领克900时，对于**2.0T车型**的**整体驾驶感受**，是否低于、符合、超越预期；",
    "M": "用户在考虑领克900时，对比的**竞品车型**有哪些；",
    "N": "用户在**对比竞品时**，认为**优于领克900**的有哪些；",
    "O": "用户在**对比竞品时**，认为**领克900更好的地方**有哪些。"
}


def batch_generator(lst, batch_size):
    """ 生成器函数，用于逐批次返回列表中的元素 """
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


async def summarize_content(openai_service, content, theme):

    formatted_user_prompt = summarize_theme_user_prompt.format(post_content=content)
    formatted_system_prompt = summarize_theme_system_prompt.format(theme=theme)
    summary =  await openai_service.infer(
        user_prompt=formatted_user_prompt,
        system_prompt=formatted_system_prompt
    )
    return (theme, summary)


async def summarize_by_theme(theme_count_data):
    openai_service = OpenAIService()
    tasks = []
    batch_size = 200
    for theme, data in theme_count_data.items():
        content_list = data["content"]
        question = questions_map[theme]
        for batch in batch_generator(content_list, batch_size):
            content = "\n".join(batch)
            task = asyncio.create_task(summarize_content(openai_service, content, question))
            tasks.append(task)
            
    results = await asyncio.gather(*tasks)
    analyzed_data = {}
    for theme, summary in results:
        if theme not in analyzed_data:
            analyzed_data[theme] = {"summary_list": []}
        analyzed_data[theme]["summary_list"].extend(summary)

    return analyzed_data

def main():
    theme_count_data = read_json("analyze/analyze_results/theme_count.json")
    analyzed_data = asyncio.run(summarize_by_theme(theme_count_data))
    write_json(analyzed_data, "analyze/analyze_results/summarized.json")


if __name__ == "__main__":
    main()

        
