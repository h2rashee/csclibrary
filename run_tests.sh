#!/usr/bin/env bash

librarian_dir="$(realpath "$(dirname "$0")")"
librarian_tests_dir="${librarian_dir}/librarian_tests"

export PYTHONPATH="${librarian_dir}"
cd "${librarian_tests_dir}"

python3 -m unittest "$@" test_*.py
