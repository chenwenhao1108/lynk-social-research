import json
import os
import re
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv()


class OpenAIService:
    """Service class for OpenAI API interactions."""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("OPENAI_API_BASE"),
        )

    def infer(
        self,
        user_prompt: str,
        system_prompt: str,
        model: str = "gpt-4.1-mini",
        temperature: float = 0.8,
        retries: int = 3,
    ):
        """Make an inference using OpenAI API."""
        for attempt in range(retries):
            try:
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        ({"role": "system", "content": system_prompt}),
                        {"role": "user", "content": user_prompt},
                    ],
                    timeout=300,
                    temperature=temperature,
                )
                res_raw = completion.choices[0].message.content
                # Try to parse JSON if present
                pattern = re.compile(r"```json\s*([\s\S]*?)\s*```")
                matches = pattern.findall(res_raw) if res_raw else None
                if matches:
                    try:
                        return json.loads(matches[0], strict=False)
                    except json.JSONDecodeError as e:
                        user_prompt += f"""**请严格按照要求的json格式返回结果，确保json格式正确，且不要返回多余的解释和注释**
                        请注意避免出现如下报错：
                        ```
                        {e}
                        ```
                        """
                        continue
                else:
                    user_prompt += "**请严格按照要求的json格式返回结果，确保json格式正确，且不要返回多余的解释和注释**"
                    continue

            except Exception as e:
                print(f"OpenAI API call failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    raise


def read_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        raise
    
def write_json(data, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error writing to file: {e}")
        raise
    