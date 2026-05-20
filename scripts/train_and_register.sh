#!/bin/bash
set -e
cd "$(dirname "$0")/.."
python ml/train.py "$@"
echo "Model artifacts ready in ml/artifacts/"
