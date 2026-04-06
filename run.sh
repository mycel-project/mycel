#!/bin/bash

cd "$(dirname "$0")"
./env/bin/python3 -m src.main "$@"
