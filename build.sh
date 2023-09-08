#!/bin/sh

set -e

cd $(dirname -- "$0")

rm -rf build
exec ${PYTHON:-python3} -m mkwhl "$@"
