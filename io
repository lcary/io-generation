#!/bin/bash
set -e
# Ensure tests are run from project root
cd "$( dirname "${BASH_SOURCE[0]}" )"
python -m iogen.iogen "$@"
