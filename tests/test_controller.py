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
from sprinkl_async.errors import AuthenticateError

from .const import TEST_HOST

from tests.fixtures import (
    login_fixture,
    controller_login_fixture,
    auth_token,
    controller_json,
    authenticate_token_expired_json,
)


@pytest.mark.asyncio
async def test_controller_properties(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            controller = controllers[0]

            assert controller.enabled
            assert controller.connected


@pytest.mark.asyncio
async def test_controller_weather(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            controller = controllers[0]

            weather = await controller.weather()
            assert weather.station == "None"
            assert "accumulations" in weather
            assert "conditions" in weather


@pytest.mark.asyncio
async def test_controller_location(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            controller = controllers[0]

            location = await controller.location()
            assert location.city == "Palo Alto"


@pytest.mark.asyncio
async def test_controller_conservation(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            controller = controllers[0]

            conservation = await controller.conservation()
            assert conservation.rain_chance == 70.0
            assert "seasonal_adjustments" in conservation


@pytest.mark.asyncio
async def test_controller_history(event_loop, controller_login_fixture):
    async with controller_login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            controller = controllers[0]

            history = await controller.history()
            assert len(history.data) == 1

            assert history.data[0]["dummy"] == "history"


@pytest.mark.asyncio
async def test_controller_stop(event_loop, controller_login_fixture):
    controller_login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/stop",
        "POST",
        aresponses.Response(status=200, text=""),
    )

    async with controller_login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            controller = controllers[0]
            assert controller.id == "1"

            await controller.stop()


@pytest.mark.asyncio
async def test_controller_reauth(
    event_loop, controller_login_fixture, authenticate_token_expired_json
):
    def login_handler(request):
        # token refresh
        if "refresh_token" in request.query:
            return aresponses.Response(
                status=200,
                text=json.dumps(
                    {
                        "data": {
                            "token": "refreshed_token",  # used in controllers_handler to signal authenticated user
                            "refresh_token": "refreshed_refresh_token",
                            "user_id": "refreshed_userid",
                        }
                    }
                ),
            )

    # Should be called after invalid token from stop
    controller_login_fixture.add(TEST_HOST, "/v1/authenticate", "post", login_handler)

    # Fail first call to stop with invalid token
    controller_login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/stop",
        "POST",
        aresponses.Response(
            status=401, text=json.dumps(authenticate_token_expired_json)
        ),
    )

    # Retry call with call stop agian (with success)
    controller_login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/stop",
        "POST",
        aresponses.Response(status=200, text=""),
    )

    async with controller_login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            controller = controllers[0]
            assert controller.id == "1"

            await controller.stop()

            assert client.auth_info.token == "refreshed_token"
