from utils import *

theme_count = read_json("analyze/analyze_results/theme_count.json")

for theme in theme_count.values():
    theme["content"] = list(set(theme["content"]))

write_json(theme_count, "analyze/analyze_results/theme_count.json")
    