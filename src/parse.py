# parse.py

import json
import re


def parse_json_with_ctzdist(raw_text: str) -> list[dict]:
    entries = []

    for match in re.finditer(r"\{.*?\}", raw_text, re.DOTALL):
        obj_text = match.group(0)

        num_match = re.search(r'"CTZDIST"\s*:\s*(\d+)', obj_text)
        str_match = re.search(r'"CTZDIST"\s*:\s*"([^"]+)"', obj_text)

        obj_text = re.sub(r'"CTZDIST"\s*:\s*("[^"]+"|\d+),?', "", obj_text)

        obj = json.loads(obj_text)
        obj["CTZDIST__1"] = int(num_match.group(1)) if num_match else None
        obj["CTZDIST__2"] = str_match.group(1) if str_match else None

        entries.append(obj)

    return entries
