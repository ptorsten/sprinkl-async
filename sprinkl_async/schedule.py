"""Define schedule class."""
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
from datetime import date
from typing import Awaitable, Callable

from .dataobject import DictObject


class Schedule(DictObject):
    """Defines a schedule."""

    def __init__(
        self, request: Callable[..., Awaitable[dict]], adjustments: dict, schedule: dict
    ):
        """Intialize."""
        super().__init__(schedule)
        self._request = request
        self._adjustments = adjustments

    @property
    def enabled(self) -> bool:
        """Return true if sechedule is enabled."""
        return self.get("enabled")

    async def run(self, use_seasonal_adjustment: bool = False) -> None:
        """Run a schedule manually with adjustments if needed."""
        zones_to_run = []

        for zone in self.zones:
            run_time = zone.run_time
            if use_seasonal_adjustment:
                run_time = round(
                    run_time * (self._adjustments[date.today().month - 1] / 100)
                )

            zones_to_run.append({"zone": zone.number, "time": run_time})

        await self._request("post", "run", json=zones_to_run)
