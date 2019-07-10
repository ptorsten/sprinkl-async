"""Define a zone class."""
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


class Zone(DictObject):
    """Represents a zone in the Sprinkl controller."""

    def __init__(self, data: dict, request: Callable[..., Awaitable[dict]]):
        """Initialize."""
        super().__init__(data)
        self._request = request

    @property
    def id(self) -> str:
        """Return id of zone."""
        return self.get("id")

    @property
    def number(self) -> int:
        """Return numer of zone."""
        return self.get("number")

    @property
    def enabled(self) -> bool:
        """Return if the zone is enabled."""
        return self.get("enabled")

    async def run(self, time_in_minutes: int) -> None:
        """Run the current zone."""
        await self._request(
            "post", "run", json=[{"zone": self.number, "time": time_in_minutes}]
        )
