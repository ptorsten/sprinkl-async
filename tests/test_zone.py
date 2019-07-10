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
from sprinkl_async.errors import (
    AuthenticateError,
    RequestError,
    ControllerAlreadyRunning,
)

from .const import TEST_HOST

from tests.fixtures import login_fixture, auth_token, controller_json


@pytest.mark.asyncio
async def test_zone_properties(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            zones = await controllers[0].zones()
            assert len(zones) == 1

            zone = zones["z_1"]

            assert zone.enabled
            assert zone.name == "Test Zone"
            assert zone.number == 1

            with pytest.raises(AttributeError):
                assert zone.apa == "apa"


@pytest.mark.asyncio
async def test_zone_run(event_loop, login_fixture):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/run",
        "POST",
        aresponses.Response(status=200, text=""),
    )
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            zones = await controllers[0].zones()
            assert len(zones) == 1

            zone = zones["z_1"]

            await zone.run(10)


@pytest.mark.asyncio
async def test_zone_run_error(event_loop, login_fixture):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/run",
        "POST",
        aresponses.Response(status=400, text="Bad Request"),
    )
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            zones = await controllers[0].zones()
            assert len(zones) == 1

            zone = zones["z_1"]

            with pytest.raises(RequestError):
                await zone.run(0)


@pytest.mark.asyncio
async def test_zone_run_already_running(event_loop, login_fixture):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/run",
        "POST",
        aresponses.Response(
            status=403,
            text=json.dumps({"errors": [{"detail": "Controller is already running"}]}),
        ),
    )
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            zones = await controllers[0].zones()
            assert len(zones) == 1

            zone = zones["z_1"]

            with pytest.raises(ControllerAlreadyRunning):
                await zone.run(1)


@pytest.mark.asyncio
async def test_zone_run_invalid_json_error(event_loop, login_fixture):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/run",
        "POST",
        aresponses.Response(status=403, text="Error"),
    )
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            zones = await controllers[0].zones()
            assert len(zones) == 1

            zone = zones["z_1"]

            with pytest.raises(RequestError):
                await zone.run(1)
