"""Global test fixtures"""
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
import json

import aresponses
import pytest
import asyncio
import json

from ..const import TEST_HOST, TEST_PORT


@pytest.fixture()
def fail_to_authenticate_refresh_token(event_loop, auth_token, controller_json):
    client = aresponses.ResponsesMockServer(loop=event_loop)

    """Fail refresh token"""
    client.add(
        TEST_HOST, "/v1/authenticate", "POST", aresponses.Response(status=401, text="")
    )

    """Fail autentication twice"""
    client.add(
        TEST_HOST, "/v1/authenticate", "POST", aresponses.Response(status=401, text="")
    )

    yield client

    event_loop.run_until_complete(event_loop.shutdown_asyncgens())
    event_loop.close()


@pytest.fixture()
def login_fixture(event_loop, auth_token, controller_json):
    client = aresponses.ResponsesMockServer(loop=event_loop)

    client.add(
        TEST_HOST,
        "/v1/authenticate",
        "post",
        aresponses.Response(
            text=json.dumps(
                {
                    "data": {
                        "token": "login_token",
                        "refresh_token": "login_refresh_token",
                        "user_id": "login_userid",
                    }
                }
            ),
            status=200,
        ),
    )

    client.add(
        TEST_HOST,
        "/v1/controllers",
        "GET",
        aresponses.Response(status=200, text=json.dumps(controller_json)),
    )

    yield client

    event_loop.run_until_complete(event_loop.shutdown_asyncgens())
    event_loop.close()


@pytest.fixture()
def controller_login_fixture(event_loop, auth_token, controller_json):
    """Return an aresponses server for an authenticated remote client."""
    client = aresponses.ResponsesMockServer(loop=event_loop)

    client.add(
        TEST_HOST,
        "/v1/authenticate",
        "post",
        aresponses.Response(
            text=json.dumps(
                {
                    "data": {
                        "token": "login_token",
                        "refresh_token": "login_refresh_token",
                        "user_id": "login_userid",
                    }
                }
            ),
            status=200,
        ),
    )

    client.add(
        TEST_HOST,
        "/v1/controllers",
        "GET",
        aresponses.Response(status=200, text=json.dumps(controller_json)),
    )

    client.add(
        TEST_HOST,
        "/v1/controllers/1/history",
        "GET",
        aresponses.Response(
            status=200,
            text=json.dumps(
                {"data": [{"dummy": "history"}], "meta": {"page": 1, "count": 1}}
            ),
        ),
    )
    yield client

    event_loop.run_until_complete(event_loop.shutdown_asyncgens())
    event_loop.close()


@pytest.fixture()
def authenticated_refresh_token(
    event_loop, auth_token, controller_json, authenticate_token_expired_json
):
    def handler(request):
        if "Authorization" in request.headers and (
            request.headers["Authorization"] == "refreshed_token"
            or request.headers["Authorization"] == "login_token"
        ):
            return aresponses.Response(status=200, text=json.dumps(controller_json))

        return aresponses.Response(
            status=401, text=json.dumps(authenticate_token_expired_json)
        )

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

        # login
        return aresponses.Response(
            status=200,
            text=json.dumps(
                {
                    "data": {
                        "token": "login_token",
                        "refresh_token": "login_refresh_token",
                        "user_id": "login_userid",
                    }
                }
            ),
        )

    """Return an aresponses server for an authenticated remote client."""
    client = aresponses.ResponsesMockServer(loop=event_loop)

    client.add(TEST_HOST, "/v1/controllers", "GET", handler)

    client.add(TEST_HOST, "/v1/controllers", "GET", handler)

    client.add(TEST_HOST, "/v1/authenticate", "post", login_handler)

    yield client

    event_loop.run_until_complete(event_loop.shutdown_asyncgens())
    event_loop.close()


@pytest.fixture()
def controller_auth_failure_fixture(
    event_loop, auth_token, controller_json, authenticate_token_expired_json
):
    """Return an aresponses server for an authenticated remote client."""
    client = aresponses.ResponsesMockServer(loop=event_loop)

    client.add(
        TEST_HOST, "/v1/controllers", "GET", aresponses.Response(status=401, text="")
    )

    client.add(
        TEST_HOST,
        "/v1/authenticate",
        "post",
        aresponses.Response(
            status=200,
            text=json.dumps(
                {
                    "data": {
                        "token": "login_token",
                        "refresh_token": "login_refresh_token",
                        "user_id": "login_userid",
                    }
                }
            ),
        ),
    )

    client.add(
        TEST_HOST,
        "/v1/controllers",
        "GET",
        aresponses.Response(status=200, text=json.dumps(controller_json)),
    )

    yield client

    event_loop.run_until_complete(event_loop.shutdown_asyncgens())
    event_loop.close()


