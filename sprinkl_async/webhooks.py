"""Define class to handle webhooks."""
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

from typing import Awaitable, Callable, List

from .errors import InvalidWebhookEvent
from .dataobject import ListObject
from .webhook import Webhook


class Webhooks:
    """Handle webhooks for Sprinkl cloud service."""

    def __init__(self, request: Callable[..., Awaitable[dict]]) -> None:
        """Initialize."""
        self._request = request
        self._events = None

    async def create(self, external_id: str, url: str, events: List[str]) -> Webhook:
        """Create a new webhook for this controller."""
        supported_events = await self.events()
        for event in events:
            if event not in supported_events:
                raise InvalidWebhookEvent()

        wh_create = {"external_id": external_id, "url": url, "events": events}

        create = await self._request("post", "webhooks", json=wh_create)
        return Webhook(create["data"], self._request)

    async def events(self) -> List[str]:
        """List all webhook events."""
        if self._events:
            return self._events

        events = await self._request("get", "webhooks/events")
        self._events = events["data"]
        assert self._events is not None
        return self._events

    async def get(self, ident: str) -> Webhook:
        """Get webhook by id."""
        webhook = await self._request("get", "webhooks/{0}".format(ident))
        return Webhook(webhook["data"], self._request)

    async def delete(self, ident: str) -> None:
        """Delete webhook by id."""
        await self._request("delete", "webhooks/{0}".format(ident))

    async def all(self) -> ListObject:
        """Return all active webhooks."""
        webhooks = await self._request("get", "webhooks")
        return ListObject([Webhook(item, self._request) for item in webhooks["data"]])

    async def find(self, external_id: str) -> ListObject:
        """Find all webhooks matching a external id."""
        webhooks = await self.all()
        hooks = [webhook for webhook in webhooks if webhook.external_id == external_id]
        return ListObject(hooks)
