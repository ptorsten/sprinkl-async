"""Client class for Sprinkl controllers."""
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

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import async_timeout
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientResponseError

from .authtoken import AuthToken
from .const import (
    DEFAULT_TIMEOUT,
    SPRINKL_AUTH_ENDPOINT,
    SPRINKL_ENDPOINT,
    TOKEN_LIFETIME,
    USER_AGENT,
)
from .controller import Controller
from .errors import (
    AuthenticateError,
    ControllerAlreadyRunning,
    RequestError,
    RequestTimeout,
    TokenExpired,
)

_LOGGER = logging.getLogger(__name__)


class Client:
    """Client class for Sprinkl controllers."""

    def __init__(
        self,
        websession: ClientSession,
        timeout: Optional[int] = DEFAULT_TIMEOUT,
        ssl: Optional[bool] = True,
        proxy: Optional[str] = None,
    ) -> None:
        """Initialize."""
        self._websession = websession
        self._timeout = timeout
        self._ssl = ssl
        self._proxy = proxy
        self._auth = None  # type: Union[AuthToken, None]

    async def _request(
        self,
        method: str,
        url: str,
        *,
        authorization: Optional[str] = None,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        reauth_token: Optional[bool] = False
    ) -> Dict[Any, Any]:
        if not headers:
            headers = {}
        if not params:
            params = {}

        headers.update({"User-Agent": USER_AGENT, "Content-Type": "application/json"})

        if authorization:
            headers.update({"Authorization": authorization})

        if not authorization and self._auth:
            headers.update({"Authorization": self._auth.token})

        try:
            while True:
                try:
                    async with async_timeout.timeout(self._timeout):
                        async with self._websession.request(
                            method,
                            url,
                            headers=headers,
                            params=params,
                            json=json,
                            ssl=self._ssl,
                            proxy=self._proxy,
                        ) as response:
                            await _throw_api_exception(response)
                            response.raise_for_status()
                            return await response.json(content_type=None)
                except TokenExpired as err:
                    if not self._auth or not reauth_token:
                        if self._auth is None:
                            _LOGGER.error("Reqest to re-auth but no auth token.")
                        raise err
                    # Try re-auth only once
                    reauth_token = False
                    self._auth = await self._try_refresh_token_auth(self._auth)
                    if self._auth is None:
                        _LOGGER.error("Failed to refresh token while doing re-auth.")
                except ClientResponseError as err:
                    _LOGGER.error("Request error: %s (%s)", err, type(err))
                    raise RequestError(err)
        except asyncio.TimeoutError as err:
            raise RequestTimeout(err)

    async def _try_refresh_token_auth(
        self, auth_info: AuthToken
    ) -> Union[AuthToken, None]:
        try:
            auth = await self._request(
                "post",
                SPRINKL_AUTH_ENDPOINT,
                params={"refresh_token": auth_info.refresh_token},
            )
            return _create_auth_info(auth)
        except AuthenticateError as err:
            _LOGGER.error(
                "Failed to authenticate while getting refresh token. (%s)", str(err)
            )
            return None

    async def _try_login(
        self, email: Optional[str], password: Optional[str]
    ) -> AuthToken:
        if email is None or password is None:
            raise AuthenticateError("Failed to login with credentials")

        auth = await self._request(
            "post", SPRINKL_AUTH_ENDPOINT, json={"email": email, "password": password}
        )
        return _create_auth_info(auth)

    async def _get_controllers(self, auth_info: AuthToken) -> List[Any]:
        controllers = await self._request(
            "get", SPRINKL_ENDPOINT + "/controllers", authorization=auth_info.token
        )
        return controllers["data"]

    def _parse_controllers(self, controllers: list) -> dict:
        parsed = {}
        for controller in controllers:
            obj = Controller(self._request, controller)
            parsed[obj.id] = obj
        return parsed

    @property
    def auth_info(self):
        """Return active authentication information."""
        return self._auth

    # pylint: disable=attribute-defined-outside-init
    async def login(
        self, email: str = None, password: str = None, auth_info: AuthToken = None
    ) -> Union[AuthToken, None]:
        """Login to Sprinkl cloud and get all controllers."""
        controllers = None
        if auth_info:
            if auth_info.is_valid:
                try:
                    controllers = await self._get_controllers(auth_info)
                except TokenExpired:
                    # Try using refresh token
                    if auth_info.refresh_token:
                        auth_info = await self._try_refresh_token_auth(auth_info)
                    else:
                        auth_info = None
                except AuthenticateError:
                    # just continue and try to login
                    auth_info = None
                    pass
            else:
                # Try using refresh token
                if auth_info.refresh_token:
                    auth_info = await self._try_refresh_token_auth(auth_info)
                else:
                    auth_info = None

        # Try to login if refresh / controller failed
        if not auth_info:
            auth_info = await self._try_login(email, password)

        if not controllers:
            controllers = await self._get_controllers(auth_info)

        self._controllers = self._parse_controllers(controllers)
        self._auth = auth_info

        return auth_info

    async def controllers(self) -> list:
        """Return controllers."""
        return [self._controllers[key] for key in self._controllers]

    async def get(self, idx: str) -> Controller:
        """Get controller by index."""
        return self._controllers[idx]


def _create_auth_info(auth: dict) -> AuthToken:
    return AuthToken(
        token=auth["data"]["token"],
        refresh_token=auth["data"]["refresh_token"],
        refresh_ts=datetime.now() + TOKEN_LIFETIME,
        user_id=auth["data"]["user_id"],
    )


# pylint: disable=broad-except
async def _get_response_json(response) -> Any:
    try:
        return await response.json(content_type=None)
    except Exception as err:
        _LOGGER.info(
            "_get_response_json() Failed to parse json: %s (%s)", err, type(err)
        )
        # broken json for some errors
        pass
    return None


async def _throw_api_exception(response) -> None:
    if response.status == 403:
        json = await _get_response_json(response)
        if (
            json
            and "errors" in json
            and len(json["errors"]) == 1
            and json["errors"][0]["detail"] == "Controller is already running"
        ):
            raise ControllerAlreadyRunning()

    if response.status == 401:
        # TODO(totte): not sure this is a good idea - maybe just always try to refresh token
        json = await _get_response_json(response)
        if (
            json
            and "errors" in json
            and len(json["errors"]) == 1
            and json["errors"][0]["detail"] == "Token has expired"
        ):
            raise TokenExpired()

        raise AuthenticateError()
