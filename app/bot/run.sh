#!/bin/bash

# Создание новой сессии tmux для бота
# tmux new-session -d -s bot_session 'pdm config venv.in_project False; pdm i; pdm alembic-upgrade; pdm apply-seeds; pdm start'
pdm config venv.in_project False; pdm config check_update false; pdm i; pdm alembic-upgrade; pdm apply-seeds; TZ="Europe/Moscow" pdm start
# pdm config venv.in_project False; pdm i; sleep 10000
# Ожидание, пока бот станет доступен
# sleep 5  # Настройте время ожидания, если нужно

# # Создание сессии для Celery Worker
# tmux new-session -d -s celery_worker_session 'pdm start_celery_worker; exec bash'

# # Создание сессии для Celery Beat
# tmux new-session -d -s celery_beat_session 'pdm start_celery_beat; exec bash'

# Подключение к сессии бота
# tmux attach-session -t bot_session
