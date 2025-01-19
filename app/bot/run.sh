#!/bin/bash

pdm config venv.in_project False; pdm config check_update false; pdm i; pdm alembic-upgrade; pdm apply-seeds; TZ="Europe/Moscow" pdm start
# pdm config venv.in_project False; pdm i; sleep 10000
