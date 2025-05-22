"""
这个脚本用来对每个post分配主题
"""
import asyncio
from utils import *
from prompt import *

from concurrent.futures import ThreadPoolExecutor, as_completed


async def process_item(idx, content, type_, openai_service, reply_idx=None):
    """
    该函数负责调用 infer 并返回任务的位置信息，便于后续写回 posts 结构。
    """
    user_prompt = distribute_themes_user_prompt.format(post_content=content)
    res = await openai_service.infer(
        user_prompt=user_prompt,
        system_prompt=distribute_themes_system_prompt
    )
    if type_ == "post":
        location = idx
    else:
        location = (idx, reply_idx)
    return (location, type_, res)

async def analyze_posts_async(posts, max_concurrent_tasks=200):
    openai_service = OpenAIService()
    tasks = []

    for idx, post in enumerate(posts):
        content = post["content"]
        # 为每个主 post 创建任务
        task = asyncio.create_task(
            process_item(
                idx=idx,
                content=content,
                type_="post",
                openai_service=openai_service
            )
        )
        tasks.append(task)

        # 为每个 reply 创建任务
        replies = post.get("replies", [])
        for i, reply in enumerate(replies):
            task = asyncio.create_task(
                process_item(
                    idx=idx,
                    reply_idx=i,
                    content=reply["content"],
                    type_="reply",
                    openai_service=openai_service
                )
            )
            tasks.append(task)

    # 并发执行所有任务
    results = await asyncio.gather(*tasks)

    # 将结果写入 posts
    for location, type_, res in results:
        if type_ == "post":
            posts[location]["themes"] = res
        else:
            idx, reply_idx = location
            posts[idx]["replies"][reply_idx]["themes"] = res

    return posts

async def main():
    file_names = [
        "autohome.json",
        "dongchedi.json",
        "bili.json",
        "wb.json",
    ]
    for file_name in file_names:
        file_path = f"analyze/raw_data/formatted/{file_name}"
        data = read_json(file_path)
        analyzed_data = await analyze_posts_async(data)
        write_json(analyzed_data, f"analyze/analyze_results/{file_name}")

if __name__ == "__main__":
    asyncio.run(main())
                
                

                
            
            
            
