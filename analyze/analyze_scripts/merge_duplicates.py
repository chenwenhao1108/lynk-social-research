import asyncio
import json
from utils import OpenAIService, read_json, write_json # Assuming these are in utils.py
from prompt import MERGE_ITEMS_SYSTEM_PROMPT, MERGE_ITEMS_USER_PROMPT

async def call_llm_for_merging(openai_service, items_to_merge, item_type_description):
    """Helper function to call LLM for merging items."""
    if not items_to_merge:
        return []

    items_json_string = json.dumps(items_to_merge, ensure_ascii=False, indent=4)
    
    user_prompt = MERGE_ITEMS_USER_PROMPT.format(items_json_string=items_json_string)
    system_prompt = MERGE_ITEMS_SYSTEM_PROMPT

    # print(f"Calling LLM to merge {item_type_description}...")

    try:
        merged_items = await openai_service.infer(
            user_prompt=user_prompt,
            system_prompt=system_prompt
        )
        # print(f"Successfully merged {item_type_description}.")
        return merged_items
    except Exception as e:
        print(f"An error occurred during LLM call for {item_type_description}: {e}")
        return items_to_merge

async def merge_points_for_summary_task(summary_object, openai_service):
    """Merges semantically similar points within a single summary object. Designed to be a task for asyncio.gather."""
    points = summary_object.get("points", [])
    if not points or len(points) < 2:
        return summary_object

    merged_points = await call_llm_for_merging(openai_service, points, f"points for summary '{summary_object.get('summary', 'Untitled')[:30]}...'" )
    summary_object["points"] = merged_points
    return summary_object

async def merge_summaries_and_their_points_for_theme_task(theme_key, summary_list, openai_service):
    """Merges summaries for a theme, then merges points within each of those (potentially merged) summaries. Designed for asyncio.gather."""
    if not summary_list or len(summary_list) < 2:
        # If no summaries or only one, still process its points if any
        processed_summaries = []
        if summary_list: # Potentially a list with one summary
            point_merge_tasks = [merge_points_for_summary_task(s_obj, openai_service) for s_obj in summary_list]
            processed_summaries = await asyncio.gather(*point_merge_tasks)
        return theme_key, processed_summaries

    # Step 1: Merge summaries for the theme
    # print(f"Calling LLM to merge summaries for theme '{theme_key}'...")
    merged_summaries_from_llm = await call_llm_for_merging(openai_service, summary_list, f"summaries for theme '{theme_key}'")
    # print(f"Summaries merged for theme '{theme_key}'. Now merging points within them.")

    # Step 2: Concurrently merge points for each (newly merged or original) summary
    point_merge_tasks = []
    for summary_obj in merged_summaries_from_llm:
        point_merge_tasks.append(merge_points_for_summary_task(summary_obj, openai_service))
    
    final_processed_summaries = await asyncio.gather(*point_merge_tasks)
    # print(f"Points merged for summaries in theme '{theme_key}'.")
    return theme_key, final_processed_summaries

async def main():
    input_file = "analyze/analyze_results/summarized.json"
    output_file = "analyze/analyze_results/merged_summarized.json"

    summarized_data = read_json(input_file)
    if not summarized_data:
        print(f"Could not read or parse {input_file}. Exiting.")
        return

    openai_service = OpenAIService()
    merged_data_intermediate = {}

    # Create tasks for processing each theme concurrently
    theme_processing_tasks = []
    for theme_key, theme_value in summarized_data.items():
        print(f"Queueing theme for processing: {theme_key}")
        summary_list = theme_value.get("summary_list", [])
        task = merge_summaries_and_their_points_for_theme_task(theme_key, summary_list, openai_service)
        theme_processing_tasks.append(task)
    
    # Gather results from all theme processing tasks
    print(f"\nStarting concurrent processing of {len(theme_processing_tasks)} themes...")
    theme_results = await asyncio.gather(*theme_processing_tasks)
    print("\nAll themes processed.")

    # Populate the final merged_data dictionary
    final_merged_data = {}
    for theme_key, processed_summary_list in theme_results:
        final_merged_data[theme_key] = {"summary_list": processed_summary_list}

    write_json(final_merged_data, output_file)
    print(f"\nSuccessfully merged summaries and points concurrently. Output saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())