"""Authentication helper class."""
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

from datetime import datetime
from typing import Optional


class AuthToken:
    """Authenticate token helper class."""

    def __init__(
        self,
        refresh_token: Optional[str] = "",
        refresh_ts: Optional[datetime] = None,
        token: Optional[str] = "",
        user_id: Optional[str] = "",
    ) -> None:
        """Initialize."""
        self._token = token
        self._refresh_ts = refresh_ts
        self._refresh_token = refresh_token
        self._user_id = user_id

    @property
    def token(self):
        """Return active token."""
        return self._token

    @property
    def refresh_token(self):
        """Return refresh token."""
        return self._refresh_token

    @property
    def refresh_timestamp(self):
        """Return timestmap of when token needs to be refreshed."""
        return self._refresh_ts

    @property
    def user_id(self):
        """Return user id."""
        return self._user_id

    @property
    def is_valid(self):
        """Return true if token is valid."""
        if not self._refresh_ts:
            return False

        return datetime.now() < self._refresh_ts

    def __repr__(self):
        """Return repr of object."""
        return "AuthToken(%s, %s, %s, %s)" % (
            self._refresh_token.__repr__(),
            self._refresh_ts.__repr__(),
            self._token.__repr__(),
            self._user_id.__repr__(),
        )
