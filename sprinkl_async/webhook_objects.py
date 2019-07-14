"""Define classes for webhook events."""
#
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .dataobject import DictObject


class WebhookBaseObject:
    """Base object for all webhook objects."""

    def __init__(self, obj):
        """Intialize."""
        self._device_id = obj["device_id"]
        self._webhook_id = obj["webhook_id"]
        self._external_id = obj["external_id"]
        self._event = obj["event"]
        self._event_data = DictObject(obj["event_data"])

    @property
    def device_id(self):
        """Return device id."""
        return self._device_id

    @property
    def webhook_id(self):
        """Return webhook id."""
        return self._webhook_id

    @property
    def external_id(self):
        """Return external id."""
        return self._external_id

    @property
    def event(self):
        """Return event type."""
        return self._event

    @property
    def data(self) -> DictObject:
        """Return event data."""
        return self._event_data
