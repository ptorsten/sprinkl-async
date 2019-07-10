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
import json
from datetime import datetime, timedelta

import aiohttp
import asynctest
import pytest
import aresponses

from sprinkl_async.client import Client
from sprinkl_async.authtoken import AuthToken
from sprinkl_async.errors import AuthenticateError, RequestTimeout, RequestError

from tests.const import TEST_HOST, TEST_PORT, TEST_EMAIL, TEST_PASSWORD

from tests.fixtures import (
    auth_token,
    authenticated_refresh_token,
    fail_to_authenticate_refresh_token,
    controller_json,
    login_fixture,
    login_fail_refresh_token,
    authenticate_token_expired_json,
    controller_auth_failure_fixture,
)


@pytest.mark.asyncio
async def test_login_failed_refresh_auth(
    event_loop, fail_to_authenticate_refresh_token
):
    auth_info = AuthToken(
        token="token",
        refresh_token="refresh_token",
        refresh_ts=datetime.now() - timedelta(hours=int(10)),
        user_id="user",
    )

    async with fail_to_authenticate_refresh_token:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            with pytest.raises(AuthenticateError):
                result = await client.login(
                    email=TEST_EMAIL, password=TEST_PASSWORD, auth_info=auth_info
                )


@pytest.mark.asyncio
async def test_controller_auth_failure(event_loop, controller_auth_failure_fixture):
    auth_info = AuthToken(
        token="token",
        # refreshed_token = valid
        refresh_token="refreshed_token",
        refresh_ts=datetime.now() + timedelta(hours=int(10)),
        user_id="user",
    )

    assert auth_info.is_valid

    async with controller_auth_failure_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(
                email="test@test.com", password="password", auth_info=auth_info
            )

            assert result.user_id == "login_userid"


@pytest.mark.asyncio
async def test_login_refresh_auth(event_loop, authenticated_refresh_token):
    auth_info = AuthToken(
        token="token",
        # refreshed_token = valid
        refresh_token="refreshed_token",
        refresh_ts=datetime.now() + timedelta(hours=int(10)),
        user_id="user",
    )

    assert auth_info.is_valid

    async with authenticated_refresh_token:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(
                email="test@test.com", password="password", auth_info=auth_info
            )

            assert result.user_id == "refreshed_userid"
            assert result.refresh_token == "refreshed_refresh_token"
            assert result.token == "refreshed_token"

            assert client.auth_info == result


@pytest.mark.asyncio
async def test_login_refresh_invalid_refresh_token(
    event_loop, authenticated_refresh_token
):
    auth_info = AuthToken(
        token="token",
        refresh_token="",
        refresh_ts=datetime.now() + timedelta(hours=int(10)),
        user_id="user",
    )

    async with authenticated_refresh_token:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(
                email="test@test.com", password="password", auth_info=auth_info
            )

            assert result.user_id == "login_userid"


@pytest.mark.asyncio
async def test_login_not_valid_token(event_loop, authenticated_refresh_token):
    auth_info = AuthToken(
        token="token",
        refresh_token="refresh_token",
        # make sure token isn't valid
        refresh_ts=datetime.now() - timedelta(hours=int(10)),
        user_id="user",
    )

    assert auth_info.is_valid == False

    async with authenticated_refresh_token:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(
                email="test@test.com", password="password", auth_info=auth_info
            )

            assert result.user_id == "refreshed_userid"
            assert result.refresh_token == "refreshed_refresh_token"
            assert result.token == "refreshed_token"


@pytest.mark.asyncio
async def test_login_not_valid_token_refreshtoken(
    event_loop, authenticated_refresh_token
):
    auth_info = AuthToken(
        token="token",
        refresh_token="",
        # make sure token isn't valid
        refresh_ts=datetime.now() - timedelta(hours=int(10)),
        user_id="user",
    )

    assert auth_info.is_valid == False

    async with authenticated_refresh_token:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(
                email="test@test.com", password="password", auth_info=auth_info
            )

            assert result.user_id == "login_userid"


