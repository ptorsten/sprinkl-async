"""Define class to handle a webhook."""
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

from typing import Awaitable, Callable

from .dataobject import DictObject


class Webhook(DictObject):
    """Handle webhooks for Sprinkl cloud service."""

    def __init__(self, webhook, request: Callable[..., Awaitable[dict]]):
        """Initialize."""
        super().__init__(webhook)
        self._request = request

    async def delete(self) -> None:
        """Delete current webhook."""
        await self._request("delete", "webhooks/{0}".format(self.id))
