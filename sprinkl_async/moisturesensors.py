"""Define moisture sensors class."""
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

from typing import Awaitable, Callable, Any, Dict

from .moisturesensor import MoistureSensor


class MoistureSensors:
    """Class for moisture sensors."""

    def __init__(self, request: Callable[..., Awaitable[dict]], sensors: list) -> None:
        """Intialize."""
        self._request = request
        self._sensors: Dict[str, Any] = {}
        for sensor in sensors:
            parsed_sensor = MoistureSensor(self._request, sensor)
            self._sensors[parsed_sensor.id] = parsed_sensor

    def __iter__(self):
        """Iterator."""
        for item in self._sensors:
            yield self._sensors[item]

    def __getitem__(self, key):
        """Get sensor by id."""
        if key in self._sensors:
            return self._sensors[key]
        raise KeyError

    def __len__(self):
        """Return number of sensors."""
        return len(self._sensors)

    def get(self, key: str):
        """Return sensor by id."""
        return self._sensors.get(key)

    def all(self, include_disabled: bool = True) -> list:
        """Return all or active sensors."""
        return [
            self._sensors[key]
            for key in self._sensors
            if include_disabled or self._sensors[key].enabled
        ]