@pytest.mark.asyncio
async def test_login(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"
            assert result.refresh_token == "login_refresh_token"
            assert result.token == "login_token"


@pytest.mark.asyncio
async def test_login_no_email(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            with pytest.raises(AuthenticateError):
                result = await client.login(email=None, password="password")


@pytest.mark.asyncio
async def test_login_no_password(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            with pytest.raises(AuthenticateError):
                result = await client.login(email="test@test.com", password=None)


@pytest.mark.asyncio
async def test_login_timeout(event_loop, login_fixture):
    async def long_running_login(*args, **kwargs):
        await asyncio.sleep(1)

    with asynctest.mock.patch.object(
        aiohttp.ClientResponse, "json", long_running_login
    ):
        async with login_fixture:
            async with aiohttp.ClientSession(loop=event_loop) as websession:
                with pytest.raises(RequestTimeout):
                    client = Client(websession, timeout=0.1)
                    result = await client.login(
                        email="test@test.com", password="password"
                    )


@pytest.mark.asyncio
async def test_request_timeout(event_loop, login_fixture):
    client = aresponses.ResponsesMockServer(loop=event_loop)

    client.add(
        TEST_HOST,
        "/v1/authenticate",
        "post",
        aresponses.Response(text="error", status=500),
    )

    async with client:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            with pytest.raises(RequestError):
                client = Client(websession, timeout=0.1)
                result = await client.login(email="test@test.com", password="password")


@pytest.mark.asyncio
async def test_login_fail_refreshtoken(
    event_loop, login_fail_refresh_token, controller_json
):
    auth_info = AuthToken(
        token="token",
        refresh_token="refresh_token",
        refresh_ts=datetime.now() - timedelta(hours=int(10)),
        user_id="user",
    )

    login_fail_refresh_token.add(
        TEST_HOST,
        "/v1/controllers",
        "GET",
        aresponses.Response(status=200, text=json.dumps(controller_json)),
    )

    async with login_fail_refresh_token:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(
                email="test@test.com", password="password", auth_info=auth_info
            )

            assert result.user_id == "login_userid"
            assert result.refresh_token == "login_refresh_token"
            assert result.token == "login_token"


@pytest.mark.asyncio
async def test_login_fail_refreshtoken_and_controller(
    event_loop, login_fail_refresh_token
):
    auth_info = AuthToken(
        token="token",
        refresh_token="refresh_token",
        refresh_ts=datetime.now() + timedelta(hours=int(10)),
        user_id="user",
    )

    login_fail_refresh_token.add(
        TEST_HOST, "/v1/controllers", "GET", aresponses.Response(status=401, text="")
    )

    async with login_fail_refresh_token:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)

            with pytest.raises(AuthenticateError):
                result = await client.login(
                    email="test@test.com", password="password", auth_info=auth_info
                )

                assert result.user_id == "login_userid"


@pytest.mark.asyncio
async def test_get_controller_authinfo(event_loop, login_fixture):
    auth_info = AuthToken(
        token="token",
        refresh_token="refresh_token",
        refresh_ts=datetime.now() + timedelta(hours=int(10)),
        user_id="user",
    )

    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(auth_info=auth_info)

            assert result.user_id == "user"

            controllers = await client.controllers()
            assert len(controllers) == 1
            assert controllers[0].id == "1"
            assert controllers[0].name == "Test Site"


@pytest.mark.asyncio
async def test_get_controller(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            assert controllers[0].id == "1"
            assert controllers[0].name == "Test Site"

            assert await client.get("1") == controllers[0]

            with pytest.raises(AttributeError):
                assert controllers[0].apa == "apa"


@pytest.mark.asyncio
async def test_get_zones(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            zones = await controllers[0].zones()
            assert len(zones) == 1

            assert zones["z_1"].enabled
            assert zones["z_1"].name == "Test Zone"

            with pytest.raises(KeyError):
                assert zones["apa"].id == "apa"

            with pytest.raises(AttributeError):
                assert zones["z_1"].apa == "apa"
