# sprinkl-async: A Simple Python Library for Sprinkl™ Controllers

[![Travis CI](https://travis-ci.org/ptorsten/sprinkl-async.svg?branch=master)](https://travis-ci.org/ptorsten/sprinkl-async)
[![PyPi](https://img.shields.io/pypi/v/sprinkl_async.svg)](https://pypi.python.org/pypi/sprinkl_async)
[![Version](https://img.shields.io/pypi/pyversions/sprinkl_async.svg)](https://pypi.python.org/pypi/sprinkl_async)
[![License](https://img.shields.io/pypi/l/sprinkl_async.svg)](https://github.com/ptorsten/sprinkl-async/blob/master/LICENSE)
[![Code Coverage](https://codecov.io/gh/ptorsten/sprinkl-async/branch/master/graph/badge.svg)](https://codecov.io/gh/ptorsten/sprinkl-async)
[![Maintainability](https://api.codeclimate.com/v1/badges/29ad8b03a39f66e78833/maintainability)](https://codeclimate.com/github/ptorsten/sprinkl-async/maintainability)

`sprinkl-async` is a  Python library for interacting with [Sprinkl™ Control SR-400](https://sprinkl.com/control/)

## Python Versions

The python test suite requires Python 3.6 or higher; tests
run on Python 3.5 will fail.

`sprinkl-async` is currently supported on:

* Python 3.5
* Python 3.6
* Python 3.7

## Installation

```python
pip install sprinkl_async
```

## Examples

### Get controller and zones

```python
import asyncio
from aiohttp import ClientSession
from sprinkl_async import Client

async def main() -> None:
    """Create client and login"""
    async with ClientSession() as session:
        # Create sprinkl-async client
        client = Client(session)
        
        # login
        auth = await client.login(email="email", password="secret")

asyncio.get_event_loop().run_until_complete(main())

```

## Developing

1. Install developer environment: `make init`
2. Use virtual environment for development: `pipenv shell`
3. Write code/tests and be happy
4. Update `README.MD` with examples

## Testing

1. Write new tests for the functionality added
2. Run tests and ensure 100% coverage: `make coverage`
3. Ensure no lint errors: `make lint`
4. Ensure no typing errors: `make type`

## Contributing

Follow the developing/testing flows and follow [CONTRIBUTING.MD](CONTRIBUTING) for details.

## License

Apache 2.0; see [LICENSE](LICENSE) for details.

## Inspiration

The API for Sprinkl-async follow the same design principals as [Regenmaschine](https://github.com/bachya/regenmaschine)
[![Say Thanks](https://img.shields.io/badge/SayThanks-!-1EAEDB.svg)](https://saythanks.io/to/bachya)


## Disclaimer

This project is not an official Google project. It is not supported by Google
and Google specifically disclaims all warranties as to its quality,
merchantability, or fitness for a particular purpose.