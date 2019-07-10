"""Define helper object for handling Sprinkl paging."""
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

from .dataobject import DictObject, ListObject


class PageObject:
    """Helper object to handle paging."""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        paged_data: dict,
        request: Callable[..., Awaitable[dict]],
        method: str,
        uri: str,
        page: int = 1,
    ) -> None:
        """Initialize."""
        self._meta = DictObject(paged_data["meta"])
        self._data = ListObject(paged_data["data"])
        self._page = page

        self._request = request
        self._method = method
        self._uri = uri

    @property
    def has_more(self) -> bool:
        """Return true if there is more pages."""
        if self._page < int(self._meta.count):
            return True
        return False

    async def next(self):
        """Return the next page."""
        if not self.has_more:
            return None

        page = self._page + 1
        data = await self._request(self._method, self._uri, params={"page": page})
        return PageObject(data, self._request, self._method, self._uri, page=page)

    @property
    def meta(self):
        """Return the meta data object."""
        return self._meta

    @property
    def data(self):
        """Return data object."""
        return ListObject(self._data)

    @property
    def json(self) -> str:
        """Return a well-formated json string."""
        return self._data.json
