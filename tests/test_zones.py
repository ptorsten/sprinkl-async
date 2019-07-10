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

from tests.fixtures import login_fixture, auth_token, controller_json


@pytest.mark.asyncio
async def test_zones_get(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            zones = await controllers[0].zones()
            assert len(zones) == 1

            assert "z_1" in zones

            with pytest.raises(KeyError):
                assert zones["apa"].id == "apa"

            assert zones.get("z_1") == zones["z_1"]

            for zone in zones:
                assert zone == "z_1"

            assert zones.get_by_number(1) == zones["z_1"]
            with pytest.raises(KeyError):
                zones.get_by_number(3)


@pytest.mark.asyncio
async def test_zones_run(event_loop, login_fixture):
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

            assert "z_1" in zones
            await zones.run([{"z_1": 10}])


@pytest.mark.asyncio
async def test_zones_run_invalid_list(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            zones = await controllers[0].zones()
            assert len(zones) == 1

            assert "z_1" in zones
            with pytest.raises(Exception):
                await zones.run({"z_1": 10})

            with pytest.raises(Exception):
                await zones.run([{"z_1": 10, "z_2": 10}])


@pytest.mark.asyncio
async def test_zones_skip(event_loop, login_fixture):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/skip",
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

            assert "z_1" in zones

            await zones.skip()
