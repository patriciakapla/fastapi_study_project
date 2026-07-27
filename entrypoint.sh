#!/bin/sh

set -e

# executes db migrations
poetry run alembic upgrade head

# starts app
poetry run uvicorn --host 0.0.0.0 fastapi_study_project.app:app
