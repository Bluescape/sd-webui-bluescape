#
# MIT License
#
# Copyright (c) 2023 Thought Stream, LLC dba Bluescape.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from enum import Enum
import re
import json
import base64

def extract_workspace_id(input):
    parts = input.split()
    workspace_part = parts[-1]
    workspace_id = workspace_part[1:-1]
    if len(workspace_id) != 20:
        raise

    return workspace_id

def extract_token_exp(token):
    if token != '' and token is not None:
        token_split = token.split(".")
        decoded = base64.b64decode(f"{token_split[1]}{'=' * (4 - len(token_split[1]) % 4)}")
        token_info = json.loads(decoded.decode("utf-8"))
        return token_info["exp"]

    return None

class CanvasTitleStrategy(Enum):
    Default = "Default (A1111 | prompt)"
    GenerationMode = "Generation mode (txt2img / img2img)"
    Username = "User name (John Smith)"
    Timestamp = "Timestamp (2023-07-06 10:35:41)"

class CanvasHeaderStrategy(Enum):
    Default = "Default (A1111 | prompt)"
    GenerationMode = "Generation mode + prompt (txt2img / img2img | prompt)"
    Username = "User name + prompt (John Smith | prompt)"
    Timestamp = "Timestamp + prompt (2023-07-06 10:35:41 | prompt)"

class SuggestedCanvasBorderColors(Enum):
    Blue = "#0000ff"
    Teal = "#008080"
    Yellow = "#ffff00"
    Orange = "#ffa500"
    Red = "#ff0000"
    Magenta = "#ff00ff"
    Purple = "#800080"

class FindSpaceDirection(Enum):
    Right = "Right"
    Down = "Down"

def is_hex_color(s):
    return bool(re.fullmatch(r'^#([A-Fa-f0-9]{6})$', s))

def hex_to_bluescape_rgb(hex_color):
    # Ensure the hex color starts with '#'
    if not is_hex_color(hex_color):
        raise ValueError('Input string must be a hex color of 6 characters, excluding the "#"')

    # Convert the hex color to RGB
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)

    return {
        'r': r,
        'g': g,
        'b': b,
        'a': 1
    }

def find_on_key_value(json_list, key_to_find, value_to_find):
    def search_dict(json_input, key_to_find, value_to_find):
        if isinstance(json_input, dict):
            if key_to_find in json_input and json_input[key_to_find] == value_to_find:
                return True
            for k, v in json_input.items():
                if search_dict(v, key_to_find, value_to_find):
                    return True
        elif isinstance(json_input, list):
            for item in json_input:
                if search_dict(item, key_to_find, value_to_find):
                    return True
        return False

    return [json_obj for json_obj in json_list if search_dict(json_obj, key_to_find, value_to_find)]

def find_on_key(json_list, key_to_find):
    def search_dict(json_input, key_to_find):
        if isinstance(json_input, dict):
            if key_to_find in json_input:
                return True
            for v in json_input.values():
                if search_dict(v, key_to_find):
                    return True
        elif isinstance(json_input, list):
            for item in json_input:
                if search_dict(item, key_to_find):
                    return True
        return False

    return [json_obj for json_obj in json_list if search_dict(json_obj, key_to_find)]
