"""Data object helpers."""
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

from typing import Any, Dict, List


class ListObject:
    """Represent a list with property access to sub-dict/list objects."""

    # pylint: disable=unused-variable
    def __init__(self, data: list):
        """Initialize."""
        self._data = []  # type: List[Any]
        for pos, item in enumerate(data):
            if isinstance(item, dict):
                self._data.append(DictObject(item))
            elif isinstance(item, list):
                self._data.append(ListObject(item))
            else:
                self._data.append(item)

    def __iter__(self):
        """Iterator."""
        for item in self._data:
            yield item

    def __getitem__(self, idx):
        """Iterator."""
        if idx < 0 or idx >= len(self._data):
            raise KeyError

        return self._data[idx]

    def __len__(self):
        """Return number of items."""
        return len(self._data)

    def get(self, idx):
        """Return item based on index."""
        return self._data[idx]

    @property
    def data(self):
        """Return data object."""
        return self._data


class DictObject:
    """Represent a dict with property access to sub-dict/list objects."""

    def __init__(self, data: dict):
        """Initialize."""
        self._data = {}  # type: Dict[Any, Any]
        for key in data:
            if isinstance(data[key], dict):
                self._data[key] = DictObject(data[key])
            elif isinstance(data[key], list):
                self._data[key] = ListObject(data[key])
            else:
                self._data[key] = data[key]

    def __getattr__(self, name):
        """Allow property name access to data."""
        if name in self._data:
            return self._data[name]

        return object.__getattribute__(self, name)

    def __iter__(self):
        """Iterator."""
        for item in self._data:
            yield item

    def __getitem__(self, key):
        """Iterator."""
        if key in self._data:
            return self._data[key]
        raise KeyError

    def __len__(self):
        """Return number of items."""
        return len(self._data)

    def get(self, key):
        """Return key."""
        return self._data.get(key)

    @property
    def data(self):
        """Return data object."""
        return self._data
