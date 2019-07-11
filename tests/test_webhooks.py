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
import re

from sprinkl_async.client import Client
from sprinkl_async.authtoken import AuthToken
from sprinkl_async.errors import AuthenticateError, InvalidWebhookEvent

from .const import TEST_HOST

from tests.fixtures import (
    login_fixture,
    auth_token,
    controller_json,
    webhook_list_json,
    webhooks_events_json,
    webhook_get_id1_json,
)


async def get_controller(websession):
    client = Client(websession)
    result = await client.login(email="test@test.com", password="password")

    assert result.user_id == "login_userid"
    controllers = await client.controllers()
    assert len(controllers) == 1

    return controllers[0]


@pytest.mark.asyncio
async def test_webhooks_all(event_loop, login_fixture, webhook_list_json):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/webhooks",
        "GET",
        aresponses.Response(status=200, text=json.dumps(webhook_list_json)),
    )

    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            controller = await get_controller(websession)
            all_hooks = await controller.webhooks.all()
            assert len(all_hooks) == 3
            assert all_hooks[0].external_id == "ext_id1"


@pytest.mark.asyncio
async def test_webhooks_find(event_loop, login_fixture, webhook_list_json):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/webhooks",
        "GET",
        aresponses.Response(status=200, text=json.dumps(webhook_list_json)),
    )

    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            controller = await get_controller(websession)
            all_hooks = await controller.webhooks.find("ext_id1")
            assert len(all_hooks) == 1
            assert all_hooks[0].external_id == "ext_id1"


@pytest.mark.asyncio
async def test_webhooks_get(event_loop, login_fixture, webhook_get_id1_json):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/webhooks/id1",
        "GET",
        aresponses.Response(status=200, text=json.dumps(webhook_get_id1_json)),
    )

    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            controller = await get_controller(websession)
            hook = await controller.webhooks.get("id1")
            assert hook.external_id == "ext_id1"


@pytest.mark.asyncio
async def test_webhooks_get_and_delete(event_loop, login_fixture, webhook_get_id1_json):

    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/webhooks/id_1",
        "GET",
        aresponses.Response(status=200, text=json.dumps(webhook_get_id1_json)),
    )

    login_fixture.add(
        TEST_HOST,
        re.compile("/v1/controllers/1/webhooks/id_1"),
        "DELETE",
        aresponses.Response(status=200, text=""),
    )

    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            controller = await get_controller(websession)

            hook = await controller.webhooks.get("id_1")
            assert hook.external_id == "ext_id1"

            await hook.delete()


@pytest.mark.asyncio
async def test_webhooks_events(event_loop, login_fixture, webhooks_events_json):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/webhooks/events",
        "GET",
        aresponses.Response(status=200, text=json.dumps(webhooks_events_json)),
    )

    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            controller = await get_controller(websession)

            all_events = await controller.webhooks.events()
            assert len(all_events) == 11

            # test caching
            all_events = await controller.webhooks.events()
            assert len(all_events) == 11


@pytest.mark.asyncio
async def test_webhooks_delete(event_loop, login_fixture):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/webhooks/id_1",
        "DELETE",
        aresponses.Response(status=200, text=""),
    )

    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            controller = await get_controller(websession)

            await controller.webhooks.delete("id_1")


@pytest.mark.asyncio
async def test_webhooks_create(
    event_loop, login_fixture, webhooks_events_json, webhook_get_id1_json
):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/webhooks",
        "POST",
        aresponses.Response(status=200, text=json.dumps(webhook_get_id1_json)),
    )

    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/webhooks/events",
        "GET",
        aresponses.Response(status=200, text=json.dumps(webhooks_events_json)),
    )

    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            controller = await get_controller(websession)

            webhook = await controller.webhooks.create(
                "ext_id1", "http://id", webhooks_events_json["data"]
            )


@pytest.mark.asyncio
async def test_webhooks_invalid_create(
    event_loop, login_fixture, webhooks_events_json, webhook_get_id1_json
):
    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/webhooks",
        "POST",
        aresponses.Response(status=200, text=json.dumps(webhook_get_id1_json)),
    )

    login_fixture.add(
        TEST_HOST,
        "/v1/controllers/1/webhooks/events",
        "GET",
        aresponses.Response(status=200, text=json.dumps(webhooks_events_json)),
    )

    async with login_fixture:
        async with aiohttp.ClientSession(loop=event_loop) as websession:
            controller = await get_controller(websession)

            with pytest.raises(InvalidWebhookEvent):
                webhook = await controller.webhooks.create(
                    "ext_id1", "http://id", ["apa"]
                )
