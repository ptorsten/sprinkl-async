"""Define a class to hold schedule classes."""
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
from typing import Awaitable, Callable, Dict, Any

from .schedule import Schedule


class Schedules:
    """Defines the schedules for a controller."""

    def __init__(
        self,
        request: Callable[..., Awaitable[dict]],
        schedules: dict,
        adjustments: dict,
    ) -> None:
        """Intialize."""
        self._adjustments = adjustments
        self._schedules: Dict[str, Any] = {}
        for schedule in schedules:
            parsed_schedule = Schedule(request, adjustments, schedule)
            self._schedules[parsed_schedule.id] = parsed_schedule

    def __iter__(self):
        """Iterator."""
        for item in self._schedules:
            yield self._schedules[item]

    def __getitem__(self, key):
        """Get sensor by id."""
        if key in self._schedules:
            return self._schedules[key]
        raise KeyError

    def __len__(self):
        """Return number of schedules."""
        return len(self._schedules)

    def get(self, key: str):
        """Return sensor by id."""
        return self._schedules.get(key)

    async def all(self, include_disabled: bool = True) -> list:
        """Return all or active schedules."""
        return [
            self._schedules[key]
            for key in self._schedules
            if include_disabled or self._schedules[key].enabled
        ]
