#! /usr/bin/env bash

set -eu -o pipefail

find . -type f | grep '_test\.py' | xargs -I {} python3 {}
