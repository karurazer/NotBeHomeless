import json
from pathlib import Path

import aiofiles


async def load_json_file(project_file_path: str) -> dict:
    """
        Load a JSON file and return its content as a dictionary.
    """
    file_path = Path(__file__).resolve().parent.parent / project_file_path
    async with aiofiles.open(file_path, 'r') as f:
        content = await f.read()
        return json.loads(content)