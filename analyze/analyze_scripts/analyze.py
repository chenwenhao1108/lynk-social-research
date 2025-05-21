
from utils import *
from prompt import *

from concurrent.futures import ThreadPoolExecutor, as_completed


def analyze_posts(posts, max_workers=200):
    openai_service = OpenAIService()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures_map = {}
        
        for idx, post in enumerate(posts):
            content = post["content"]
            future = executor.submit(
                openai_service.infer,
                distribute_themes_user_prompt.format(post_content=content),
                system_prompt=distribute_themes_system_prompt,
            )
            futures_map[future] = {"type": "post", "location": idx}
            
            replies = post.get("replies", None)
            if replies:
                for i, reply in enumerate(replies):
                    future = executor.submit(
                        openai_service.infer,
                        distribute_themes_user_prompt.format(post_content=reply["content"]),
                        system_prompt=distribute_themes_system_prompt,
                    )
                    futures_map[future] = {"type": "reply", "location": (idx, i)}
                    
        for future in as_completed(futures_map):
            task_info = futures_map[future]
            task_type = task_info["type"]
            location = task_info["location"]
            res = future.result()
            if res is not None:
                if task_type == "post":
                    idx = location
                    posts[idx]["themes"] = res
                elif task_type == "reply":
                    idx, i = location
                    posts[idx]["replies"][i]["themes"] = res
            else:
                print(f"Res is None for task type {task_type} and location {location}")
                if task_type == "post":
                    idx = location
                    posts[idx]["themes"] = []
                elif task_type == "reply":
                    idx, i = location
                    posts[idx]["replies"][i]["themes"] = []

    return posts

def main():
    file_names = [
        "autohome.json",
        "dongchedi.json",
        "bili.json",
        "wb.json",
    ]
    for file_name in file_names:
        file_path = f"analyze/raw_data/formatted/{file_name}"
        data = read_json(file_path)
        analyzed_data = analyze_posts(data)
        write_json(analyzed_data, f"analyze/analyze_results/{file_name}")

if __name__ == "__main__":
    main()
                
                

                
            
            
            
