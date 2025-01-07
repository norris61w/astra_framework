#!/usr/bin/env bash

set -e


VENV_DIR=".venv"
COMMON_REQUIREMENTS="../astracommon/requirements.txt"
COMMON_DEV_REQUIREMENTS="../astracommon/requirements-dev.txt"
PROJECT_REQUIREMENTS="requirements.txt"
PROJECT_DEV_REQUIREMENTS="requirements-dev.txt"
PYTHONPATH_VAR="../astracommon/src/"
PYLINT_TARGET="src/astragateway"
PYLINT_RC="../astracommon/pylintrc"


mkdir -p "$VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"


echo "Installing dependencies..."
pip install -r "$COMMON_REQUIREMENTS"
pip install -r "$COMMON_DEV_REQUIREMENTS"
pip install -r "$PROJECT_REQUIREMENTS"
pip install -r "$PROJECT_DEV_REQUIREMENTS"


echo "********** PYLINT ***********"
PYTHONPATH="$PYTHONPATH_VAR" pylint "$PYLINT_TARGET" \
    --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}" \
    --rcfile="$PYLINT_RC"


deactivate
