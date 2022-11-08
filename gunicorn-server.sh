#!/bin/bash

python api/main.py --experiment_name ""  --bind 0.0.0.0 --gunicorn_port 8000 --mlflow_port 5000 --verbose "info" --workers 1
