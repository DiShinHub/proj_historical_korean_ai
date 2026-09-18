echo "Waiting for main app to start..."
sleep 5

poetry run python /apps/task_worker/main.py 