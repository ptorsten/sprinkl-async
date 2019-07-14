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

from sprinkl_async.webhook_objects import WebhookBaseObject


def test_wh_obj_creation():
    data = {
        "device_id": "d_id",
        "webhook_id": "w_id",
        "external_id": "e_id",
        "event": "test",
        "event_data": {"data_test": "test"},
    }
    test = WebhookBaseObject(data)

    assert test.device_id == "d_id"
    assert test.webhook_id == "w_id"
    assert test.external_id == "e_id"
    assert test.event == "test"
    assert test.data.data_test == "test"
