from utils import *

questions_map = {
    "A": "用户决定下定、购买领克900的原因、理由；",
    "B": "用户纠结下定、购买领克900的原因、理由；",
    "C": "用户决定放弃购买领克900的原因、理由；",
    "D": "用户在网上浏览领克900后，预留联系方式后，是否及时获得反馈，包括但不限于询问车辆信息、价格、政策、邀约到店等；",
    "E": "用户在领克门店，看领克900的整体体验，是否低于、符合、超越预期；",
    "F": "用户在领克门店看领克900时，对于销售的接待、服务体验，是否低于、符合、超越预期；",
    "G": "用户在领克门店看领克900时，对于销售介绍车辆的专业度，是否低于、符合、超越预期；",
    "H": "用户在领克门店看领克900时，对于试驾的整体体验，是否低于、符合、超越预期；",
    "I": "用户在领克门店试驾领克900时，对于1.5T车型的智驾辅助系统，是否低于、符合、超越预期；",
    "J": "用户在领克门店试驾领克900时，对于1.5T车型的整体驾驶感受，是否低于、符合、超越预期；",
    "K": "用户在领克门店试驾领克900时，对于2.0T车型的智驾辅助系统，是否低于、符合、超越预期；",
    "L": "用户在领克门店试驾领克900时，对于2.0T车型的整体驾驶感受，是否低于、符合、超越预期；",
    "M": "用户在考虑领克900时，对比的竞品车型有哪些；",
    "N": "用户在对比竞品时，认为优于领克900的有哪些；",
    "O": "用户在对比竞品时，认为领克900更好的地方有哪些。"
}
    
def count_themes(posts):
    theme_count = {}
    for post in posts:
        themes = post.get("themes", [])
        for theme in themes:
            if theme not in theme_count:
                theme_count[theme] = {
                    "count": 0,
                    "content": []
                }
            theme_count[theme]["count"] += 1
            theme_count[theme]["content"].append(post["content"])
        for reply in post.get("replies", []):
            reply_themes = reply.get("themes", [])
            for theme in reply_themes:
                if theme not in theme_count:
                    theme_count[theme] = {
                        "count": 0,
                        "content": []
                    }
                theme_count[theme]["count"] += 1
                theme_count[theme]["content"].append(reply["content"])
    return theme_count


def main():
    posts = []
    file_paths = [
        "analyze/analyze_results/autohome.json",
        "analyze/analyze_results/dongchedi.json",
        "analyze/analyze_results/bili.json",
        "analyze/analyze_results/wb.json",
    ]
    for path in file_paths:
        posts.extend(read_json(path))
    theme_count = count_themes(posts)
    
    for theme, info in theme_count.items():
        count = info['count']
        print(f"主题 {theme} 出现的次数为 {count}")

    write_json(theme_count, "analyze/analyze_results/theme_count.json")


if __name__ == "__main__":
    main()