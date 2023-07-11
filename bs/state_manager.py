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
import json
import os
from .bluescape_api import bs_get_all_workspaces
from appdirs import AppDirs
import subprocess
from pathlib import Path
from .misc import CanvasHeaderStrategy, CanvasTitleStrategy

class StateManager:

    user_token = ""
    user_id = ""

    # Array for dropdown values - labels
    workspace_dd = {}
    # Dictionary to lookup name by workspace id
    workspace_ids = {}

    selected_workspace_id = ""
    enable_verbose = False
    img2img_include_init_images = True
    scale_to_standard_size = True
    enable_metadata = True
    enable_analytics = True
    user_swimlane = True
    use_canvas_border_color = False
    canvas_border_color = None
    canvas_title_strategy = CanvasTitleStrategy.Default.value
    canvas_header_strategy = CanvasHeaderStrategy.Default.value
    nick_name = None
    user_name = ""
    token_exp = None

    token_expired = False

    img2img_include_mask_image = False

    txt2img_status = ""
    img2img_status = ""

    a1111_version = "unknown"
    extension_version = "unknown"

    def __init__(self):
        dirs = AppDirs("a1111-sd-extension", "Bluescape")
        os.makedirs(dirs.user_data_dir, exist_ok=True)
        self.state_file = os.path.join(dirs.user_data_dir, "bs_state.json")
        print("State file for your system: " + self.state_file)

    def read_versions(self, extension_file_path):
        if self.a1111_version != "unknown":
            return

        try:
            self.a1111_version = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip().decode()
        except Exception:
            pass
        try:
            extension_root_dir = Path(extension_file_path).parent.parent
            version_file = str(extension_root_dir) + '/version.txt'
            with open(version_file) as f:
                self.extension_version = f.read()
        except Exception:
            pass

    def flush_user_data(self):
        self.user_token = ""
        self.user_id = ""
        self.user_name = ""
        self.workspace_dd = {}
        self.workspace_ids = {}
        self.selected_workspace_id = ""
        self.token_exp = None
        self.save()

    def refresh_workspaces(self, token):
        workspaces = bs_get_all_workspaces(token)
        print(f"Total {len(workspaces)} workspaces retrieved")
        self.workspace_ids = {}
        self.workspace_dd = []

        for w in workspaces:
            dd_name = f"{w['name']} ({w['id']})"
            self.workspace_ids[w['id']] = dd_name
            self.workspace_dd.append(dd_name)

        # If we don't have an existing selected id, lets select the first one
        if self.selected_workspace_id == "" or self.selected_workspace_id not in self.workspace_ids.keys():
            self.selected_workspace_id = next(iter(self.workspace_ids))

        self.save()

    def get_selected_workspace_item(self):
        selected_workspace = None
        if self.selected_workspace_id is not None and self.selected_workspace_id != "" and self.selected_workspace_id in self.workspace_ids:
            selected_workspace = self.workspace_ids[self.selected_workspace_id]

        return selected_workspace

    def save(self):
        with open(self.state_file, "w+") as out_file:
            json.dump({
                "user_id": self.user_id,
                "user_name": self.user_name,
                "selected_workspace_id": self.selected_workspace_id,
                "enable_verbose": self.enable_verbose,
                "img2img_include_init_images": self.img2img_include_init_images,
                "img2img_include_mask_image": self.img2img_include_mask_image,
                "scale_to_standard_size": self.scale_to_standard_size,
                "enable_metadata": self.enable_metadata,
                "enable_analytics": self.enable_analytics,
                "user_swimlane": self.user_swimlane,
                "use_canvas_border_color": self.use_canvas_border_color,
                "canvas_border_color": self.canvas_border_color,
                "workspace_dd": self.workspace_dd,
                "workspace_ids": self.workspace_ids,
                "canvas_title_strategy": self.canvas_title_strategy,
                "canvas_header_strategy": self.canvas_header_strategy,
                "nick_name": self.nick_name,
                "user_token": self.user_token,
                "token_exp": self.token_exp
            }, out_file, indent = 6)
            out_file.close()

    def load(self):
        if not os.path.exists(self.state_file):
            return

        try:
            with open(self.state_file) as f:
                data = json.load(f)
                try:
                    self.user_id = data['user_id']
                    self.selected_workspace_id = data['selected_workspace_id']
                    self.enable_verbose = data['enable_verbose']
                    self.img2img_include_init_images = data['img2img_include_init_images']
                    self.img2img_include_mask_image = data['img2img_include_mask_image']
                    self.scale_to_standard_size = data['scale_to_standard_size']
                    self.enable_metadata = data['enable_metadata']
                    self.enable_analytics = data['enable_analytics']
                    self.user_swimlane = data['user_swimlane']
                    self.canvas_title_strategy = data['canvas_title_strategy'] if data['canvas_title_strategy'] else CanvasTitleStrategy.Default.value
                    self.canvas_header_strategy = data['canvas_header_strategy'] if data['canvas_header_strategy'] else CanvasHeaderStrategy.Default.value
                    self.use_canvas_border_color = data['use_canvas_border_color']
                    self.canvas_border_color = data['canvas_border_color'] if data["canvas_border_color"] else None
                    self.workspace_dd = data['workspace_dd']
                    self.workspace_ids = data['workspace_ids']
                    self.nick_name = data['nick_name'] if data['nick_name'] else None
                    self.user_token = data['user_token']
                except KeyError:
                    print('Unsupported state file version, flushing state...')

                self.user_name = self.read_from_json(data, "user_name", "")
                self.token_exp = self.read_from_json(data, "token_exp", None)

                f.close()

        except json.JSONDecodeError:
            print("JSONDecode Error")
            return

    def read_from_json(self, data, property_name, default_value):
        if property_name in data:
            return data[property_name]
        else:
            return default_value
