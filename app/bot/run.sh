#!/bin/bash

pdm config venv.in_project False; pdm config check_update false; pdm i; TZ="Europe/Moscow" pdm start
# pdm config venv.in_project False; pdm i; pdm alembic-upgrade; sleep 10000
