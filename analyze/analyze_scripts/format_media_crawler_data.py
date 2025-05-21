from utils import read_json, write_json
def format_bili_data(data):
    comment_ids = set()
    formatted_data = []
    for comment in data:
        id = comment["comment_id"]
        if id in comment_ids:
            continue
        content = comment["content"]
        timestamp = comment["create_time"]
        video_id = comment["video_id"]
        tmp = {
            "video_id": video_id,
            "comment_id": id,
            "content": content,
            "timestamp": timestamp,
        }
        formatted_data.append(tmp)
        comment_ids.add(id)
    return formatted_data

def format_wb_data(note_data, comment_data):
    formatted_data = []
    
    comment_ids = set()
    formatted_comments = {}
    for comment in comment_data:
        comment_id = comment["comment_id"]
        note_id = comment["note_id"]
        if id in comment_ids:
            continue
        if not note_id in formatted_comments:
            formatted_comments[note_id] = []
        
        tmp ={
            "comment_id": comment_id,
            "content": comment["content"],
            "timestamp": comment["create_time"],
        }
        formatted_comments[note_id].append(tmp)
        comment_ids.add(comment_id)
    
    note_ids = set()
    for note in note_data:
        note_id = note["note_id"]
        if note_id in note_ids:
            continue
        tmp = {
            "note_id": note_id,
            "content": note["content"],
            "timestamp": note["create_time"],
            "replies": formatted_comments.get(note_id, []),
        }
        formatted_data.append(tmp)
        note_ids.add(note_id)
    return formatted_data
    

def main():
    data = read_json("analyze/raw_data/bili/search_comments_2025-05-20.json") + read_json("analyze/raw_data/bili/search_comments_2025-05-21.json")
    formatted_data = format_bili_data(data)
    write_json(formatted_data, "analyze/raw_data/formatted/bili.json")
    
    note_data = read_json("analyze/raw_data/wb/search_contents_2025-05-20.json") + read_json("analyze/raw_data/wb/search_contents_2025-05-21.json")
    comment_data = read_json("analyze/raw_data/wb/search_comments_2025-05-20.json") + read_json("analyze/raw_data/wb/search_comments_2025-05-21.json")
    formatted_data = format_wb_data(note_data, comment_data)
    write_json(formatted_data, "analyze/raw_data/formatted/wb.json")
    

if __name__ == "__main__":
    main()
        