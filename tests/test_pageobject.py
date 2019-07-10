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

from sprinkl_async.pageobject import PageObject


def test_page_properties():
    def request(method, uri, params):
        request_called = True

    data = {
        "data": [{"object1": "1"}, {"object2": "2"}],
        "meta": {"count": "31411", "page": "1"},
    }

    page_obj = PageObject(data, request, "get", "uri")

    assert page_obj.data[0]["object1"] == "1"
    assert page_obj.data[1]["object2"] == "2"

    assert page_obj.meta.count == "31411"
    assert page_obj.meta.page == "1"

    assert page_obj.has_more

    assert json.loads(page_obj.json)[0]["object1"] == "1"


@pytest.mark.asyncio
async def test_page_next():
    request_called = False

    async def request(method, uri, params):
        page2 = {
            "data": [{"object3": "1"}, {"object4": "2"}],
            "meta": {"count": "31411", "page": "2"},
        }
        request_called = True
        assert params["page"] == 2
        assert uri == "uri"
        return page2

    page1 = {
        "data": [{"object1": "1"}, {"object2": "2"}],
        "meta": {"count": "31411", "page": "1"},
    }

    page_obj = PageObject(page1, request, "get", "uri")
    next_obj = await page_obj.next()

    assert next_obj.data[0]["object3"] == "1"
    assert next_obj.data[1]["object4"] == "2"

    assert next_obj.meta.count == "31411"
    assert next_obj.meta.page == "2"

    assert next_obj.has_more


@pytest.mark.asyncio
async def test_page_single():
    async def request(method, uri, params):
        request_called = True

    page1 = {
        "data": [{"object1": "1"}, {"object2": "2"}],
        "meta": {"count": "1", "page": "1"},
    }

    page_obj = PageObject(page1, request, "get", "uri")
    assert not page_obj.has_more
    assert not await page_obj.next()
