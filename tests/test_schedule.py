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
async def test_schedule(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            controller = controllers[0]

            schedules = await controller.schedules()

            assert schedules.get("s_1").enabled


@pytest.mark.asyncio
async def test_schedule_run(event_loop, login_fixture):
    async with login_fixture:

        async def handler(request):
            # Request should contain a body with zone+time
            assert request.body_exists
            json = await request.json()
            assert json[0]["zone"] == 1
            assert json[0]["time"] == 4

            return aresponses.Response(status=200, text="")

        login_fixture.add(TEST_HOST, "/v1/controllers/1/run", "POST", handler)

        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            controller = controllers[0]

            schedules = await controller.schedules()

            assert schedules.get("s_1").enabled
            await schedules.get("s_1").run()


@pytest.mark.asyncio
async def test_schedule_run_season(event_loop, login_fixture):
    async with login_fixture:

        async def handler(request):
            # Request should contain a body with zone+time
            assert request.body_exists
            json = await request.json()
            assert json[0]["zone"] == 1
            return aresponses.Response(status=200, text="")

        login_fixture.add(TEST_HOST, "/v1/controllers/1/run", "POST", handler)

        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1
            controller = controllers[0]

            schedules = await controller.schedules()

            assert schedules.get("s_1").enabled
            await schedules.get("s_1").run(True)
