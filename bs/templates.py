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
from .config import Config

def status_block(block_id):
    return f"""
        <div style="margin-bottom: var(--spacing-lg); color: var(--block-info-text-color); font-weight: var(--block-info-text-weight); font-size: var(--block-info-text-size); line-height: var(--line-sm);">Status<div>
        <div style="margin-top: var(--spacing-lg); color: var(--body-text-color); font-weight: var(--checkbox-label-text-weight); font-size: var(--checkbox-label-text-size);" id="{block_id}">Idle</div>
    """

def login_endpoint_page(challenge):
    return f"""
        <script>
            const url = `{Config.isam_base_domain}/api/v3/oauth2/authorize?client_id={Config.client_id}&redirect_uri={Config.auth_redirect_url}&response_type=code&scope=v2legacy%20offline_access&state=1a2b3c4d&code_challenge={challenge}&code_challenge_method=S256`;
            window.location = url;
        </script>
        """

def registration_endpoint_page(registration_url):
    return f"""
            <script>
                localStorage.setItem("bluescapeRegistrationStarted", true);
                window.location = '{registration_url}';
            </script>
        """

def refresh_ui_page():
    return f"""
            <script>
                localStorage.setItem("bluescapeRefreshUI", true);
                window.location = "/";
            </script>
        """

bluescape_auth_function = f"""
        function bluescape_auth() {{
            window.location = '/bluescape/login';
        }}
    """

bluescape_open_workspace_function = f"""
        function open_selected_workspace() {{
            const selectedWorkspace = document.querySelector("#bluescape-open-workspace-id textarea");
            if (selectedWorkspace) {{
                workspaceId = selectedWorkspace.value;
                const url = '{Config.client_base_domain}' + '/' + workspaceId;
                window.open(url, "_blank");
            }}
        }}
    """

workspace_label_block = "Selected workspace: <b id='selected-workspace-label'></b>"