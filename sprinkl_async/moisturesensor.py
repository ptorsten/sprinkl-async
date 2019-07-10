"""Define moisture sensor class."""
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

from typing import Any, Awaitable, Callable, List

from .pageobject import PageObject


class MoistureSensor:
    """Class for a moisture sensor."""

    def __init__(self, request: Callable[..., Awaitable[dict]], sensor: dict) -> None:
        """Initialize."""
        self._request = request
        self._data = sensor
        # not useful data (no timestamps)
        del self._data["temps"]
        del self._data["moistures_t"]
        del self._data["moistures_m"]
        del self._data["moistures_b"]

        # convert so we are consistent
        self._data["moisture_1"] = self._data["moisture_t"]
        self._data["moisture_3"] = self._data["moisture_m"]
        self._data["moisture_5"] = self._data["moisture_b"]

        del self._data["moisture_t"]
        del self._data["moisture_m"]
        del self._data["moisture_b"]

    def __getattr__(self, name):
        """Allow property access of data object."""
        if name in self._data:
            return self._data[name]

        return object.__getattribute__(self, name)

    async def readings(self) -> PageObject:
        """Return sensor readings."""
        data = await self._request("get", "sensors/{0}/readings".format(self.id))

        return PageObject(
            data, self._request, "get", "sensors/{0}/readings".format(self.id)
        )

    async def averages_day(self) -> PageObject:
        """Return average of day from sensor readings."""
        data = await self._request(
            "get", "sensors/{0}/readings/averages/day".format(self.id)
        )

        return PageObject(
            data,
            self._request,
            "get",
            "sensors/{0}/readings/averages/day".format(self.id),
        )

    async def averages_hour(self) -> PageObject:
        """Return average of hour from sensor readings."""
        data = await self._request(
            "get", "sensors/{0}/readings/averages/hour".format(self.id)
        )

        return PageObject(
            data,
            self._request,
            "get",
            "sensors/{0}/readings/averages/hour".format(self.id),
        )

    async def refresh(self) -> None:
        """Refresh sensor object from Sprinkl controller."""
        data = await self._request("get", "sensors/{0}".format(self.id))
        for key in data["data"]:
            self._data[key] = data["data"][key]
