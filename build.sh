#!/bin/sh

cd $(dirname -- "$0")

exec ${PYTHON:-python3} -m mkwhl --src-include 'mkwhl/**/*' "$@"
