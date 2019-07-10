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

import datetime

from sprinkl_async.authtoken import AuthToken


def test_token():
    auth_info = AuthToken(
        token="token",
        refresh_token="refresh_token",
        refresh_ts=datetime.datetime.now() - datetime.timedelta(hours=int(1)),
        user_id="user",
    )

    repr_str = repr(auth_info)
    repr_obj = eval(repr_str)

    assert repr_obj.token == auth_info.token
    assert repr_obj.refresh_token == auth_info.refresh_token
    assert repr_obj.refresh_timestamp == auth_info.refresh_timestamp
    assert repr_obj.user_id == auth_info.user_id


def test_no_refresh():
    auth_info = AuthToken(
        token="token",
        refresh_token=None,
        refresh_ts=datetime.datetime.now() - datetime.timedelta(hours=int(1)),
        user_id="user",
    )

    repr_str = repr(auth_info)
    repr_obj = eval(repr_str)

    assert repr_obj.token == auth_info.token
    assert repr_obj.refresh_token == auth_info.refresh_token
    assert repr_obj.refresh_timestamp == auth_info.refresh_timestamp
    assert repr_obj.user_id == auth_info.user_id


def test_only_refresh():
    auth_info = AuthToken(refresh_token="refresh_token")

    assert not auth_info.is_valid
    assert auth_info.refresh_token == "refresh_token"
