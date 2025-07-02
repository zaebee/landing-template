#!/bin/sh
npx prettier --write "**/*.{json,css,html}"
npx clang-format -i proto/*.proto
