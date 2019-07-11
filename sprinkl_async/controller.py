"""Controller class for Sprinkl controllers."""
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

import logging
from typing import Awaitable, Callable

from .dataobject import DictObject
from .moisturesensors import MoistureSensors
from .pageobject import PageObject
from .schedules import Schedules
from .zones import Zones
from .webhooks import Webhooks

_LOGGER = logging.getLogger(__name__)

URL_BASE = "https://api.sprinkl.com/v1"


class Controller:
    """Controller for a Sprinkl device."""

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self, request: Callable[..., Awaitable[dict]], controller_data: dict
    ) -> None:
        """Initialize."""
        self._request = request
        self._moisture_sensors = MoistureSensors(
            self._request_controller, controller_data["moisture_sensors"]
        )
        self._weather = DictObject(controller_data["weather"])
        self._schedules = Schedules(
            self._request_controller,
            controller_data["schedules"],
            controller_data["conservation"]["seasonal_adjustments"],
        )
        self._location = DictObject(controller_data["location"])
        self._conservation = DictObject(controller_data["conservation"])
        self._zones = Zones(self._request_controller, controller_data["zones"])
        self._controller = controller_data
        self._webhooks = None

    def __getattr__(self, name):
        """Allow property access to data object."""
        if name in self._controller:
            return self._controller[name]

        return object.__getattribute__(self, name)

    async def _request_controller(
        self,
        method: str,
        path: str,
        *,
        headers: dict = None,
        params: dict = None,
        json: dict = None
    ):
        return await self._request(
            method,
            "{0}/controllers/{1}/{2}".format(URL_BASE, self._controller["id"], path),
            headers=headers,
            params=params,
            json=json,
        )

    @property
    def enabled(self) -> bool:
        """Return if the controller is enabled."""
        return self._controller["enabled"]

    @property
    def connected(self) -> bool:
        """Return if the controller is connected."""
        return self._controller["connected"]

    @property
    def webhooks(self):
        """Return helper to handle webhooks."""
        if not self._webhooks:
            self._webhooks = Webhooks(self._request_controller)
        return self._webhooks

    async def moisture_sensors(self) -> MoistureSensors:
        """Return the moister sensors."""
        return self._moisture_sensors

    async def weather(self) -> DictObject:
        """Return the weather."""
        return self._weather

    async def location(self) -> DictObject:
        """Return conservation schedule for the current controller."""
        return self._location

    async def conservation(self) -> DictObject:
        """Return conservation schedule."""
        return self._conservation

    async def schedules(self) -> Schedules:
        """Return the schedules."""
        return self._schedules

    async def zones(self) -> Zones:
        """Return the zones."""
        return self._zones

    async def history(self) -> PageObject:
        """Return history of events."""
        data = await self._request_controller("get", "history")
        return PageObject(data, self._request, "get", "history")

    async def stop(self) -> None:
        """Stop/halt the controller."""
        return await self._request_controller("post", "stop")
