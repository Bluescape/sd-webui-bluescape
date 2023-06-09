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
import re
from .expired_token_exception import ExpiredTokenException
from .config import Config
from typing import Tuple
import requests
import json

default_timeout = 30

def bs_find_space(token, workspace_id, bounding_box: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:

    x, y, width, height = bounding_box

    bs_api_url = f'{Config.api_base_domain}/v3/workspaces/{workspace_id}/findAvailableArea'

    body =  {
        "direction": "Right",
        "proposedArea": {
            "x": x,
            "y": y,
            "width": width,
            "height": height
        }
    }

    response = requests.post(bs_api_url, json = body, headers = get_headers(token), timeout = default_timeout)

    if response.status_code == 200:

            result = response.json()
            x = int(result["x"])
            y = int(result["y"])
            width = int(result["width"])
            height = int(result["height"])

            return (x, y, width, height)

    elif response.status_code == 401:
        raise ExpiredTokenException

def bs_create_zygote_at(token, workspace_id, filename, x, y, width, height, traits):

    bs_api_url = f'{Config.api_base_domain}/v3/workspaces/{workspace_id}/elements'

    body =  {
        'type': 'Image',
        'imageFormat': 'png',
        'title': filename,
        'filename': filename,
        'width': width,
        'height': height,
        'transform': {
            'x': x,
            'y': y
        },
        'traits': {
            'content': {

            }
        }
    }

    for k, v in traits.items():
        body['traits']['content'][k] = v

    response = requests.post(bs_api_url, json = body, headers = get_headers(token), timeout = default_timeout)

    return response.text

def bs_upload_asset(zr, buffer):

    body =  {
        'key': zr['data']['content']['fields']['key'],
        'bucket': zr['data']['content']['fields']['bucket'],
        'X-Amz-Algorithm': zr['data']['content']['fields']['X-Amz-Algorithm'],
        'X-Amz-Credential': zr['data']['content']['fields']['X-Amz-Credential'],
        'X-Amz-Date': zr['data']['content']['fields']['X-Amz-Date'],
        'Policy': zr['data']['content']['fields']['Policy'],
        'X-Amz-Signature': zr['data']['content']['fields']['X-Amz-Signature'],
    }

    files = { 'file': buffer}

    url = zr['data']['content']['url']
    response = requests.post(url, data = body, files = files, timeout = default_timeout)

    return response.text

def bs_finish_asset(token, workspace_id, upload_id):

    bs_elementary_api_url = f'{Config.api_base_domain}/v3/workspaces/{workspace_id}/assets/uploads/{upload_id}'

    requests.put(bs_elementary_api_url, headers = get_headers(token), json = {}, timeout = default_timeout)

def bs_upload_image_at(token, workspace_id, buffer, filename, bounding_box: Tuple[int, int, int, int], traits):

    x, y, width, height = bounding_box

    zygote_response = bs_create_zygote_at(token, workspace_id, filename, x, y, width,height, traits)
    zygote = json.loads(zygote_response)
    bs_upload_asset(zygote, buffer)
    bs_finish_asset(token, workspace_id, zygote['data']['content']['uploadId'])

def bs_create_canvas_at(token, workspace_id, title, bounding_box: Tuple[int, int, int, int], traits):

    x, y, width, height = bounding_box

    body = {
        'type': 'Canvas',
        'name': title,
        'style': {
            'width': width,
            'height': height,
            'fillColor': {
                'r': 255,
                'g': 255,
                'b': 255,
                'a': 1
            },
            'borderColor': {
                'r': 255,
                'g': 255,
                'b': 255,
                'a': 1
            },
            'showName': True
        },
        'transform': {
            'x': x,
            'y': y
        },
        'traits': {
            'content': {

            }
        }
    }

    for k, v in traits.items():
        body['traits']['content'][k] = v

    url = f'{Config.api_base_domain}/v3/workspaces/{workspace_id}/elements'

    response = requests.post(url, json = body, headers = get_headers(token), timeout = default_timeout)

    response_info = json.loads(response.text)

    return response_info['data']['id']

def bs_create_text_with_body(token, workspace_id, body):

    url = f'{Config.api_base_domain}/v3/workspaces/{workspace_id}/elements'

    response = requests.post(url, json = body, headers = get_headers(token), timeout = default_timeout)
    response_info = json.loads(response.text)

    return response_info['data']['id']

def bs_create_top_title(token, workspace_id, location: Tuple[int, int, int], text):

    title = "  |  " + text

    body = {
        "type": "Text",
        "blocks": [
            {
                "block": {
                    "content": [
                        {
                            "text": "Automatic1111"
                        },
                        {
                            "span": {
                                "color": { #charcoal50
                                    "r": 145,
                                    "g": 149,
                                    "b": 151,
                                    "a": 1
                                },
                                "text": title
                            }
                        }
                    ]
                }
            }
        ],
        "style": {
            "fontFamily": "Source_Sans_Pro",
            "fontSize": 63,
            "width": location[2],
            "backgroundColor": {
                "r": 255,
                "g": 255,
                "b": 255,
                "a": 0
            },
            "color": { #charcoal100
                "r": 46,
                "g": 54,
                "b": 61,
                "a": 1
            },
            "verticalAlign": "top"
        },
        "transform": {
            "x": location[0],
            "y": location[1]
        }
    }

    return bs_create_text_with_body(token, workspace_id, body)

def bs_create_extended_data(token, workspace_id, location: Tuple[int, int, int], extended_generation_data):

    content = []
    for key_value_pair in extended_generation_data:
        key = key_value_pair[0]
        value = key_value_pair[1]
        content.append(
            {
                "span": {
                    "fontWeight": "bold",
                    "text": str(key) + ": "
                }
            }
        )
        content.append(
            {
                "span": {
                    "text": str(value) + ", "
                }
            }
        )

    body = {
        "type": "Text",
        "blocks": [
            {
                "block": {
                    "content": content
                }
            }
        ],
        "style": {
            "fontFamily": "Source_Sans_Pro",
            "fontSize": 32,
            "width": location[2],
            "backgroundColor": { #bluescape20
                "r": 204,
                "g": 226,
                "b": 255,
                "a": 1
            },
            "color": { #charcoal90
                "r": 67,
                "g": 74,
                "b": 80,
                "a": 1
            },
            "verticalAlign": "top"
        },
        "transform": {
            "x": location[0],
            "y": location[1]
        }
    }

    return bs_create_text_with_body(token, workspace_id, body)

def bs_create_generation_data(token, workspace_id, location: Tuple[int, int, int], infotext):

    infos = infotext.split("\n")

    blocks = []

    # Example with prompt + negative prompt:
    #
    # Ellen Ripley from Alien movie, astronaut, [perfect symmetric] helmet on, visor closed, looking up, action pose, standing on background of Nostromo space shuttle [intricate] interiors , sci-fi
    # Negative prompt: disfigured, bad
    # Steps: 30, Sampler: Euler a, CFG scale: 7, Seed: 889387345, Face restoration: CodeFormer, Size: 512x512, Model hash: ad2a33c361, Model: v2-1_768-ema-pruned, Version: v1.3.1

    # Example without negative prompt:
    #
    # Ellen Ripley from Alien movie, astronaut, [perfect symmetric] helmet on, visor closed, looking up, action pose, standing on background of Nostromo space shuttle [intricate] interiors , sci-fi
    # Steps: 30, Sampler: Euler a, CFG scale: 7, Seed: 889387345, Face restoration: CodeFormer, Size: 512x512, Model hash: ad2a33c361, Model: v2-1_768-ema-pruned, Version: v1.3.1

    # Example without prompt, but with negative prompt:
    #
    # Negative prompt: disfigured, bad
    # Steps: 30, Sampler: Euler a, CFG scale: 7, Seed: 889387345, Face restoration: CodeFormer, Size: 512x512, Model hash: ad2a33c361, Model: v2-1_768-ema-pruned, Version: v1.3.1

    # Example without prompt + without negative prompt:
    #
    # Steps: 30, Sampler: Euler a, CFG scale: 7, Seed: 889387345, Face restoration: CodeFormer, Size: 512x512, Model hash: ad2a33c361, Model: v2-1_768-ema-pruned, Version: v1.3.1

    # This is a bit hacky, but we'll check if the row starts with "Negative prompt:" or "Steps:" and then turn
    # on styling for that row (keys to be bolded, values not)

    for info in infos:
        content = []
        if info.startswith("Negative prompt:"):
            key, value = info.split(':', 1)
            content.append(
                {
                    "span": {
                        "fontWeight": "bold",
                        "text": str(key) + ": "
                    }
                }
            )
            content.append(
                {
                    "span": {
                        "text": str(value)
                    }
                }
            )
        elif info.startswith("Steps:"):
            try:
                # Regex pattern to match either key: "value with, commas" or key: value
                pattern = re.compile(r'([^:]+): ("[^"]*"|[^,]*),?')

                # Find all matches in the string
                matches = pattern.findall(info)

                # Convert matches to a dictionary
                key_value_pairs = {key.strip(): value.strip(' "')
                    for key, value in matches}

                for key, value in key_value_pairs.items():
                    content.append(
                        {
                            "span": {
                                "fontWeight": "bold",
                                "text": str(key) + ": "
                            }
                        }
                    )
                    content.append(
                        {
                            "span": {
                                "text": str(value) + ", "
                            }
                        }
                    )
            except Exception as e:
                print("Failed to format generation data:")
                print(e)
                print("Falling back to unformatted string")
                content.append(
                {
                    "span": {
                        "text": str(info)
                    }
                }
            )

        else:
            content.append(
                {
                    "span": {
                        "text": str(info)
                    }
                }
            )

        blocks.append(
            {
                "block": {
                    "content": content
                }
            }
        )


    body = {
        "type": "Text",
        "blocks": blocks,
        "style": {
            "fontFamily": "Source_Sans_Pro",
            "fontSize": 32,
            "width": location[2],
            "backgroundColor": { #bluescape20
                "r": 204,
                "g": 226,
                "b": 255,
                "a": 1
            },
            "color": { #charcoal90
                "r": 67,
                "g": 74,
                "b": 80,
                "a": 1
            },
            "verticalAlign": "top"
        },
        "transform": {
            "x": location[0],
            "y": location[1]
        }
    }

    return bs_create_text_with_body(token, workspace_id, body)

def bs_create_seed(token, workspace_id, location: Tuple[int, int, int], seed, subseed):

    body = {
        "type": "Text",
        "blocks": [
            {
                "block": {
                    "content": [
                        {
                            "span": {
                                "fontWeight": "bold",
                                "text": "Seed: "
                            }
                        },
                        {
                            "span": {
                                "text": str(seed)
                            }
                        },
                        {
                            "span": {
                                "fontStyle": "italic",
                                "text": " (sub: " + str(subseed) + ")"
                            }
                        }
                    ]
                }
            }
        ],
        "style": {
            "fontFamily": "Source_Sans_Pro",
            "fontSize": 24,
            "width": location[2],
            "backgroundColor": { #bluescape20
                "r": 204,
                "g": 226,
                "b": 255,
                "a": 1
            },
            "color": { #charcoal90
                "r": 67,
                "g": 74,
                "b": 80,
                "a": 1
            },
            "verticalAlign": "top"
        },
        "transform": {
            "x": location[0],
            "y": location[1]
        }
    }

    return bs_create_text_with_body(token, workspace_id, body)



def bs_create_generation_label(token, workspace_id, location: Tuple[int, int, int], text):

    body = {
        "type": "Text",
        "blocks": [
            {
                "block": {
                    "content": [
                        {
                            "span": {
                                "fontWeight": "bold",
                                "text": text
                            }
                        }
                    ]
                }
            }
        ],
        "style": {
            "fontFamily": "Source_Sans_Pro",
            "fontSize": 32,
            "width": location[2],
            "backgroundColor": {
                "r": 255,
                "g": 255,
                "b": 255,
                "a": 0
            },
            "color": { #charcoal90
                "r": 67,
                "g": 74,
                "b": 80,
                "a": 1
            },
            "verticalAlign": "top"
        },
        "transform": {
            "x": location[0],
            "y": location[1]
        }
    }

    return bs_create_text_with_body(token, workspace_id, body)


def bs_create_label(token, workspace_id, location: Tuple[int, int, int], text):

    body = {
        "type": "Text",
        "blocks": [
            {
                "block": {
                    "content": [
                        {
                            "span": {
                                "fontWeight": "bold",
                                "text": text
                            }
                        }
                    ]
                }
            }
        ],
        "style": {
            "fontFamily": "Source_Sans_Pro",
            "fontSize": 24,
            "width": location[2],
            "backgroundColor": { #cheeseSoft
                "r": 254,
                "g": 240,
                "b": 159,
                "a": 1
            },
            "color": { #charcoal90
                "r": 67,
                "g": 74,
                "b": 80,
                "a": 1
            },
            "verticalAlign": "top"
        },
        "transform": {
            "x": location[0],
            "y": location[1]
        }
    }

    return bs_create_text_with_body(token, workspace_id, body)

def bs_get_all_workspaces(token):
    has_next_page = True
    cursor = None
    workspaces = []
    i = 1

    while has_next_page:
        (current_page, next) = bs_get_workspaces(token, cursor)
        workspaces = workspaces + current_page
        cursor = next
        # Limit for 3 requests for now
        print(f"Loading workspaces... {str(i)} of 3")
        i = i + 1
        has_next_page = next is not None and i < 4

    return workspaces

def bs_get_workspaces(token, cursor = None):
    url = f'{Config.api_base_domain}/v3/users/me/workspaces?pageSize=100&includeCount=true&filterBy=associatedWorkspaces eq false&orderBy=contentUpdatedAt desc'

    if (cursor is not None):
        url = f'{Config.api_base_domain}/v3/users/me/workspaces?cursor={cursor}'

    response = requests.get(url, headers = get_headers(token), timeout = default_timeout)
    if response.status_code == 200:
        response_info = json.loads(response.text)
        return (response_info['workspaces'], response_info['next'])
    elif response.status_code == 401:
        raise ExpiredTokenException
    
def bs_get_user_id(token):
        url = f'{Config.api_base_domain}/v3/users/me'

        response = requests.get(url, headers = get_headers(token))

        if response.status_code == 200:
            response_info = json.loads(response.text)
            return response_info["id"]

        print("Error: " + response.text)

def get_headers(token):
    return {
        'Authorization': f'Bearer {token}',
        'Content-type': 'application/json'
    }
