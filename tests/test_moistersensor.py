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
    moister_sensor_get_day_average,
    auth_token,
    controller_json,
    controller_sensor_json,
)


@pytest.mark.asyncio
async def test_get_moistersensors(event_loop, moister_sensor_get_day_average):
    async with moister_sensor_get_day_average:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            controller = controllers[0]

            sensors = await controller.moisture_sensors()
            assert len(sensors) == 1

            sensor = sensors["1"]

            with pytest.raises(AttributeError):
                assert sensor.apa == "apa"


@pytest.mark.asyncio
async def test_get_readings(event_loop, moister_sensor_get_day_average):
    async with moister_sensor_get_day_average:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            controller = controllers[0]

            sensors = await controller.moisture_sensors()
            assert len(sensors) == 1

            sensor = sensors["1"]

            readings = await sensor.readings()
            assert len(readings.data) == 1
            assert readings.data[0]["dummy"] == "no sensor"


@pytest.mark.asyncio
async def test_get_averages(event_loop, moister_sensor_get_day_average):
    async with moister_sensor_get_day_average:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            controller = controllers[0]

            sensors = await controller.moisture_sensors()
            assert len(sensors) == 1

            sensor = sensors["1"]

            readings = await sensor.averages_day()
            assert len(readings.data) == 1
            assert readings.data[0]["dummy"] == "no sensor"

            readings = await sensor.averages_hour()
            assert len(readings.data) == 1
            assert readings.data[0]["dummy"] == "no sensor"


@pytest.mark.asyncio
async def test_get_refresh(event_loop, moister_sensor_get_day_average):
    async with moister_sensor_get_day_average:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            client = Client(websession)
            result = await client.login(email="test@test.com", password="password")

            assert result.user_id == "login_userid"

            controllers = await client.controllers()
            assert len(controllers) == 1

            controller = controllers[0]

            sensors = await controller.moisture_sensors()
            assert len(sensors) == 1

            sensor = sensors["1"]

            await sensor.refresh()
            assert sensor.battery == 90
