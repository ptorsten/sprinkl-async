# Copyright 2019 Google Inc.
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

init:
	pip3 install --upgrade pip pipenv
	pipenv lock
	pipenv install --three --dev
	pipenv run pre-commit install

lint:
	pipenv run pylint sprinkl_async
	pipenv run flake8 sprinkl_async
	pipenv run pydocstyle sprinkl_async

clean:
	pipenv --rm

coverage:
	pipenv run py.test -s --verbose --cov-report term-missing --cov-report xml --cov-report annotate --cov=sprinkl_async tests

publish:
	pipenv run python setup.py sdist bdist_wheel
	pipenv run twine upload dist/*
	rm -rf dist/ build/ .egg sprinkl_async.egg-info/

test:
	pipenv run py.test --verbose

type:
	pipenv run mypy sprinkl_async
