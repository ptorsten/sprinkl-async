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

from tests.const import TEST_HOST, TEST_PORT

from tests.fixtures import (
    login_fixture,
    auth_token,
    controller_json,
    controller_sensor_json,
)


@pytest.mark.asyncio
async def test_get_moistersensors_invalid(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            controller = controllers[0]

            sensors = await controller.moisture_sensors()
            assert len(sensors) == 1

            sensor = sensors.get("0")
            assert sensor == None

            with pytest.raises(KeyError):
                assert sensors["apa"].id == "apa"


@pytest.mark.asyncio
async def test_get_moistersensors(event_loop, login_fixture):
    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            controller = controllers[0]

            sensors = await controller.moisture_sensors()
            assert len(sensors) == 1

            sensor = sensors.get("1")
            assert sensor == sensors["1"]

            assert len(sensors.all()) == 1

            for iter_sensor in sensors:
                assert iter_sensor == sensor.id
