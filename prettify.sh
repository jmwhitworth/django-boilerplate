#!/bin/bash

npm run prettier
uv run djhtml ./**/*.html
npx rustywind --write .