@pytest.fixture()
def login_fail_refresh_token(event_loop, auth_token, controller_json):
    """Return an aresponses server for an authenticated remote client."""
    client = aresponses.ResponsesMockServer(loop=event_loop)

    """Failed to refresh token"""
    client.add(
        TEST_HOST, "/v1/authenticate", "post", aresponses.Response(status=401, text="")
    )

    client.add(
        TEST_HOST,
        "/v1/authenticate",
        "post",
        aresponses.Response(
            status=200,
            text=json.dumps(
                {
                    "data": {
                        "token": "login_token",
                        "refresh_token": "login_refresh_token",
                        "user_id": "login_userid",
                    }
                }
            ),
        ),
    )

    yield client

    event_loop.run_until_complete(event_loop.shutdown_asyncgens())
    event_loop.close()


@pytest.fixture()
def moister_sensor_get_day_average(
    event_loop, auth_token, controller_json, controller_sensor_json
):
    """Return an aresponses server for an authenticated remote client."""
    client = aresponses.ResponsesMockServer(loop=event_loop)

    client.add(
        TEST_HOST,
        "/v1/authenticate",
        "post",
        aresponses.Response(
            text=json.dumps(
                {
                    "data": {
                        "token": "login_token",
                        "refresh_token": "login_refresh_token",
                        "user_id": "login_userid",
                    }
                }
            ),
            status=200,
        ),
    )

    client.add(
        TEST_HOST,
        "/v1/controllers",
        "GET",
        aresponses.Response(status=200, text=json.dumps(controller_json)),
    )

    client.add(
        TEST_HOST,
        "/v1/controllers/1/sensors/1",
        "GET",
        aresponses.Response(status=200, text=json.dumps(controller_sensor_json)),
    )

    client.add(
        TEST_HOST,
        "/v1/controllers/1/sensors/1/readings",
        "GET",
        aresponses.Response(
            status=200,
            text=json.dumps(
                {"data": [{"dummy": "no sensor"}], "meta": {"page": "1", "count": 1}}
            ),
        ),
    )

    client.add(
        TEST_HOST,
        "/v1/controllers/1/sensors/1/readings/averages/day",
        "GET",
        aresponses.Response(
            status=200,
            text=json.dumps(
                {"data": [{"dummy": "no sensor"}], "meta": {"page": "1", "count": 1}}
            ),
        ),
    )

    client.add(
        TEST_HOST,
        "/v1/controllers/1/sensors/1/readings/averages/hour",
        "GET",
        aresponses.Response(
            status=200,
            text=json.dumps(
                {"data": [{"dummy": "no sensor"}], "meta": {"page": "1", "count": 1}}
            ),
        ),
    )

    yield client

    event_loop.run_until_complete(event_loop.shutdown_asyncgens())
    event_loop.close()


@pytest.fixture()
def authenticate_token_expired_json():
    return {"errors": [{"detail": "Token has expired"}]}


@pytest.fixture()
def auth_token():
    return {
        "data": {
            "token": "test-token",
            "refresh_token": "refresh-token",
            "user_id": "test-user",
        }
    }


@pytest.fixture()
def controller_sensor_json():
    return {
        "data": {
            "battery": 90,
            "enabled": True,
            "id": "1",
            "last_reading_at": "2019-06-14T03:07:51.837Z",
            "mac": "20:10:00:00:00:00:00:47",
            "moisture_5": 30,
            "moisture_3": 20,
            "moisture_1": 10,
            "moistures_5": [
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                96,
                97,
                97,
                96,
                97,
                97,
                96,
                97,
                96,
                96,
                97,
                97,
                97,
                97,
                96,
                96,
            ],
            "moistures_3": [
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
                97,
            ],
            "moistures_1": [
                53,
                53,
                52,
                52,
                52,
                52,
                52,
                52,
                52,
                51,
                51,
                51,
                51,
                51,
                50,
                50,
                50,
                50,
                50,
                50,
                50,
                49,
                49,
                49,
                49,
                48,
                48,
                48,
                48,
                48,
                48,
                48,
                48,
                48,
                48,
                47,
                47,
                47,
                47,
                47,
                47,
                47,
                47,
                47,
                47,
                47,
                46,
                46,
            ],
            "name": "Test Sensor",
            "rssi": -79,
            "temp": 81.0,
            "temps": [
                68.0,
                68.0,
                68.0,
                68.0,
                68.0,
                68.0,
                68.0,
                70.0,
                72.0,
                73.0,
                75.0,
                77.0,
                79.0,
                81.0,
                82.0,
                82.0,
                84.0,
                84.0,
                86.0,
                86.0,
                86.0,
                86.0,
                88.0,
                88.0,
                88.0,
                90.0,
                90.0,
                90.0,
                90.0,
                90.0,
                91.0,
                90.0,
                91.0,
                91.0,
                91.0,
                91.0,
                90.0,
                90.0,
                90.0,
                88.0,
                88.0,
                86.0,
                86.0,
                84.0,
                84.0,
                84.0,
                82.0,
                81.0,
            ],
        }
    }


