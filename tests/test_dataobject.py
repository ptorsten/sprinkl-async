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

from sprinkl_async.dataobject import DictObject, ListObject


def test_create_lists():
    dl = ListObject([["subitem1", "subitem2"]])

    assert len(dl) == 1

    for sublist in dl:
        assert len(sublist) == 2

    assert len(dl[0]) == 2
    assert dl[0][0] == "subitem1"
    assert dl[0][1] == "subitem2"

    assert dl.get(0) == dl[0]

    with pytest.raises(IndexError):
        item = dl.get(1)

    with pytest.raises(KeyError):
        item = dl[1]

    assert len(dl.data) == 1


def test_create_dict():
    do = DictObject({"item": "subitem1"})

    assert len(do) == 1

    for item in do:
        assert item == "item"

    assert do.get("item") == do["item"]

    item = do.get("1")
    assert item == None

    with pytest.raises(KeyError):
        item = do["1"]

    assert len(do.data) == 1
