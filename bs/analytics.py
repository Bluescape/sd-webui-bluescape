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
from datetime import datetime
from .state_manager import StateManager
import requests
from .config import Config

class AnalyticsEvent:
    componentId = str
    category = str
    type = str
    containsPII = bool
    containsConfidential = bool
    date = datetime
    organizationId = str
    workspaceId = str
    actorType = str
    data = object

class Analytics:

    category = "AI"
    componentId = "automatic1111-extension"

    def __init__(self, state: StateManager):
        self.state = state

    # Public

    def send_user_attempting_registration_event(self, registration_attempt_id):
        e = AnalyticsEvent()
        e.category = self.category
        e.componentId = self.componentId
        e.type = "UserAttemptingRegistration"
        e.containsPII = False
        e.containsConfidential = False
        e.workspaceId = None
        e.date = datetime.now()
        e.data = {
            "registrationAttemptId": registration_attempt_id,
            "a1111Version": self.state.a1111_version,
            "extensionVersion": self.state.extension_version
        }

        self.send_event(e, None)

    def send_user_logged_in_event(self, token, user_id):
        e = AnalyticsEvent()
        e.category = self.category
        e.componentId = self.componentId
        e.type = "UserLoggedIn"
        e.containsPII = False
        e.containsConfidential = False
        e.workspaceId = None
        e.date = datetime.now()
        e.data = {
            "userId": user_id,
            "a1111Version": self.state.a1111_version,
            "extensionVersion": self.state.extension_version
        }

        self.send_event(e, token)

    def send_uploaded_generated_images_event(self, token, workspace_id, images_number, user_id):
        e = AnalyticsEvent()
        e.category = self.category
        e.componentId = self.componentId
        e.type = "UserUploadedGeneratedImages"
        e.containsPII = False
        e.containsConfidential = False
        e.workspaceId = workspace_id
        e.date = datetime.now()
        e.data = {
            "imageCount": images_number,
            "userId": user_id,
            "a1111Version": self.state.a1111_version,
            "extensionVersion": self.state.extension_version
        }

        self.send_event(e, token)

    # Private

    def send_event(self, e: AnalyticsEvent, token):

        if self.state.enable_analytics:
            body = {
                'events': [
                    {
                        'category': e.category,
                        'componentId': e.componentId,
                        'type': e.type,
                        'containsPII': e.containsPII,
                        'containsConfidential': e.containsConfidential,
                        'date': datetime.utcnow().isoformat() + 'Z',
                        'data': e.data,
                    }
                ]
            }

            if e.workspaceId is not None:
                body['events'][0]['workspaceId'] = e.workspaceId

            url = f'{Config.analytics_base_domain}/api/v3/collect'
            response = requests.post(url, json = body, headers = self.get_headers(token))
            if response.status_code != 200:
                print("Analytics response: " + str(response.text))

    def get_headers(self, token):
        if token is not None:
            return {
                #'Authorization': f'Bearer {token}',
                'Content-type': 'application/json'
            }

        return {
            'Content-type': 'application/json'
        }
