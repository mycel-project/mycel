# Mycel

[![Build Status](https://img.shields.io/github/actions/workflow/status/mycel-project/mycel/ci.yml?branch=main)](https://github.com/mycel-project/mycel/actions)
[![Release](https://img.shields.io/github/v/release/mycel-project/mycel)](https://github.com/mycel-project/mycel/releases)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Active Dev](https://img.shields.io/github/last-commit/mycel-project/mycel/dev?label=dev%20activity)](https://github.com/mycel-project/mycel/tree/dev)

Mycel is an open-source long-term learning framework built around a standardized API, designed to be embedded into apps, plugins, and any existing tool.

For more information, visit [Mycel Project's website](https://mycel-project.com).

## Quick start

- Ensure **Python v3.10+** and **git** are installed
- Clone this repo: `git clone https://github.com/mycel-project/mycel`
- Setup: `mycel.bat setup` (Windows) or `./mycel.sh setup` (Linux/macOS)
- Run: `mycel.bat run` (Windows) or `./mycel.sh run` (Linux/macOS)
- Update: `mycel.bat update` (Windows) or `./mycel.sh update` (Linux/macOS)

For the full setup guide, see [mycel-project.com/mycel#self-hosting](https://mycel-project.com/mycel/index.html#self-hosting).

## Contributing / Development

See the [contribution guide](https://mycel-project.com/docs/mycel/manual/contribution-guide/).

After running `./mycel.sh setup`, install the additional dev dependencies
(needed to run the test suite) with:
```bash
./env/bin/pip install -r requirements-dev.txt
```

Then run the tests with:

```bash
./env/bin/pytest tests/
```
