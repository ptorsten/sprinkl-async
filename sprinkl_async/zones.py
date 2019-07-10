"""Define a class to hold all zones."""
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

from typing import Awaitable, Any, Dict, Callable

from .zone import Zone


class Zones:
    """Represents all zones in a controller."""

    def __init__(self, request: Callable[..., Awaitable[dict]], zones: list):
        """Initialize."""
        self._request = request
        self._zones = {}  # type: Dict[str, Any]
        for item in zones:
            zone = Zone(item, request)
            self._zones[zone.id] = zone

    def __iter__(self):
        """Iterator."""
        for item in self._zones:
            yield item

    def __getitem__(self, key):
        """Iterator."""
        if key in self._zones:
            return self._zones[key]
        raise KeyError

    def __len__(self):
        """Return number of zones."""
        return len(self._zones)

    def get(self, idx: str):
        """Get zone by id."""
        return self._zones.get(idx)

    def get_by_number(self, number: int):
        """Get zone by number."""
        for pos, (key, zone) in enumerate(self._zones.items()):
            if zone.number == number:
                return zone

        raise KeyError()

    # pylint: disable=unused-variable
    async def run(self, run_zones: list):
        """Run zones."""
        run_list = []
        for item in run_zones:
            if not isinstance(item, dict):
                raise Exception("run takes a list of dict(zone-number, time)")

            if len(item) != 1:
                raise Exception("run takes a list of dict(zone-number, time)")

            for pos, (zone, time) in enumerate(item.items()):
                run_list.append({"zone": zone, "time": time})

        return await self._request("post", "run", json=run_list)

    async def skip(self):
        """Skip the current running zone and go to the next in the queue."""
        return await self._request("post", "skip")
