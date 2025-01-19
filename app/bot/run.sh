#!/bin/bash

pdm config venv.in_project False; pdm config check_update false; pdm i; pdm alembic-upgrade; TZ="Europe/Moscow" pdm start
# pdm config venv.in_project False; pdm i; sleep 10000
