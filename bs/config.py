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
import os

class Config:

    api_base_domain = os.getenv('BS_API_BASE_DOMAIN', 'https://api.apps.us.bluescape.com')
    client_base_domain = os.getenv('BS_CLIENT_BASE_DOMAIN', 'https://client.apps.us.bluescape.com')
    analytics_base_domain = os.getenv('BS_ANALYTICS_BASE_DOMAIN', 'https://analytics-api.apps.us.bluescape.com')
    isam_base_domain =  os.getenv('BS_ISAM_BASE_DOMAIN', 'https://isam.apps.us.bluescape.com')
    client_id = os.getenv('BS_CLIENT_ID', 'cbc5407f-1860-4a47-a61f-ec135715aea0')
    auth_redirect_url = os.getenv('BS_AUTH_REDIRECT', 'http://localhost:7860/bluescape/oauth_callback')
