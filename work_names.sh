#!/bin/bash
cd ~/PycharmProjects/MusicUtils || exit
source .venv/bin/activate
while true; do
  ollama serve
  python3 ollama_rename_plan_integration.py rename_plan.sqlite ai_gen.json
  result=$?
  if [ $result -eq 0 ]; then
    echo "Script successfully ended"
    break
  elif [ $result -eq 75 ]; then
    echo "Script failed due to timeout or interrupt, Retrying in 10 seconds..."
    ollama stop
    sleep 10
  else
    echo "Script failed"
    exit $result
  fi
done