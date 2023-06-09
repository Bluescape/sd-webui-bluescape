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
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Tuple
from .expired_token_exception import ExpiredTokenException
from .templates import bluescape_auth_function, bluescape_open_workspace_function, login_endpoint_page, refresh_ui_page, registration_endpoint_page
from .config import Config
from .analytics import Analytics
from .bluescape_api import bs_create_extended_data, bs_create_canvas_at, bs_create_generation_label, bs_create_generation_data, bs_create_label, bs_create_seed, bs_create_top_title, bs_find_space, bs_get_existing_canvases, bs_upload_image_at, bs_get_user_info
from .state_manager import StateManager
from .misc import CanvasHeaderStrategy, extract_workspace_id, extract_token_exp, CanvasTitleStrategy, SuggestedCanvasBorderColors
import gradio as gr
import modules.scripts as scripts
import uuid
import math
import pkce
from modules import script_callbacks
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
import random

class BluescapeUploadManager:

    state = StateManager()
    analytics = Analytics(state)

    def initialize(self):
        self.state.load()
        script_callbacks.on_ui_tabs(self.on_ui_tabs)
        script_callbacks.on_app_started(self.on_app_start)

    def bluescape_login_endpoint(self):
        self.code_verifier, challenge = pkce.generate_pkce_pair()
        return login_endpoint_page(challenge)

    def bluescape_oauth_callback_endpoint(self, code):
        print("Received callback on /bluescape/oauth_callback")
        url = f"{Config.isam_base_domain}/api/v3/oauth2/token"

        response = requests.post(url, headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        },

        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': Config.client_id,
            'redirect_uri': Config.auth_redirect_url,
            'code_verifier': self.code_verifier
        })

        if response.status_code == 200:
            response_info = json.loads(response.text)
            token = response_info['access_token']
            user_id, user_name = bs_get_user_info(token)
            # refresh_workspaces saves state afterwards
            self.state.user_token = token
            self.state.user_id = user_id
            self.state.user_name = user_name
            self.state.token_exp = extract_token_exp(token)

            self.state.save()
            self.state.token_expired = False
            self.analytics.send_user_logged_in_event(token, user_id)
            self.state.refresh_workspaces(token)
            return refresh_ui_page()
        else:
            print("OAuth error:")
            print(response.text)

    def bluescape_logout_endpoint(self):
        print("User data is flushed")
        self.state.flush_user_data()
        return refresh_ui_page()

    def bluescape_status_endpoint(self):

        # Check whether token expired
        # The token expiration is in UTC, so we need to get the
        # now in utc timezone as well
        now = math.trunc(datetime.now(tz=timezone.utc).timestamp())
        if self.state.token_exp is not None and now > self.state.token_exp:
            self.state.token_expired = True
        else:
            self.state.token_expired = False

        selected_workspace_item = self.get_selected_workspace_item()
        if selected_workspace_item is None:
            selected_workspace_item = " "

        return self.state.txt2img_status + "\n" + self.state.img2img_status + "\n" + selected_workspace_item + "\n" + str(self.state.token_expired)

    def bluescape_register_endpoint(self):
        registration_attempt_id = str(uuid.uuid4())
        self.analytics.send_user_attempting_registration_event(registration_attempt_id)
        registration_url = f"{Config.client_base_domain}/signup?utm_campaign=automatic_offer&utm_source=campaign_signup&utm_term={registration_attempt_id}"

        return registration_endpoint_page(registration_url)

    def set_status(self, status, is_txt2img):
        if is_txt2img:
            self.state.txt2img_status = status
        else:
            self.state.img2img_status = status

    def on_app_start(self, _, app: FastAPI):
        app.add_api_route("/bluescape/login", self.bluescape_login_endpoint, methods=["GET"],
        response_class=HTMLResponse)
        app.add_api_route("/bluescape/oauth_callback", self.bluescape_oauth_callback_endpoint, methods=["GET"],
        response_class=HTMLResponse)
        app.add_api_route("/bluescape/registration", self.bluescape_register_endpoint, methods=["GET"], response_class=HTMLResponse)
        app.add_api_route("/bluescape/logout", self.bluescape_logout_endpoint, methods=["GET"], response_class=HTMLResponse)
        app.add_api_route("/bluescape/status", self.bluescape_status_endpoint, methods=["GET"], response_class=HTMLResponse)
        print("Bluescape endpoints have been mounted")

    def upload_image_at(self, buffer, filename, bounding_box: Tuple[int, int, int, int], traits):
        bs_upload_image_at(self.state.user_token, self.state.selected_workspace_id, buffer, filename, bounding_box, traits)

    def create_canvas_at(self, title, bounding_box: Tuple[int, int, int, int], traits, canvas_color):
        return bs_create_canvas_at(self.state.user_token, self.state.selected_workspace_id, title, bounding_box, traits, canvas_color)

    def find_space(self, bounding_box: Tuple[int, int, int, int], direction) -> Tuple[int, int, int, int]:
        return bs_find_space(self.state.user_token, self.state.selected_workspace_id, bounding_box, direction)

    def get_existing_canvases(self):
        return bs_get_existing_canvases(self.state.user_token, self.state.selected_workspace_id)

    def create_top_title(self, location: Tuple[int, int, int], title, header):
        return bs_create_top_title(self.state.user_token, self.state.selected_workspace_id, location, title, header)

    def create_extended_data(self, location: Tuple[int, int, int], extended_generation_data):
        return bs_create_extended_data(self.state.user_token, self.state.selected_workspace_id, location, extended_generation_data)

    def create_generation_data(self, location: Tuple[int, int, int], infotext):
        return bs_create_generation_data(self.state.user_token, self.state.selected_workspace_id, location, infotext)

    def create_seed_label(self, location: Tuple[int, int, int], seed, subseed):
        return bs_create_seed(self.state.user_token, self.state.selected_workspace_id, location, seed, subseed)

    def create_label(self, location: Tuple[int, int, int], text):
        return bs_create_label(self.state.user_token, self.state.selected_workspace_id, location, text)

    def create_generation_label(self, location: Tuple[int, int, int], text):
        return bs_create_generation_label(self.state.user_token, self.state.selected_workspace_id, location, text)

    def get_enable_verbose(self):
        return self.state.enable_verbose

    def get_img2img_include_init_images(self):
        return self.state.img2img_include_init_images

    def get_img2img_include_mask_image(self):
        return self.state.img2img_include_mask_image

    def get_scale_to_standard_size(self):
        return self.state.scale_to_standard_size

    def get_enable_metadata(self):
        return self.state.enable_metadata

    def get_enable_analytics(self):
        return self.state.enable_analytics

    def get_user_swimlane(self):
        return self.state.user_swimlane

    def get_use_canvas_border_color(self):
        return self.state.use_canvas_border_color

    def is_empty_user_token(self):
        return self.state.user_token == ""

    def get_user_token(self):
        return self.state.user_token

    def get_workspace_dd(self):
        return self.state.workspace_dd

    def get_selected_workspace_item(self):
        return self.state.get_selected_workspace_item()

    def get_canvas_title(self):
        return self.state.canvas_title_strategy

    def get_canvas_header(self):
        return self.state.canvas_header_strategy

    def get_canvas_border_color(self):
        color = self.state.canvas_border_color
        return color if color else random.choice(list(SuggestedCanvasBorderColors)).value

    def get_nick_name(self):
        name = self.state.nick_name
        return name if name else self.state.user_name

    def on_ui_tabs(self):

        with gr.Blocks() as bluescape_tab:

            token_source = gr.Textbox(self.get_user_token, visible=False)

            # Outputs: workspaces_dropdown, workspace_to_open_textbox, register_button, refresh_workspaces_button, open_workspace_button, login_button, logout_button
            def refresh_workspaces_and_ui(input):
                try:
                    self.state.refresh_workspaces(input)
                    ws_value = self.state.workspace_ids.get(self.state.selected_workspace_id, self.state.workspace_dd[0])
                    return [
                        gr.Dropdown.update(choices=self.state.workspace_dd, visible=True, value=ws_value),
                        gr.Textbox.update(value=self.state.selected_workspace_id),
                        gr.Button.update(visible=False),
                        gr.Button.update(visible=True),
                        gr.Button.update(visible=True),
                        gr.Button.update(visible=False),
                        gr.Button.update(visible=True)
                    ]
                except ExpiredTokenException:
                    print("Bluescape token has expired")
                    self.state.token_expired = True
                    self.state.user_token = ""
                    self.state.save()

                    return [
                        gr.Dropdown.update(choices=[], visible=False, value=''),
                        gr.Textbox.update(value=self.state.selected_workspace_id),
                        gr.Button.update(visible=True),
                        gr.Button.update(visible=False),
                        gr.Button.update(visible=False),
                        gr.Button.update(visible=True),
                        gr.Button.update(visible=False),
                        gr.Checkbox.update(visible=True)
                    ]

            with gr.Row():
                with gr.Column():
                    with gr.Row():
                        gr.Markdown(elem_id="bs-token-expired-tip", value=
                            """
                            # 🔴 Access to Bluescape has expired. Please login again.

                            """
                        )
                    with gr.Row(variant="panel"):
                        gr.Markdown(
                            """
                            # Instructions

                            Get started using the Bluescape extension:

                            1. **Register**: If you haven't done so yet, register for a free account
                            2. **Login**: Log into your account
                            3. **Select Workspace**: Choose the workspace where you'd like to upload generated images
                            4. **Enable Upload Option**: Navigate to either the 'txt2img' or 'img2img' tab and select the "Upload results to Bluescape" option
                            5. **Review**: Open your workspace to review, curate and collaborate on the generated images


                            _Tip: Generation data added to the Bluescape workspace can be copied back to Automatic1111 and re-applied through the prompt._
                            """
                        )
                    with gr.Row():
                        with gr.Column():
                            login_button = gr.Button(value="Login", elem_id="bluescape-login-button", visible=self.is_empty_user_token())
                            logout_button = gr.Button(value="Logout", elem_id="bluescape-logout-button", visible=(not self.is_empty_user_token()))
                        with gr.Column():
                            register_button = gr.Button(value="Register for a free account", visible=self.is_empty_user_token())
                    with gr.Row():
                        workspaces_dropdown = gr.Dropdown(choices=self.get_workspace_dd(), label="Select target workspace:", value=self.get_selected_workspace_item, elem_id="bluescape-workspaces-dropdown", visible=(not self.is_empty_user_token()))
                    with gr.Row():
                        with gr.Column():
                            workspace_to_open_textbox = gr.Textbox(label="Workspace to open", value=self.get_selected_workspace_item, elem_id="bluescape-open-workspace-id", visible=False)
                            open_workspace_button = gr.Button("Open target workspace", visible=(not self.is_empty_user_token()))
                        with gr.Column():
                            refresh_workspaces_button = gr.Button("Refresh workspaces", visible=(not self.is_empty_user_token()))
                    with gr.Row():
                        gr.Markdown(
                            """
                            # Configuration
                            _See [documentation](https://github.com/Bluescape/sd-webui-bluescape#configuration-options) for further details on each configuration option._
                            ## General
                            """)
                    enable_verbose_checkbox = gr.Checkbox(label="Include extended generation data in workspace", value=self.get_enable_verbose, interactive=True)
                    img2img_include_init_images_checkbox = gr.Checkbox(label="Include source image in workspace (img2img)", value=self.get_img2img_include_init_images, interactive=True)
                    img2img_include_mask_image_checkbox = gr.Checkbox(label="Include image mask in workspace (img2img)", value=self.get_img2img_include_mask_image, interactive=True)
                    scale_to_standard_size_checkbox = gr.Checkbox(label="Scale images to standard size (1000x1000) in workspace", value=self.get_scale_to_standard_size, interactive=True)
                    enable_metadata_checkbox = gr.Checkbox(label="Store generation data as metadata in image object within workspace", value=self.get_enable_metadata, interactive=True)
                    enable_analytics_checkbox = gr.Checkbox(label="Send extension usage analytics", value=self.get_enable_analytics, interactive=True)

                    with gr.Row():
                        gr.Markdown(
                            """
                            ## Canvas
                            """)
                    canvas_title_dropdown = gr.Dropdown(label="Title format", choices=[strategy.value for strategy in CanvasTitleStrategy], value=self.get_canvas_title, interactive=True)
                    canvas_header_dropdown = gr.Dropdown(label="Header format", choices=[strategy.value for strategy in CanvasHeaderStrategy], value=self.get_canvas_header, interactive=True)
                    user_swimlane_checkbox = gr.Checkbox(label="User specific canvas placement", value=self.get_user_swimlane, interactive=True)
                    with gr.Row():
                        with gr.Column():
                            use_canvas_border_color_checkbox = gr.Checkbox(label="Use canvas border color", value=self.get_use_canvas_border_color, interactive=True)
                        with gr.Column():
                            canvas_border_color_picker = gr.ColorPicker(label="Color", value=self.get_canvas_border_color, interactive=True)

                    nickname_textbox = gr.Textbox(label="Override user name for title and header", interactive=True, value=self.get_nick_name)

                    with gr.Row(variant="panel"):
                        gr.Markdown(
                            """
                            # Feedback

                            Feel free to send us any feedback you may have. Whether it's praise or constructive criticism.

                            To share your thoughts, click [here](https://community.bluescape.com/t/stable-diffusion-automatic1111-bluescape-extension/3730)

                            For further documentation on the project visit [Github](https://github.com/Bluescape/sd-webui-bluescape)
                            """
                        )

                    token_source.change(refresh_workspaces_and_ui, inputs=[token_source], outputs=[workspaces_dropdown, workspace_to_open_textbox, register_button, refresh_workspaces_button, open_workspace_button, login_button, logout_button])


                with gr.Column():
                    # Used to force a second column for better page layout
                    gr.Textbox(label="dummy", interactive=False, visible=False, value="dummy")

            def selected_workspace_change(input):
                if input is not None and input != "":
                    self.state.selected_workspace_id = extract_workspace_id(input)
                    self.state.save()

                    return gr.Textbox.update(value=self.state.selected_workspace_id)

            def enable_analytics_change(input):
                self.state.enable_analytics = input
                self.state.save()

            def user_swimlane_change(input):
                self.state.user_swimlane = input
                self.state.save()

            def canvas_border_color_change(input):
                self.state.canvas_border_color = input
                self.state.save()

            def use_canvas_border_color_change(input):
                self.state.use_canvas_border_color = input
                self.state.save()

            def enable_verbose_change(input):
                self.state.enable_verbose = input
                self.state.save()

            def enable_metadata_change(input):
                self.state.enable_metadata = input
                self.state.save()

            def img2img_include_init_images_change(input):
                self.state.img2img_include_init_images = input
                self.state.save()

            def img2img_include_mask_image_change(input):
                self.state.img2img_include_mask_image = input
                self.state.save()

            def scale_to_standard_size_change(input):
                self.state.scale_to_standard_size = input
                self.state.save()

            def canvas_title_dropdown_change(input):
                self.state.canvas_title_strategy = input
                self.state.save()

            def canvas_header_dropdown_change(input):
                self.state.canvas_header_strategy = input
                self.state.save()

            def nickname_textbox_change(input):
                self.state.nick_name = input
                self.state.save()

            # Event handlers assignment
            login_button.click(None, _js=bluescape_auth_function)
            logout_button.click(None, _js="bluescape_logout")
            open_workspace_button.click(None, _js=bluescape_open_workspace_function)
            register_button.click(None, _js="bluescape_registration")
            refresh_workspaces_button.click(refresh_workspaces_and_ui, inputs=[token_source], outputs=[workspaces_dropdown, workspace_to_open_textbox, register_button, refresh_workspaces_button, open_workspace_button, login_button, logout_button])
            workspaces_dropdown.change(selected_workspace_change, inputs=[workspaces_dropdown], outputs=[workspace_to_open_textbox])
            enable_verbose_checkbox.change(enable_verbose_change, inputs=[enable_verbose_checkbox])
            img2img_include_init_images_checkbox.change(img2img_include_init_images_change, inputs=[img2img_include_init_images_checkbox])
            img2img_include_mask_image_checkbox.change(img2img_include_mask_image_change, inputs=[img2img_include_mask_image_checkbox])
            scale_to_standard_size_checkbox.change(scale_to_standard_size_change, inputs=[scale_to_standard_size_checkbox])
            enable_metadata_checkbox.change(enable_metadata_change, inputs=[enable_metadata_checkbox])
            enable_analytics_checkbox.change(enable_analytics_change, inputs=[enable_analytics_checkbox])
            user_swimlane_checkbox.change(user_swimlane_change, inputs=[user_swimlane_checkbox])
            canvas_border_color_picker.change(canvas_border_color_change, inputs=[canvas_border_color_picker])
            use_canvas_border_color_checkbox.change(use_canvas_border_color_change, inputs=[use_canvas_border_color_checkbox])
            canvas_title_dropdown.change(canvas_title_dropdown_change, inputs=[canvas_title_dropdown])
            canvas_header_dropdown.change(canvas_header_dropdown_change, inputs=[canvas_header_dropdown])
            nickname_textbox.change(nickname_textbox_change, inputs=[nickname_textbox])

        return ((bluescape_tab, "Bluescape", "bluescape-tab"),)