@pytest.fixture()
def controller_json():
    return {
        "data": [
            {
                "alert": "None",
                "connected": True,
                "conservation": {
                    "rain_chance": 70.0,
                    "rain_inches_24hr": 0.3,
                    "rain_inches_48hr": 0.6,
                    "rain_inches_4day": 1.5,
                    "rain_inches_7day": 2.0,
                    "seasonal_adjustments": [
                        20,
                        30,
                        40,
                        80,
                        100,
                        100,
                        100,
                        100,
                        100,
                        80,
                        40,
                        20,
                    ],
                    "temp_above": 35.0,
                },
                "created_at": "2018-09-29T23:34:52.153Z",
                "enabled": True,
                "id": "1",
                "last_checkin_at": "2019-06-14T03:13:28.811Z",
                "last_ran_at": "2019-06-13T08:40:01.000Z",
                "location": {
                    "city": "Palo Alto",
                    "country": "United States",
                    "latitude": 10.41754879871175,
                    "longitude": -100.12193391663871,
                    "postal_code": "94200",
                    "state": "California",
                    "street_1": "None",
                    "street_2": "None",
                    "timezone": "America/Los_Angeles",
                },
                "moisture_sensors": [
                    {
                        "battery": 100,
                        "enabled": True,
                        "id": "1",
                        "last_reading_at": "2019-06-14T03:07:51.837Z",
                        "mac": "20:10:00:00:00:00:00:47",
                        "moisture_b": 96,
                        "moisture_m": 97,
                        "moisture_t": 46,
                        "moistures_b": [
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            96,
                            97,
                            97,
                            96,
                            97,
                            97,
                            96,
                            97,
                            96,
                            96,
                            97,
                            97,
                            97,
                            97,
                            96,
                            96,
                        ],
                        "moistures_m": [
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                            97,
                        ],
                        "moistures_t": [
                            53,
                            53,
                            52,
                            52,
                            52,
                            52,
                            52,
                            52,
                            52,
                            51,
                            51,
                            51,
                            51,
                            51,
                            50,
                            50,
                            50,
                            50,
                            50,
                            50,
                            50,
                            49,
                            49,
                            49,
                            49,
                            48,
                            48,
                            48,
                            48,
                            48,
                            48,
                            48,
                            48,
                            48,
                            48,
                            47,
                            47,
                            47,
                            47,
                            47,
                            47,
                            47,
                            47,
                            47,
                            47,
                            47,
                            46,
                            46,
                        ],
                        "name": "Test Sensor",
                        "rssi": -79,
                        "temp": 81.0,
                        "temps": [
                            68.0,
                            68.0,
                            68.0,
                            68.0,
                            68.0,
                            68.0,
                            68.0,
                            70.0,
                            72.0,
                            73.0,
                            75.0,
                            77.0,
                            79.0,
                            81.0,
                            82.0,
                            82.0,
                            84.0,
                            84.0,
                            86.0,
                            86.0,
                            86.0,
                            86.0,
                            88.0,
                            88.0,
                            88.0,
                            90.0,
                            90.0,
                            90.0,
                            90.0,
                            90.0,
                            91.0,
                            90.0,
                            91.0,
                            91.0,
                            91.0,
                            91.0,
                            90.0,
                            90.0,
                            90.0,
                            88.0,
                            88.0,
                            86.0,
                            86.0,
                            84.0,
                            84.0,
                            84.0,
                            82.0,
                            81.0,
                        ],
                    }
                ],
                "name": "Test Site",
                "next_scheduled_at": "2019-06-14T08:00:52.000Z",
                "schedules": [
                    {
                        "created_at": "2018-09-29T23:51:11.500Z",
                        "days": ["S", "T", "Th", "Su"],
                        "enabled": True,
                        "frequency": "odd_days",
                        "id": "s_1",
                        "name": "2 days",
                        "next_run_at": "None",
                        "run_time": "None",
                        "scheduled_days": [],
                        "seasonally_adjust": False,
                        "start_time": "2018-09-30T14:00:15.000Z",
                        "type": "standard",
                        "updated_at": "2018-12-20T05:22:25.858Z",
                        "zones": [{"id": "z_1", "number": 1, "run_time": 4}],
                    }
                ],
                "updated_at": "2019-06-14T03:16:14.255Z",
                "weather": {
                    "accumulations": {
                        "total_2day": 0.0,
                        "total_4day": 0.0,
                        "total_7day": 0.0,
                        "total_today": 0.0,
                    },
                    "conditions": {
                        "pop": 0.0,
                        "raining": False,
                        "temp": 75.0,
                        "temp_high": 79.0,
                        "temp_low": 56.0,
                        "type": "clear_day",
                        "wind": 0.0,
                    },
                    "station": "None",
                },
                "zones": [
                    {
                        "enabled": True,
                        "exposure": "full_sun",
                        "head_dripline_ft": 0,
                        "head_num": 4,
                        "head_type": "spray",
                        "id": "z_1",
                        "moisture_sensor": {
                            "limit_moisture_b": 95,
                            "limit_moisture_m": 95,
                            "limit_moisture_t": 65,
                            "limit_temp": 35,
                            "moisture_sensor_id": "m_1",
                        },
                        "name": "Test Zone",
                        "number": 1,
                        "slope": "flat",
                        "soil_type": "None",
                        "type": "flowerbed",
                    }
                ],
            }
        ],
        "meta": {"count": 1, "page": 1},
    }
